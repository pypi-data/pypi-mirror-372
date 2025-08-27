# import libs
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# local imports
from .llm import llm_router
from .config_api import config_router


# NOTE: logger
logger = logging.getLogger(__name__)


class ThermoAIAPI:
    '''
    ThermoAI AI API class that initializes a FastAPI application and sets up the necessary middleware.
    This class is designed to handle the initialization of the FastAPI app and the setup of CORS middleware.
    '''
    # NOTE: attributes
    _cors_origins: Optional[List[str]] = ["*"]  # Default to allow all origins
    _name: Optional[str] = None
    _version: Optional[str] = None
    _description: Optional[str] = None

    def __init__(
        self,
        cors_origins: Optional[List[str]] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None
    ):
        '''
        This initializes the FastAPI application and sets up the necessary middleware.
        It also prepares the THermoAI agent for handling requests.

        Parameters
        ----------
        cors_origins : Optional[List[str]]
            A list of allowed CORS origins. If None, defaults to allowing all origins.
        '''
        # NOTE: Initialize CORS origins
        self._cors_origins = cors_origins
        self._name = name
        self._version = version
        self._description = description

        # SECTION: Initialize FastAPI application
        try:
            self.app = FastAPI()
        except Exception as e:
            logger.error(f"Failed to initialize FastAPI app: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to initialize API") from e

        # SECTION: Setup the API middleware
        try:
            self._setup_middleware()
        except Exception as e:
            logger.error(f"Failed to setup middleware: {e}")
            raise HTTPException(
                status_code=500, detail="Middleware setup failed")

        # SECTION: Register API routers
        try:
            self._register_routers()
        except Exception as e:
            logger.error(f"Failed to register routers: {e}")
            raise HTTPException(
                status_code=500, detail="Router registration failed") from e

    @property
    def cors_origins(self) -> List[str]:
        """Returns the list of allowed CORS origins."""
        if self._cors_origins is None:
            return ["*"]
        return self._cors_origins

    @property
    def name(self) -> str:
        """Returns the API name."""
        if self._name is None:
            return "No name set"
        return self._name

    @property
    def version(self) -> str:
        """Returns the API version."""
        if self._version is None:
            return "No version set"
        return self._version

    @property
    def description(self) -> str:
        """Returns the API description."""
        if self._description is None:
            return "No description set"
        return self._description

    def _setup_middleware(self):
        """Setup middleware for the FastAPI application."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],  # Allow all methods
            allow_headers=["*"],  # Allow all headers
        )

    def _register_routers(self):
        """Register API routers to the FastAPI application."""
        # Register the llm router
        self.app.include_router(llm_router)
        # Register the config router
        self.app.include_router(config_router)
