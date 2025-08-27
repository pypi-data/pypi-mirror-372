# import libs
import logging
import asyncio
import threading
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
# local

# NOTE: logger
logger = logging.getLogger(__name__)
# set logging level
logger.setLevel(logging.INFO)

# SECTION: api router
config_router = APIRouter()

# SECTION: routes


@config_router.get("/config")
async def read_config(request: Request):
    try:
        # NOTE: check state has config attribute
        if not hasattr(request.app.state, 'api_config'):
            raise HTTPException(
                status_code=500, detail="Server configuration is not initialized.")

        # NOTE: return the current configuration
        return JSONResponse(
            content=request.app.state.api_config,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error reading configuration: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to read server configuration.")


@config_router.get("/config/exit")
async def shutdown(request: Request):
    try:
        # NOTE: check state has is_running attribute
        if not hasattr(request.app.state, 'is_running'):
            raise HTTPException(
                status_code=500, detail="Server state is not initialized.")

        # NOTE: check if the server is running
        if not request.app.state.is_running:
            raise HTTPException(
                status_code=400, detail="Server is not running.")

        # NOTE: stop the server
        def stop():
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(loop.stop)

        threading.Thread(target=stop).start()

        # NOTE: update the server state
        request.app.state.is_running = False
        logger.info("Server is shutting down...")

        # SECTION: return response
        # NOTE: return a JSON response indicating the server is shutting down
        return JSONResponse(
            content={"message": "Server is shutting down."},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to shut down the server.")
