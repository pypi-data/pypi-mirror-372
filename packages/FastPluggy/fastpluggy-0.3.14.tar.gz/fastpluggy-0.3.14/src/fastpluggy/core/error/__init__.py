from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": f"The path {request.url.path} does not exist."},
    )
