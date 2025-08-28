import traceback
from collections import defaultdict, deque
from typing import Dict, Any
import semantic_version
from fastpluggy.core.plugin_state import PluginState
from loguru import logger


class PluginDependencyResolver:
    @staticmethod
    def get_sorted_modules_by_dependency(modules: Dict[str, PluginState]) -> Dict[str, Any]:
        """
        Perform dependency resolution and return full topological order, loadable status,
        and error details. All modules that are enabled & initialized are analyzed.
        """
        output = {
            "success": True,
            "sorted_modules": [],       # Only loadable modules (based on version + presence)
            "computed_order": [],       # Full topo sort result, including unresolvable modules
            "unresolved": [],
            "error": None,
            "modules": {},
        }

        graph = defaultdict(set)  # dependency -> set of dependents
        in_degree = defaultdict(int)  # dependent -> count of unresolved deps
        module_versions = {}
        module_deps = {}

        logger.info("🔍 Gathering module versions and declared dependencies...")
        for module in modules.values():
            if module.enabled and module.initialized:
                name = module.plugin.module_name
                version_str = module.plugin.module_version or "0.0.0"
                version = semantic_version.Version.coerce(version_str)
                deps: dict = module.plugin.depends_on or {}

                module_versions[name] = version
                module_deps[name] = deps
                in_degree[name] = 0

                output["modules"][name] = {
                    "version": str(version),
                    "depends_on": deps,
                    "status": "pending",
                    "dependency_issues": [],
                    "loadable": True,
                }

        logger.info("🔧 Validating and building dependency graph...")
        for name, deps in module_deps.items():
            for dep_name, version_constraint in deps.items():
                module_output = output["modules"][name]

                if dep_name not in modules or not modules[dep_name].initialized:
                    issue = f"Missing dependency: {dep_name} (version:{version_constraint or '(any version)'})"
                    module_output["dependency_issues"].append(issue)
                    module_output["status"] = "error"
                    module_output["loadable"] = False
                    logger.warning(f"❌ {issue} for module '{name}'")
                    continue

                actual_version = module_versions.get(dep_name, semantic_version.Version("0.0.0"))
                spec = semantic_version.NpmSpec(version_constraint)

                if not spec.match(actual_version):
                    issue = f"Version mismatch for '{dep_name}': required {version_constraint}, found {actual_version}"
                    module_output["dependency_issues"].append(issue)
                    module_output["status"] = "error"
                    module_output["loadable"] = False
                    logger.error(f"❌ {issue} (in module '{name}')")
                    continue

                graph[dep_name].add(name)
                in_degree[name] += 1
                logger.debug(f"✅ '{name}' depends on '{dep_name}' {version_constraint} (actual: {actual_version})")

        # Update module status if not already in error
        for name, info in output["modules"].items():
            if info["status"] == "pending":
                info["status"] = "ok"

        logger.info("📐 Performing topological sort...")
        queue = deque([name for name in module_deps if in_degree[name] == 0])
        full_order = []

        while queue:
            current = queue.popleft()
            full_order.append(current)
            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        output["computed_order"] = full_order

        if len(full_order) != len(module_deps):
            output["success"] = False
            output["error"] = "Cyclic or unsatisfiable dependencies detected."
            unresolved = [name for name in module_deps if name not in full_order]
            output["unresolved"] = unresolved

            for name in unresolved:
                output["modules"][name]["status"] = "unresolved"
                output["modules"][name]["loadable"] = False
                logger.error(f"🔗 Module '{name}' still has unresolved dependencies: {module_deps[name]}")
        else:
            logger.info(f"✅ Modules sorted in dependency order: {full_order}")

        output["sorted_modules"] = [
            name for name in full_order if output["modules"][name]["loadable"]
        ]

        # build a new order: first all sorted/loadable, then whatever is left
        # this avoid lost module not loadable of have dependency issue
        reordered = PluginDependencyResolver.reorder_modules(modules=modules, sorted_modules=output["sorted_modules"])
        modules.clear()
        modules.update(reordered)
        return output

    @staticmethod
    def reorder_modules(modules: dict, sorted_modules: list) -> dict:
        """
        Reorder `modules` so that keys in `sorted_modules` come first (in order),
        then all the other keys (in their original order).
        """
        ordered_names = sorted_modules + [n for n in modules if n not in sorted_modules]
        return {name: modules[name] for name in ordered_names}

    @staticmethod
    def update_plugin_states_from_result(result: dict, modules: Dict[str, PluginState]):
        """
        Updates the PluginState instances in `modules` with error/warning info based on
        the output from `get_sorted_modules_by_dependency`.

        This does not re-run dependency resolution — it only reflects the result.
        """
        for name, mod_info in result["modules"].items():
            plugin_state = modules.get(name)
            if not plugin_state:
                continue

            if mod_info["status"] in {"error", "unresolved"}:
                for issue in mod_info.get("dependency_issues", []):
                    plugin_state.dependency_issues.append(issue)

            try:
                plugin_state.process()
            except Exception as err:
                plugin_state.error.append(f"Error in process(): {err}")
                plugin_state.traceback.append(traceback.format_exc())
