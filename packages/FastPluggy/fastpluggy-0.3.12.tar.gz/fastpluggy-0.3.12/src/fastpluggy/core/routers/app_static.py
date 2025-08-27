from pathlib import Path

from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse
from loguru import logger

from fastpluggy.core.dependency import get_fastpluggy

app_static_router = APIRouter()


@app_static_router.get("/app_static/{module_name}/{file_path:path}")
async def serve_module_static(module_name: str, file_path: str, request: Request,fast_pluggy = Depends(get_fastpluggy)):
    """
    Serve static files for modules (both plugins & domains).
    Example: /app_static/myapp/css/styles.css → looks for `myapp/static/css/styles.css`
    """

    # Iterate over all module types (e.g., plugin, domain)
    manager = fast_pluggy.get_manager()
    current_module = manager.modules.get(module_name)

   # for module_type in fast_pluggy.module_types:
  #  folder = fast_pluggy.get_folder_by_module_type(module_type)
    module_static_path = Path(current_module.path) / "static"

    # Check if the file exists in this module's static folder
    file_location = module_static_path / file_path
    if file_location.exists() and file_location.is_file():
        logger.info(f"Serving static files for {module_name} module in {module_static_path}")
        return FileResponse(str(file_location))
    else:
    #    logger.warning(f"No static files found for {module_type} module in {module_static_path} in : {file_location}")

        # File not found
        logger.warning(f"Static file not found: {module_name}/{file_path}")
        return {"error": "Static file not found"}, 404
