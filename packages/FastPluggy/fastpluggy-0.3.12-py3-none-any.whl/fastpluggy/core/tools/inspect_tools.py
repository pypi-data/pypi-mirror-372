import asyncio
import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Annotated, get_origin, get_args, ForwardRef

# Use tomllib (standard library in Python 3.11+) if available, otherwise use tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from loguru import logger

from fastpluggy.core.tools import convert_param_type
from fastpluggy.core.tools.fs_tools import create_init_file


# Marker class or metadata to denote internal-use parameters
class InjectDependency:
    pass


def process_function_parameters(func_signature: inspect.Signature, param_values: dict[str, Any]) -> dict[str, Any]:
    """
    Processes the parameters of a function using type hints and provided values.

    :param func_signature: Function signature to inspect.
    :param param_values: A dictionary of parameter values to be converted.
    :return: A dictionary of processed parameters.
    """
    processed_params = {}

    for param_name, param in func_signature.parameters.items():
        param_type = param.annotation  # Get type hint of the parameter
        value = param_values.get(param_name)  # Provided value for the parameter

        if value is not None:
            # Assuming convert_param_type is a function that converts the value based on its type
            converted_value = convert_param_type(param_type, value)
            processed_params[param_name] = converted_value
        else:
            # Use default value if available
            if param.default is not inspect.Parameter.empty:
                processed_params[param_name] = param.default

    return processed_params


def is_internal_dependency(annotation: Any) -> bool:
    """
    Check if a parameter annotation contains InternalDependency.
    """
    if get_origin(annotation) is Annotated:
        return InjectDependency in get_args(annotation)
    return False

def resolve_forward_ref(ref: Any, context_dict: dict) -> Any:
    """
    Resolves a ForwardRef to its actual type. Returns as-is if not a ForwardRef.
    """
    if not isinstance(ref, ForwardRef):
        return ref

    def context_to_globalns(context_dict: dict[type, object]) -> dict[str, object]:
        """
        Converts a type-based context dictionary into a global namespace
        mapping class names to classes, for use in resolving ForwardRefs.
        """
        globalns = {}

        for cls_type in context_dict:
            if hasattr(cls_type, "__name__"):
                globalns[cls_type.__name__] = cls_type

        return globalns
    try:
        globalns = context_to_globalns(context_dict)
        # For Python 3.10+ with recursive_guard
        return ref._evaluate(globalns, None, recursive_guard=set())
    except Exception as e:
        import logging
        logging.warning(f"Could not resolve ForwardRef {ref}: {e}")
        return ref

def build_injection_params(
        signature: inspect.Signature,
        context_dict: dict,
        user_kwargs: dict
) -> dict:
    """
    Given a function signature, a DI context (dictionary by type),
    and user-supplied kwargs, build the final parameters for calling the function.
    """
    params = signature.parameters  # OrderedDict(name -> Parameter)
    final_kwargs = dict(user_kwargs or {})  # Start with user overrides

    for name, param in params.items():
        # Skip if user explicitly provided this param and not None
        if name in final_kwargs and final_kwargs[name] is not None:
            continue

        # Skip if the param has no type annotation
        if param.annotation == inspect.Parameter.empty:
            continue

        needed_type = param.annotation
        is_injected_dependency = False

        # Check if the parameter is Annotated and contains InjectDependency
        if get_origin(needed_type) is Annotated:
            annotations = get_args(needed_type)
            if InjectDependency in annotations:
                is_injected_dependency = True
                # Extract the actual type from the Annotated arguments
                needed_type = next(arg for arg in annotations if arg is not InjectDependency)

                needed_type = resolve_forward_ref(needed_type,context_dict)

        injected_instance = None

        # Look for the needed type in the context dictionary
        for known_type, instance in context_dict.items():
            if known_type.__qualname__ == needed_type.__qualname__:
                injected_instance = instance
                break

        if injected_instance is not None:
            logger.info(f"Injecting {injected_instance} as {param.name}")
            final_kwargs[name] = injected_instance
        elif is_injected_dependency:
            # Raise an error if a required InjectDependency cannot be resolved
            raise ValueError(f"Dependency for parameter '{name}' of type '{needed_type}' not found in context_dict.")

    return final_kwargs


def ensure_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_running_loop()
        return loop
    except RuntimeError:
        logger.debug("Create a new loop for this thread")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def find_package_source_from_pyproject(module_path: Path) -> tuple[Path | None, str | None]:
    """
    Attempts to find the package source directory and package name from a pyproject.toml file.

    Args:
        module_path (Path): The directory path where to look for pyproject.toml

    Returns:
        tuple[Path | None, str | None]: A tuple containing:
            - Path to the __init__.py file if found/created, None otherwise
            - Package name from pyproject.toml if found, None otherwise
    """
    # Check for pyproject.toml (for git-cloned modules)
    pyproject_path = module_path / "pyproject.toml"
    if not pyproject_path.exists():
        return None, None

    logger.debug(f"Found pyproject.toml in {module_path}")

    # Check if we have a TOML parser available
    if tomllib is None:
        logger.warning("Neither tomllib nor tomli is available. Cannot parse pyproject.toml.")
        return None, None

    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        # Extract package name from entry points
        package_name = None
        if "project" in pyproject_data and "entry-points" in pyproject_data["project"]:
            entry_points = pyproject_data["project"]["entry-points"]
            if "fastpluggy.plugins" in entry_points:
                # Get the first entry point value
                plugin_entry = next(iter(entry_points["fastpluggy.plugins"].values()), "")
                if plugin_entry:
                    # Extract package name from entry point (e.g., "fastpluggy_plugin.audio_transcript.plugin:AudioTranscriptPlugin")
                    package_name = plugin_entry.split(".plugin:")[0]
                    logger.debug(f"Found package name in entry point: {package_name}")

        # If no package name found in entry points, try to get it from packages
        if not package_name and "tool" in pyproject_data and "setuptools" in pyproject_data["tool"]:
            setuptools_config = pyproject_data["tool"]["setuptools"]
            if "packages" in setuptools_config:
                packages = setuptools_config["packages"]
                if packages and isinstance(packages, list) and len(packages) > 0:
                    package_name = packages[0]
                    logger.debug(f"Found package name in packages: {package_name}")

        # Look for package source directory in pyproject.toml
        init_path = None
        if "tool" in pyproject_data and "setuptools" in pyproject_data["tool"]:
            setuptools_config = pyproject_data["tool"]["setuptools"]

            # Check if package-dir is specified
            if "package-dir" in setuptools_config:
                package_dirs = setuptools_config["package-dir"]
                # Get the first package directory value
                if package_dirs and isinstance(package_dirs, dict):
                    first_package = next(iter(package_dirs.values()), "")
                    if first_package:
                        src_dir = module_path / first_package
                        logger.debug(f"Found package source directory in pyproject.toml: {src_dir}")
                        if src_dir.exists() and src_dir.is_dir():
                            # Try to create __init__.py in the source directory
                            init_path = create_init_file(src_dir)
                            if init_path and init_path.exists():
                                logger.info(f"Created __init__.py in package source directory: {src_dir}")
                            else:
                                logger.error(f"Failed to create __init__.py in package source directory: {src_dir}")

        return init_path, package_name
    except Exception as e:
        logger.error(f"Error parsing pyproject.toml: {e}")

    return None, None


def get_module(module_name: str, reload: bool = True, module_path: str = None):
    """
    Retrieve a module by name, avoiding multiple imports.
    If reload is True, reload the module even if it's already imported.

    If module_path is provided, dynamically load the module from the given path.
    If module_path is a directory, it assumes it's a package and loads __init__.py.

    Args:
        module_name (str): The name of the module to retrieve.
        reload (bool): Whether to reload the module if it's already imported.
        module_path (str, optional): The file path of the module to load.

    Returns:
        ModuleType | None: The imported or reloaded module, or None if an error occurs.
    """
    # Replace dashes with underscores in module name for Python compatibility
    safe_module_name = module_name.replace("-", "_")
    if safe_module_name in sys.modules:
        # Module is already imported
        if reload:
            logger.info(f"{safe_module_name} is already loaded / reloading it.")
            return importlib.reload(sys.modules[safe_module_name])
        return sys.modules[safe_module_name]

    if module_path:
        module_path = Path(module_path)

        if module_path.is_dir():
            logger.info(f"Module path {module_path} is a directory — assuming package and ensuring __init__.py.")
            init_path = create_init_file(module_path)

            if not init_path or not init_path.exists():
                logger.error(f"Failed to find or create __init__.py in {module_path}")
                return None

            module_path = init_path

        if not module_path.exists():
            logger.error(f"Module file {module_path} does not exist.")
            return None

        logger.info(f"Loading {safe_module_name} from {module_path}")

        spec = importlib.util.spec_from_file_location(safe_module_name,str(module_path))
        if spec is None or spec.loader is None:
            logger.error(f"Could not load specification for module {safe_module_name}")
            return None

        module = importlib.util.module_from_spec(spec)
        # Register module in sys.modules before executing it to handle potential circular imports
        sys.modules[safe_module_name] = module

        # Add the parent directory to sys.path temporarily to help with imports
        parent_dir = str(module_path.parent)
        path_modified = False
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            path_modified = True
            logger.debug(f"Added {parent_dir} to sys.path temporarily")

        try:
            # Set __file__ attribute if it's not already set
            if not hasattr(module, '__file__'):
                module.__file__ = str(module_path)

            # Set __package__ attribute for proper relative imports
            if not hasattr(module, '__package__') or not module.__package__:
                # If module_name contains dots, use everything before the last dot as the package
                if '.' in safe_module_name:
                    module.__package__ = safe_module_name.rsplit('.', 1)[0]
                else:
                    module.__package__ = ''

            # If this is a package (loading __init__.py), set __path__ for submodule imports
            if module_path.name == '__init__.py' and not hasattr(module, '__path__'):
                module.__path__ = [str(module_path.parent)]

            spec.loader.exec_module(module)
            return module
        except Exception as e:
            # Remove from sys.modules if execution failed
            if safe_module_name in sys.modules:
                del sys.modules[safe_module_name]
            logger.error(f"Failed to load module {safe_module_name}: {e}")
            raise e
        finally:
            # Restore sys.path if we modified it
            if path_modified:
                sys.path.remove(parent_dir)
                logger.debug(f"Removed {parent_dir} from sys.path")

    # If no custom path is provided, use normal import
    logger.info(f"Importing the module {safe_module_name} dynamically")
    try:
        return importlib.import_module(safe_module_name)
    except ModuleNotFoundError:
        logger.error(f"Module {safe_module_name} not found.")
    except Exception as e:
        logger.error(f"Error importing module {safe_module_name}: {e}")

    return None


def call_with_injection(func, context_dict, user_kwargs):
    """
    High-level function to:
      1) Build the signature
      2) Collect injection params
      3) Validate against the signature (bind/apply_defaults)
      4) Call the function (sync or async)
    """
    # 1. Get the function signature
    sig = inspect.signature(func)

    # 2. Build final kwargs for injection
    call_kwargs = build_injection_params(sig, context_dict, user_kwargs)

    # 3. Use bind + apply_defaults to validate / fill defaults
    bound_args = sig.bind(**call_kwargs)  # raises TypeError if something's missing or extra
    bound_args.apply_defaults()  # fills in any default values from the signature

    # 4. Convert BoundArguments back to a dictionary
    final_kwargs = bound_args.arguments

    # 5. Execute the function, handling async vs. sync
    if inspect.iscoroutinefunction(func):
        # If we're already in an async environment, do "await".
        # If we're not, we can do "asyncio.run".
        loop = ensure_event_loop()
        if loop.is_running():
            # Already in an event loop
            return await_in_existing_loop(func, final_kwargs)
        else:
            # No event loop is running
            return asyncio.run(func(**final_kwargs))
    else:
        return func(**final_kwargs)


async def await_in_existing_loop(func, call_kwargs):
    return await func(**call_kwargs)
