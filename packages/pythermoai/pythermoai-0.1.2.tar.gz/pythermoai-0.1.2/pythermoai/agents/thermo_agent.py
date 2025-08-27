# import libs
import logging
from typing import (
    Dict,
    Union,
    List,
    Any,
    Optional
)
from pathlib import Path
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
# local
from ..models import stdioMCP, streamableHttpMCP
from .mcp_manager import MCPManager

# NOTE: logger
logger = logging.getLogger(__name__)

# SECTION: tools


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


class ThermoAgent:
    '''
    Thermo Agent class for creating and managing agents using langchain and langgraph.
    '''
    # NOTE: attributes
    # mcp lists
    _mcp_list = {}
    # agent prompt
    _agent_prompt = None
    # memory mode
    _memory_mode = False
    # agent name
    _agent_name = None
    # mcp stdio dict
    mcp_stdio_dict: Dict[str, Any] = {}
    # mcp streamable http dict
    mcp_streamable_http_dict: Dict[str, Any] = {}
    # client
    client: Optional[MultiServerMCPClient] = None

    def __init__(
        self,
        model_provider: str,
        model_name: str,
        agent_name: str,
        agent_prompt: str,
        mcp_source: Optional[
            Union[
            Dict[str, Dict[str, str]],
            Dict[str, Dict[str, str] | Dict[str, str]],
            Dict[str, Dict[str, str | List[str] | Dict[str, str]]],
            str,
            Path
            ]
        ] = None,
        memory_mode: bool = False,
        **kwargs
    ):
        '''
        Initialize the ThermoAgent with a model name and additional parameters.

        Parameters
        ----------
        model_provider : str
            The provider of the model (e.g., "openai", "google").
        model_name : str
            The name of the model to be used for the agent.
        agent_name : str
            The name of the agent.
        agent_prompt : str
            The prompt to be used for the agent.
        mcp_source : Dict[str, Dict[str, str]] | Dict[str, Dict[str, str | List[str]]], str, Path, optional
            A dictionary containing the MCP configurations or a path to a YAML file containing the MCP configurations.
        memory_mode : bool, optional
            Whether to enable memory mode for the agent.
        kwargs : dict
            Additional keyword arguments for future extensions.
        '''
        # NOTE: set attributes
        self._model_provider = model_provider
        self._model_name = model_name
        self._agent_name = agent_name
        self._agent_prompt = agent_prompt
        self._mcp_source = mcp_source
        self._memory_mode = memory_mode

        # NOTE: kwargs
        # temperature
        self._temperature = kwargs.get('temperature', 0.0)
        # max tokens
        self._max_tokens = kwargs.get('max_tokens', 2048)

        # SECTION: initialize LLM
        try:
            self.init_llm()
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise RuntimeError(f"Failed to initialize LLM: {e}") from e

        # SECTION: adapt MCP
        try:
            self.adapt_mcp()
        except Exception as e:
            logger.error(f"Failed to adapt MCP: {e}")
            raise RuntimeError(f"Failed to adapt MCP: {e}") from e

        # SECTION: create client
        try:
            self.create_client()
        except Exception as e:
            logger.error(f"Failed to create MCP client: {e}")
            raise RuntimeError(f"Failed to create MCP client: {e}") from e

    def init_llm(self):
        '''
        This method sets up the language model for the agent using the model name provided during initialization.
        It uses the `init_chat_model` function from langchain to create the model instance.
        '''
        try:
            # SECTION: initialize the LLM
            self.llm = init_chat_model(
                self._model_name,
                model_provider=self._model_provider,
                temperature=self._temperature,
                max_tokens=self._max_tokens
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise RuntimeError(f"Failed to initialize LLM: {e}") from e

    def adapt_mcp(self):
        '''
        This method adapts the MCP configurations based on the provided mcp_source.
        '''
        try:
            # SECTION: mcp setup
            if self._mcp_source:
                # NOTE: init MCPManager
                MCPManager_ = MCPManager(self._mcp_source)

                # NOTE: mcp config
                mcp_ = MCPManager_.config_mcp()

                # NOTE: convert to MCP dict for MultiServerMCPClient
                if isinstance(mcp_, dict):
                    # stdio mcp dict
                    self.mcp_stdio_dict = {
                        name: config.model_dump()
                        for name, config in mcp_.items()
                        if (
                            isinstance(config, stdioMCP) and
                            config.transport == 'stdio'
                        )
                    }

                    # streamable http mcp dict
                    self.mcp_streamable_http_dict = {
                        name: config.model_dump()
                        for name, config in mcp_.items()
                        if (
                            isinstance(config, streamableHttpMCP) and
                            config.transport == 'streamable_http'
                        )
                    }
        except Exception as e:
            logger.error(f"Failed to adapt MCP: {e}")
            raise RuntimeError(f"Failed to adapt MCP: {e}") from e

    def create_client(self):
        '''
        Create and return a MultiServerMCPClient instance with the MCP configurations.
        '''
        try:
            # log
            logger.info(
                "Creating MCP client with the provided configurations.")
            # a = self.mcp_stdio_dict
            # b = self.mcp_streamable_http_dict

            # SECTION: mcp feed
            # combine stdio and streamable http mcp dicts
            mcp_feed: Dict[str, Any] = {
                **self.mcp_stdio_dict,
                **self.mcp_streamable_http_dict
            }

            # SECTION: create MCP client
            # check if mcp is empty
            if not mcp_feed:
                self.client = None
                logger.warning(
                    "No valid MCP configurations found. Client will not be created.")
            else:
                self.client = MultiServerMCPClient(
                    mcp_feed
                )
                logger.info("MCP client created successfully.")

        except Exception as e:
            logger.error(f"Failed to create MCP client: {e}")
            raise RuntimeError(f"Failed to create MCP client: {e}") from e

    async def build_agent(self):
        '''
        build and return a langgraph agent using the initialized LLM and MCP client.
        '''
        try:
            # SECTION: client tools retrieval
            # check
            try:
                if self.client:
                    # get tools
                    tools = await self.client.get_tools()
                    # append custom tools
                    tools.extend([multiply, add])
                    # log
                    logger.info(
                        f"Retrieved {len(tools)} tools from MCP client and added custom tools.")
                else:
                    logger.warning(
                        "MCP client is not initialized. No tools will be available.")
                    tools = [multiply, add]
            except Exception as e:
                logger.error(f"Failed to retrieve tools from MCP client: {e}")
                tools = [multiply, add]

            # SECTION: memory saver
            try:
                if self._memory_mode:
                    memory = MemorySaver()
                else:
                    memory = None
            except Exception as e:
                logger.error(f"Failed to initialize memory saver: {e}")
                memory = None

            # SECTION: create agent
            try:
                agent = create_react_agent(
                    model=self.llm,
                    tools=tools,
                    prompt=self._agent_prompt,
                    checkpointer=memory
                )
            except Exception as e:
                logger.error(f"Failed to create agent: {e}")
                raise RuntimeError(f"Failed to create agent: {e}") from e

            # return agent
            return agent
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise RuntimeError(f"Failed to initialize agent: {e}") from e
