# import libs
import logging
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
# local
from ..agents import create_agent, EQUATIONS_AGENT_NAME
from ..models import AgentConfig

# NOTE: logger
logger = logging.getLogger(__name__)
# set logging level
logger.setLevel(logging.INFO)

# SECTION: api router
config_router = APIRouter(prefix="/equations-agent")


# SECTION: routes
@config_router.post("/create")
async def create_data_agent(agent_config: AgentConfig, request: Request):
    """
    Create and initialize the data agent.
    """
    app = request.app

    if not hasattr(app.state, "agents"):
        app.state.agents = {}

    if EQUATIONS_AGENT_NAME not in app.state.agents:
        # get default values from app state
        app.state.agents[EQUATIONS_AGENT_NAME] = {}

    # SECTION: extract parameters
    model_provider = agent_config.model_provider or app.state.model_provider
    model_name = agent_config.model_name or app.state.model_name
    agent_name = agent_config.agent_name or EQUATIONS_AGENT_NAME
    agent_prompt = agent_config.agent_prompt or app.state.data_agent_prompt
    mcp_source = agent_config.mcp_source or app.state.mcp_source
    memory_mode = agent_config.memory_mode or app.state.memory_mode

    # NOTE: kwargs for agent creation
    # update kwargs with the new values
    kwargs = {}
    kwargs['temperature'] = app.state.temperature
    kwargs['max_tokens'] = app.state.max_tokens

    logger.info(
        f"Creating data agent with provider: {model_provider}, model: {model_name}, "
        f"agent name: {agent_name}, memory mode: {memory_mode}"
    )

    # SECTION: create agent
    try:
        # create the agent
        agent = await create_agent(
            model_provider=model_provider,  # default values
            model_name=model_name,
            agent_name=EQUATIONS_AGENT_NAME,
            agent_prompt=agent_prompt,
            mcp_source=mcp_source,
            memory_mode=memory_mode,
            **kwargs
        )

        # NOTE: update app state
        app.state.agents[EQUATIONS_AGENT_NAME] = agent
        # config
        app.state.model_provider = model_provider
        app.state.model_name = model_name
        app.state.data_agent_prompt = agent_prompt
        app.state.mcp_source = mcp_source
        app.state.memory_mode = memory_mode

        return JSONResponse(
            content={
                "message": f"{EQUATIONS_AGENT_NAME} created successfully.",
                "success": True
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error creating data agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create data agent: {e}"
        )


@config_router.get("/config")
async def get_data_agent_config(request: Request):
    """
    Get the configuration of the data agent.
    """
    try:
        app = request.app
        if EQUATIONS_AGENT_NAME not in app.state.agents:
            raise HTTPException(
                status_code=404, detail=f"{EQUATIONS_AGENT_NAME} not found.")

        # set config dictionary
        config = {
            "model_provider": app.state.model_provider,
            "model_name": app.state.model_name,
            "agent_name": EQUATIONS_AGENT_NAME,
            "agent_prompt": app.state.data_agent_prompt,
            "mcp_source": app.state.mcp_source,
            "memory_mode": app.state.memory_mode
        }
        return JSONResponse(
            content={
                "message": "Agent configuration retrieved successfully",
                "success": True,
                "data": config,
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error retrieving data agent config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve data agent config: {e}"
        )
