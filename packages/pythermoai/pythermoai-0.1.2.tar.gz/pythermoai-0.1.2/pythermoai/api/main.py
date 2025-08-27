# import libs
import logging
import time
import json
from typing import (
    Dict,
    Union,
    List,
    Optional
)
from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    Depends
)
from fastapi.responses import JSONResponse
from pathlib import Path
# langchain
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import (
    HumanMessage,
)
# locals
from .ai_api import ThermoAIAPI
from . import data_agent, equations_agent
from ..agents import (
    create_agent,
    DATA_AGENT_PROMPT,
    EQUATIONS_AGENT_PROMPT,
    DATA_AGENT_NAME,
    EQUATIONS_AGENT_NAME
)
from ..models import (
    ChatMessage,
    LlmConfig,
    ApiConfigSummary,
    OverallSettings,
    AppInfo,
    AgentDetails,
    LlmDetails,
    AgentMessage,
    stdioMCP,
    streamableHttpMCP
)
from ..memory import generate_thread
from ..utils import agent_message_analyzer, message_token_counter
from ..config import default_token_metadata, default_model_settings, default_api_config
# dependencies
from .deps import (
    get_state,
    get_agents,
    get_llm_config_dep,
    get_mcp_source_dep
)

# NOTE: logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# NOTE: constants
# temperature and max_tokens for the LLM
DEFAULT_TEMPERATURE = default_model_settings['temperature']
DEFAULT_MAX_TOKENS = default_model_settings['max_tokens']

# input tokens and output tokens
DEFAULT_INPUT_TOKENS = default_token_metadata['input_tokens']
DEFAULT_OUTPUT_TOKENS = default_token_metadata['output_tokens']


# SECTION: create_api function

async def create_api(
    model_provider: str,
    model_name: str,
    data_agent_prompt: Optional[str] = None,
    equations_agent_prompt: Optional[str] = None,
    mcp_source: Optional[
        Union[
        Dict[str, Dict[str, str]],
        Dict[str, Dict[str, str] | Dict[str, str]],
        Dict[str, Dict[str, str | List[str] | Dict[str, str]]],
        str,
        Path
        ]
    ] = None,
    memory_mode: bool = True,
    **kwargs
) -> FastAPI:
    """
    Create and return a FastAPI application instance with the PyThermoAI API.

    Parameters
    ----------
    model_provider : str
        The provider of the model to be used (e.g., "openai", "google").
    model_name : str
        The name of the model to be used for the agent.
    data_agent_prompt : str, optional
        The prompt for the data agent.
    equations_agent_prompt : str, optional
        The prompt for the equations agent.
    mcp_source : Optional[Union[Dict[str, Dict[str, str]],
        Dict[str, Dict[str, str | List[str]]], str, Path]]
        A dictionary containing the MCP configurations or a path to a YAML file containing the MCP configurations.
    memory_mode : bool, optional
        Whether to enable memory mode for the agent, by default False.
    kwargs : dict
        Additional keyword arguments for future extensions.
        - temperature: float, optional
            The temperature for the LLM, by default 0.0.
        - max_tokens: int, optional
            The maximum number of tokens for the LLM, by default 2048.
        - cors_origins: List[str], optional
            A list of allowed CORS origins. If None, defaults to allowing all origins.
        - name: str, optional
            The name of the API, by default "Thermo AI API".
        - version: str, optional
            The version of the API, by default "No version set".
        - description: str, optional
            A description of the API, by default "No description set".

    Returns
    -------
    FastAPI
        The FastAPI application instance.
    """
    # NOTE: inputs
    cors_origins = kwargs.get('cors_origins', None)
    name = kwargs.get('name', None)
    version = kwargs.get('version', None)
    description = kwargs.get('description', None)

    # SECTION: Initialize the Thermo AI API
    ThermoAIAPI_ = ThermoAIAPI(
        cors_origins=cors_origins,
        name=name,
        version=version,
        description=description
    )

    # NOTE: create fastapi app instance
    app = ThermoAIAPI_.app

    # NOTE: set running state
    app.state.is_running = True

    # SECTION: app state configurations
    # set initial llm configurations in app.state
    app.state.temperature = kwargs.get(
        'temperature', DEFAULT_TEMPERATURE)
    app.state.max_tokens = kwargs.get(
        'max_tokens', DEFAULT_MAX_TOKENS)

    # NOTE: add api config to app.state
    api_config = kwargs.get('api_config', default_api_config)
    # check if api_config is provided
    if not api_config:
        logger.warning(
            "api_config not provided in kwargs, setting default values.")

    app.state.api_config = {
        "port": api_config.get("port", 8000),
        "host": api_config.get("host", "127.0.0.1"),
        "apiUrl": api_config.get(
            "apiUrl",
            f"http://{api_config.get('host', '127.0.0.1')}:{api_config.get('port', 8000)}"
        ),
    }

    # model provider
    app.state.model_provider = model_provider
    # model name
    app.state.model_name = model_name
    # data agent prompt
    app.state.data_agent_prompt = data_agent_prompt or DATA_AGENT_PROMPT
    # equations agent prompt
    app.state.equations_agent_prompt = \
        equations_agent_prompt or EQUATIONS_AGENT_PROMPT
    # mcp source
    app.state.mcp_source = mcp_source
    # memory mode
    app.state.memory_mode = memory_mode

    # SECTION: agent initialization if app.state.agents does not exist
    # initialize app.state.agents
    app.state.agents = {}

    # SECTION: websockets configurations
    # set client
    websocket_clients = set()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        websocket_clients.add(websocket)
        try:
            while True:
                await websocket.receive_text()  # Ignore incoming messages
        except Exception:
            pass
        finally:
            websocket_clients.remove(websocket)

    async def broadcast_log(log: str):
        for ws in list(websocket_clients):
            try:
                # not empty log
                if log and len(log.strip()) > 0:
                    # send log to websocket
                    await ws.send_text(log)
            except Exception:
                websocket_clients.remove(ws)

    async def broadcast_agent_log(log: AgentMessage):
        for ws in list(websocket_clients):
            try:
                await ws.send_text(json.dumps(log.model_dump()))
            except Exception:
                websocket_clients.remove(ws)

    # SECTION: Register the API routes
    app.include_router(data_agent.config_router)
    app.include_router(equations_agent.config_router)

    # SECTION: API routes
    async def agent_initialization():
        """
        Initialize the agents with the initial provided parameters.
        Returns True if successful, False otherwise.
        """
        try:
            # NOTE: data agent
            if DATA_AGENT_NAME not in app.state.agents:
                # build data-agent (empty)
                app.state.agents[DATA_AGENT_NAME] = {}

            app.state.agents[DATA_AGENT_NAME] = await create_agent(
                model_provider=app.state.model_provider,
                model_name=app.state.model_name,
                agent_name=DATA_AGENT_NAME,
                agent_prompt=app.state.data_agent_prompt,
                mcp_source=app.state.mcp_source,
                memory_mode=app.state.memory_mode,
                **kwargs
            )
            logger.info(
                f"data-agent agent created successfully with model: {model_name}, agent: {DATA_AGENT_NAME}")

            # NOTE: equations agent
            if EQUATIONS_AGENT_NAME not in app.state.agents:
                # build equations-agent (empty)
                app.state.agents[EQUATIONS_AGENT_NAME] = {}

            app.state.agents[EQUATIONS_AGENT_NAME] = await create_agent(
                model_provider=app.state.model_provider,
                model_name=app.state.model_name,
                agent_name=EQUATIONS_AGENT_NAME,
                agent_prompt=app.state.equations_agent_prompt,
                mcp_source=app.state.mcp_source,
                memory_mode=app.state.memory_mode,
                **kwargs
            )
            logger.info(
                f"equations-agent agent created successfully with model: {model_name}, agent: {EQUATIONS_AGENT_NAME}")

            # return
            return True
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            return False

    @app.get("/pythermoai")
    async def root():
        """
        Root endpoint to check if the API is running.
        """
        return JSONResponse(
            content={
                "message": "PyThermoAI API is running",
                "success": True
            },
            status_code=200
        )

    @app.get("/agent-initialization")
    async def initialize_agent():
        """
        Endpoint to initialize the agent with the provided parameters.
        """
        result = await agent_initialization()
        if result:
            return JSONResponse(
                content={
                    "message": "Agent initialized successfully",
                    "success": True
                },
                status_code=200
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize agent"
            )

    @app.get("/agents")
    async def get_all_agents(state=Depends(get_state)):
        """
        Endpoint to get all agents in the app state.
        """
        # NOTE: data agent
        data_agent = {
            "agent_name": DATA_AGENT_NAME,
            "model_provider": state.model_provider,
            "model_name": state.model_name,
            "agent_prompt": state.data_agent_prompt,
            "mcp_source": state.mcp_source,
            "memory_mode": state.memory_mode
        }

        # NOTE: equations agent
        equations_agent = {
            "agent_name": EQUATIONS_AGENT_NAME,
            "model_provider": state.model_provider,
            "model_name": state.model_name,
            "agent_prompt": state.equations_agent_prompt,
            "mcp_source": state.mcp_source,
            "memory_mode": state.memory_mode
        }

        return JSONResponse(
            content={
                "message": "Agent prompts retrieved successfully",
                "success": True,
                "data": [data_agent, equations_agent]
            },
            status_code=200
        )

    @app.get("/mcp-source")
    async def get_mcp_source(
        mcp_source: Dict[str, dict] = Depends(get_mcp_source_dep)
    ):
        """
        Endpoint to get the current MCP source configuration.
        """
        return JSONResponse(
            content={
                "message": "MCP source configuration retrieved successfully",
                "success": True,
                "data": mcp_source,
            },
            status_code=200
        )

    @app.get("/llm/config")
    async def get_llm_config(
        llm_config: LlmConfig = Depends(get_llm_config_dep)
    ):
        """
        Endpoint to get the current LLM configuration.
        """
        # return the llm configuration
        return JSONResponse(
            content={
                "message": "LLM configuration retrieved successfully",
                "data": llm_config.model_dump(),
                "success": True
            },
            status_code=200
        )

    @app.post("/mcp-config")
    async def set_mcp_config(
        mcp_config: Dict[str, dict]  # Accept raw dicts
    ):
        """
        Config the MCP source with the necessary parameters.
        """
        try:
            # NOTE: log the received MCP configuration
            logger.info(f"Received MCP configuration: {mcp_config}")

            # SECTION: Validate each config using discriminated union
            validated_config = {}
            for key, value in mcp_config.items():
                transport = value.get("transport")
                if transport == "stdio":
                    # Validate using stdioMCP model and convert to dict
                    validated_config[key] = stdioMCP(**value).model_dump()
                elif transport == "streamable_http":
                    validated_config[key] = streamableHttpMCP(
                        **value).model_dump()
                else:
                    raise ValueError(f"Unknown transport: {transport}")

            # SECTION: update the mcp_source in app.state
            app.state.mcp_source = validated_config

            # log
            logger.info(
                f"Updated MCP source validated_config: {validated_config}")
            logger.info(f"Updated MCP source: {app.state.mcp_source}")

            # NOTE: return success message
            logger.info("MCP source configured successfully")
            return JSONResponse(
                content={
                    "message": "MCP source configured successfully",
                    "success": True,
                    "data": app.state.mcp_source
                },
                status_code=200
            )
        except Exception as e:
            logger.error(f"Error configuring MCP source: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to configure MCP source: {e}")

    @app.post("/llm/config")
    async def set_llm_config(
        llm_config: LlmConfig
    ):
        """
        Config the LLM with the necessary parameters.
        """
        try:
            # SECTION: extract parameters from the llm_config
            model_provider_ = llm_config.model_provider
            model_name_ = llm_config.model_name
            temperature_ = llm_config.temperature
            max_tokens_ = llm_config.max_tokens

            # NOTE: update the agent's LLM configuration
            if model_provider_ is not None:
                model_provider = model_provider_
                # set the app state
                app.state.model_provider = model_provider_
            else:
                model_provider = app.state.model_provider

            # NOTE: update the model_name
            if model_name_ is not None:
                model_name = model_name_
                # set the app state
                app.state.model_name = model_name_
            else:
                model_name = app.state.model_name

            # NOTE: update the temperature
            if temperature_ is not None:
                # update the kwargs for temperature
                kwargs['temperature'] = temperature_
                # app sate
                app.state.temperature = temperature_

            # NOTE: update the max_tokens
            if max_tokens_ is not None:
                # update the kwargs for max_tokens
                kwargs['max_tokens'] = max_tokens_
                # app state
                app.state.max_tokens = max_tokens_

            # SECTION: reinitialize agents with the new LLM configuration
            result = await agent_initialization()
            if result:
                logger.info("LLM configured successfully")
                return JSONResponse(
                    content={
                        "message": f"LLM configured successfully with model: {model_provider} - {model_name}, temperature: {app.state.temperature}, max_tokens: {app.state.max_tokens}",
                        "success": True
                    },
                    status_code=200
                )
            else:
                logger.error(
                    "Failed to reinitialize agent after LLM config update")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to reinitialize agent after LLM config update"
                )
        except Exception as e:
            logger.error(f"Error configuring LLM: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to configure LLM: {e}")

    @app.post("/chat", response_model=ChatMessage)
    async def user_agent_chat(
        user_message: ChatMessage
    ):
        """
        Handle user-agent chat interaction.

        Parameters
        ----------
        user_message : ChatMessage
            The message from the user to the agent.

        Returns
        -------
        ChatMessage
            The response from the agent to the user.
        """
        # NOTE: log
        logger.info(f"Received user message: {user_message}")
        # SECTION: Extract the thread_id from the user message
        thread_id = user_message.thread_id
        user_content = user_message.content
        # timestamp
        timestamp = user_message.timestamp
        # agent selection
        agent_selection = user_message.agent_selection

        # NOTE: Generate a new thread if thread_id is not provided
        if not thread_id:
            _, new_thread_id = generate_thread()
            thread_id = new_thread_id
            user_message.thread_id = new_thread_id

        # timestamp
        if not timestamp:
            timestamp = time.time()
            user_message.timestamp = timestamp

        try:
            # SECTION: Ensure the agent is created
            # NOTE: check if agent_selection is provided
            agent_selection = user_message.agent_selection

            # check if agent_selection is provided and exists in app.state.agents
            if (
                agent_selection and
                hasattr(app.state, "agents") and
                agent_selection in app.state.agents
            ):
                agent = app.state.agents[agent_selection]
            else:
                agent = getattr(app.state, "agent", None)

            if agent is None:
                logger.error("ThermoAI agent is not created yet.")
                return ChatMessage(
                    role="assistant",
                    content="ThermoAI agent is not created yet.",
                    thread_id=thread_id,
                    response_time=None,
                    timestamp=timestamp,
                    input_tokens=DEFAULT_INPUT_TOKENS,
                    output_tokens=DEFAULT_OUTPUT_TOKENS,
                    agent_selection=agent_selection
                )

            # NOTE: Measure computation time
            start_time = time.time()

            # NOTE: Invoke the agent with the user message
            response = await agent.ainvoke(
                {
                    "messages": user_content
                },
                config=RunnableConfig(
                    configurable={
                        "thread_id": thread_id,
                    }
                )
            )

            # NOTE: Measure end time and calculate response time
            end_time = time.time()
            response_time = end_time - start_time

            # SECTION: Check response and return the last message
            # last message is the agent's response
            if response and isinstance(response, dict):
                messages = response.get("messages")
                if messages and isinstance(messages, list):
                    response_message = messages[-1]

                    # NOTE: token metadata
                    token_metadata = message_token_counter(response_message)
                    # set default values if not present
                    input_tokens = token_metadata.input_tokens if hasattr(
                        token_metadata, 'input_tokens') else DEFAULT_INPUT_TOKENS
                    output_tokens = token_metadata.output_tokens if hasattr(
                        token_metadata, 'output_tokens') else DEFAULT_OUTPUT_TOKENS

                    # NOTE: main response
                    return ChatMessage(
                        role="assistant",
                        content=getattr(
                            response_message,
                            "content",
                            str(response_message)
                        ),
                        thread_id=thread_id,
                        response_time=response_time,
                        timestamp=timestamp,
                        messages=messages,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        agent_selection=agent_selection
                    )
                else:
                    logger.error("Agent did not return any messages.")
                    return ChatMessage(
                        role="assistant",
                        content="Agent did not return any messages.",
                        thread_id=thread_id,
                        response_time=response_time,
                        timestamp=timestamp,
                        messages=[],
                        input_tokens=DEFAULT_INPUT_TOKENS,
                        output_tokens=DEFAULT_OUTPUT_TOKENS,
                        agent_selection=agent_selection
                    )
            else:
                logger.error("Agent response is not a valid dictionary.")
                return ChatMessage(
                    role="assistant",
                    content="Agent response is not a valid dictionary.",
                    thread_id=thread_id,
                    response_time=response_time,
                    timestamp=timestamp,
                    messages=[],
                    input_tokens=DEFAULT_INPUT_TOKENS,
                    output_tokens=DEFAULT_OUTPUT_TOKENS,
                    agent_selection=agent_selection
                )
        except Exception as e:
            logger.error(f"Error in user_agent_chat: {e}")
            return ChatMessage(
                role="assistant",
                content=f"Failed to process user message: {e}",
                thread_id=thread_id,
                response_time=None,
                timestamp=timestamp,
                messages=[],
                input_tokens=DEFAULT_INPUT_TOKENS,
                output_tokens=DEFAULT_OUTPUT_TOKENS,
                agent_selection=agent_selection
            )

    @app.post("/chat-stream", response_model=ChatMessage)
    async def user_agent_chat_stream(
        user_message: ChatMessage
    ):
        """
        Handle user-agent chat interaction.

        Parameters
        ----------
        user_message : ChatMessage
            The message from the user to the agent.

        Returns
        -------
        ChatMessage
            The response from the agent to the user.
        """
        # NOTE: log
        logger.info(f"Received user message: {user_message}")
        # SECTION: Extract the thread_id from the user message
        thread_id = user_message.thread_id
        user_content = user_message.content
        # timestamp
        timestamp = user_message.timestamp
        # agent selection
        agent_selection = user_message.agent_selection

        # NOTE: Generate a new thread if thread_id is not provided
        if not thread_id:
            _, new_thread_id = generate_thread()
            thread_id = new_thread_id
            user_message.thread_id = new_thread_id

        # timestamp
        if not timestamp:
            timestamp = time.time()
            user_message.timestamp = timestamp

        try:
            # SECTION: Ensure the agent is created
            agent_selection = user_message.agent_selection
            if (
                agent_selection and
                hasattr(app.state, "agents") and
                agent_selection in app.state.agents
            ):
                agent = app.state.agents[agent_selection]
            else:
                agent = getattr(app.state, "agent", None)

            if agent is None:
                logger.error("ThermoAI agent is not created yet.")
                return ChatMessage(
                    role="assistant",
                    content="ThermoAI agent is not created yet.",
                    thread_id=thread_id,
                    response_time=None,
                    timestamp=timestamp,
                    input_tokens=DEFAULT_INPUT_TOKENS,
                    output_tokens=DEFAULT_OUTPUT_TOKENS,
                    agent_selection=agent_selection
                )

            # NOTE: Measure computation time
            start_time = time.time()

            # SECTION: Invoke the agent with the user message
            async for chunk in agent.astream(
                {"messages": [
                    HumanMessage(content=user_content),
                ]},
                config=RunnableConfig(
                    configurable={
                        "thread_id": thread_id
                    }
                ),
                stream_mode="updates"
            ):
                # NOTE: Process each chunk
                if not isinstance(chunk, dict):
                    logger.error(f"Received non-dictionary chunk: {chunk}")
                    return ChatMessage(
                        role="assistant",
                        content="Agent response is not a valid dictionary.",
                        thread_id=thread_id,
                        response_time=None,
                        timestamp=timestamp,
                        messages=[],
                        input_tokens=DEFAULT_INPUT_TOKENS,
                        output_tokens=DEFAULT_OUTPUT_TOKENS,
                        agent_selection=agent_selection
                    )

                # NOTE: iterate through the messages in the chunk
                for value in chunk.values():
                    # get the messages
                    messages = value['messages']

                    # iterate through messages
                    for message in messages:
                        # agent message analyzer
                        agent_message = agent_message_analyzer(message)

                        # LINK: broadcast the log to all websocket clients
                        if agent_message:
                            await broadcast_agent_log(agent_message)

            # NOTE: Measure end time and calculate response time
            end_time = time.time()
            # time unit is seconds
            response_time = end_time - start_time

            # SECTION: Check response and return the last message
            # last message is the agent's response
            if messages and isinstance(messages, list):

                response_message = messages[-1]
                # NOTE: token metadata
                token_metadata = message_token_counter(response_message)
                # set default values if not present
                input_tokens = token_metadata.input_tokens if hasattr(
                    token_metadata, 'input_tokens') else DEFAULT_INPUT_TOKENS
                output_tokens = token_metadata.output_tokens if hasattr(
                    token_metadata, 'output_tokens') else DEFAULT_OUTPUT_TOKENS

                # NOTE: main response
                return ChatMessage(
                    role="assistant",
                    content=getattr(response_message,
                                    "content", str(response_message)),
                    thread_id=thread_id,
                    response_time=response_time,
                    timestamp=timestamp,
                    messages=messages,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    agent_selection=agent_selection
                )
            else:
                # NOTE: no messages returned
                logger.error("Agent response is not a list of messages.")
                return ChatMessage(
                    role="assistant",
                    content="Agent response is not a list of messages.",
                    thread_id=thread_id,
                    response_time=response_time,
                    timestamp=timestamp,
                    messages=[],
                    input_tokens=DEFAULT_INPUT_TOKENS,
                    output_tokens=DEFAULT_OUTPUT_TOKENS,
                    agent_selection=agent_selection
                )
        except Exception as e:
            logger.error(f"Error in user_agent_chat_stream: {e}")
            return ChatMessage(
                role="assistant",
                content=f"Failed to process user message: {e}",
                thread_id=thread_id,
                response_time=None,
                timestamp=timestamp,
                messages=[],
                input_tokens=DEFAULT_INPUT_TOKENS,
                output_tokens=DEFAULT_OUTPUT_TOKENS,
                agent_selection=agent_selection
            )

    # SECTION: Return the FastAPI application instance
    @app.get("/info", response_model=ApiConfigSummary)
    async def get_app_info():
        """
        Return app info, agent details, llm details, and overall settings as an ApiConfigSummary model.
        """
        try:
            # NOTE: Get the agent details
            agent_obj = getattr(app.state, "agent", None)

            # NOTE: app info
            app_info = AppInfo(
                name=ThermoAIAPI_.name,
                version=ThermoAIAPI_.version,
                description=ThermoAIAPI_.description,
            )

            # NOTE: Data agent details
            data_agent_details = AgentDetails(
                exists=agent_obj is not None,
                model_provider=app.state.model_provider,
                model_name=app.state.model_name,
                agent_name=DATA_AGENT_NAME,
                agent_prompt=app.state.data_agent_prompt,
                mcp_source=app.state.mcp_source,
                memory_mode=app.state.memory_mode,
            )

            # NOTE: Equations agent details
            equations_agent_details = AgentDetails(
                exists=agent_obj is not None,
                model_provider=app.state.model_provider,
                model_name=app.state.model_name,
                agent_name=EQUATIONS_AGENT_NAME,
                agent_prompt=app.state.equations_agent_prompt,
                mcp_source=app.state.mcp_source,
                memory_mode=app.state.memory_mode,
            )

            # NOTE: LLM details
            llm_details = LlmDetails(
                temperature=getattr(
                    app.state,
                    "temperature",
                    DEFAULT_TEMPERATURE
                ),
                max_tokens=getattr(
                    app.state,
                    "max_tokens",
                    DEFAULT_MAX_TOKENS
                )
            )

            # NOTE: Overall settings
            overall_settings = OverallSettings(
                cors_origins=ThermoAIAPI_.cors_origins
            )

            # NOTE: the ApiConfigSummary model
            ApiConfigSummary_ = ApiConfigSummary(
                app=app_info,
                agent=[
                    data_agent_details,
                    equations_agent_details
                ],
                llm=llm_details,
                settings=overall_settings
            )

            # NOTE: return json response
            return JSONResponse(
                content={
                    "message": "App info retrieved successfully",
                    "success": True,
                    "data": ApiConfigSummary_.model_dump()
                },
                status_code=200
            )
        except Exception as e:
            logger.error(f"Error in get_app_info: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve app info: {e}"
            )
    return app
