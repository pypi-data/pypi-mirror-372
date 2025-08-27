from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from loguru import logger

from fastpluggy.core.dependency import get_fastpluggy
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.tools.inspect_tools import call_with_injection, get_module

execute_router = APIRouter(
    prefix="/execute",
    tags=["admin"],
)


@execute_router.post("/{full_function_name:path}")
async def execute_function(
        full_function_name: str,
        request: Request,
        fast_pluggy=Depends(get_fastpluggy),
):
    """
    Generic endpoint to execute a function by its full name.
    """
    # Parse parameters from the request
    form_data = await request.form()
    params = dict(form_data)

    # Parse the full function name
    function_name = full_function_name
    module_name = params['_module']
    params.pop('_module')
    params.pop('_function')

    logger.info(f"Attempting to execute function '{function_name}' from module '{module_name}'.")
    redirect_url = request.headers.get("Referer", "/")

    def resolve_function(module, name: str):
        if '.' in name:
            # Resolve dotted path like 'Service.function'
            parts = name.split('.')
            obj = module
            for part in parts:
                obj = getattr(obj, part)
            return obj
        else:
            # Top-level function directly in module
            return getattr(module, name)

    try:
        # Import the module
        module = get_module(module_name)
        logger.debug(f"Module '{module_name}' imported successfully.")
        # Get the function from the module
        func = resolve_function(module, function_name)
        logger.debug(f"Function '{function_name}' retrieved from module '{module_name}'.")
    except (ImportError, AttributeError) as e:
        logger.error(f"Function '{full_function_name}' not found: {str(e)}")
        FlashMessage.add(request, f"Function '{full_function_name}' not found.", "error")
        # Redirect back to previous page
        return RedirectResponse(url=redirect_url, status_code=303)

    # Ensure that the object is callable
    if not callable(func):
        logger.error(f"Object '{function_name}' is not callable.")
        FlashMessage.add(request, f"Object '{function_name}' is not callable.", "error")
        # Redirect back to previous page
        return RedirectResponse(url=redirect_url, status_code=303)


    logger.debug(f"Parameters received for function '{function_name}': {params}")

    # Check for '_run_as_task' parameter
    run_as_task = params.pop('_run_as_task', 'false').lower() == 'true'

    # Call the function with parameters
    try:
        logger.info(f"Try to execute function '{function_name}' with run_as_task '{run_as_task}'.")
        if run_as_task:
            try:
                # Run the function as a background task
                # Construct the full function path
                function_full_path = '.'.join([module_name, function_name])
                logger.debug(f"Full function path: '{function_full_path}'")


                from fastpluggy.fastpluggy import FastPluggy
                task_id = FastPluggy.get_global('tasks_worker').submit(
                    func,
                    task_origin="execute_route",
                    kwargs=params,
                )
                logger.info(f"Function '{function_name}' scheduled as task with task_id: {task_id}")
                try:
                    url_detail = request.url_for('task_details', task_id=task_id)
                    task_detail_url = f'<a href="{url_detail}">follow progress</a>'
                except :
                    logger.error("Error when generate link to follow task.")
                    task_detail_url= ''
                FlashMessage.add(request, f"Function '{function_name}' is running as task {task_detail_url}", "success")
            except ImportError:
                logger.warning("No plugin task_worker")
                FlashMessage.add(request, "No plugin task_worker", "error")
        else:
            try:
                from fastpluggy.fastpluggy import FastPluggy

                context_dict ={
                    FastPluggy: fast_pluggy,
                    Request: request,
                }
                result = call_with_injection(func, context_dict, user_kwargs=params)

                logger.debug(f"Parameters bound successfully for function '{function_name}'.")
            except TypeError as e:
                logger.error(f"Invalid parameters for function '{function_name}': {str(e)}")
                FlashMessage.add(request, f"Invalid parameters for function '{function_name}'.", "error")
                return RedirectResponse(url=redirect_url, status_code=303)

            logger.info(f"Function '{function_name}' executed successfully. Result of exec is : {result}")
            FlashMessage.add(request, f"Function '{function_name}' executed successfully.", "success")

            if isinstance(result, list):
                redirect_response = None
                for item in result:
                    if isinstance(item, FlashMessage):
                        FlashMessage.add(request, item.message, item.category)
                    elif isinstance(item, RedirectResponse):
                        redirect_response = item  # Store the last RedirectResponse found

                if redirect_response:
                    return redirect_response  # Return the RedirectResponse after processing all FlashMessages

            elif isinstance(result, FlashMessage):
                FlashMessage.add(request, result.message, result.category)

            elif isinstance(result, RedirectResponse):
                return result


    except Exception as e:
        logger.exception(f"An error occurred while executing function '{function_name}': {str(e)}")
        FlashMessage.add(request, f"An error occurred while executing function '{function_name}'.", "error", exception=e)
        # Redirect back to previous page
        return RedirectResponse(url=redirect_url, status_code=303)

    # Redirect back to the previous page upon successful execution
    return RedirectResponse(url=redirect_url, status_code=303)
