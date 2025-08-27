# import libs
import logging
from langchain.chat_models import init_chat_model
from typing import (
    Optional
)
# langchain
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models.base import BaseChatModel
# local
from ..config import llm_providers

# NOTE: logger
logger = logging.getLogger(__name__)


class LlmManager:
    """
    Manager class for LLM model initialization and utilities.
    """
    # NOTE: attributes
    # ping message to check model responsiveness
    system_message = SystemMessage(
        content="You are a helpful assistant. If someone pings you, respond with 'pong'.")
    # human message
    human_message = HumanMessage(content="ping")
    # ping messages
    ping_messages = [system_message, human_message]

    def __init__(
        self,
        model_provider: str,
        model_name: str, **kwargs
    ):
        # NOTE set attributes
        self.model_provider: str = model_provider
        self.model_name: str = model_name
        self.kwargs = kwargs
        self.model: Optional[BaseChatModel] = None

        # SECTION: initialize the model
        self.init()

    def init(self):
        """
        Initialize the chat model and store it in self.model.
        """
        try:
            self.model = LlmManager.initialize_model(
                model_provider=self.model_provider,
                model_name=self.model_name,
                **self.kwargs
            )
            logger.info(f"Model {self.model_name} initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise

    def ping(self) -> bool:
        """
        Ping the model to check if it is responsive.
        Returns True if responsive, False otherwise.
        """
        if self.model is None:
            logger.warning("Model not initialized.")
            return False
        try:
            # Simple test: invoke the model with a ping message
            response = self.model.invoke(self.ping_messages)

            # check if response contains 'pong'
            if "pong" not in response.content:
                logger.warning("Ping response did not contain 'pong'.")
                return False

            logger.info("Ping successful.")
            return True
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    def get_model(self):
        """
        Return the initialized model instance.
        """
        return self.model

    @staticmethod
    def initialize_model(
        model_provider: str,
        model_name: str,
        **kwargs
    ) -> BaseChatModel:
        """
        Initialize and return a chat model based on the specified model name.

        Parameters
        ----------
        model_company : str
            The company or provider of the model (e.g., "openai", "google", "anthropic").
        model_name : str
            The name of the model to be initialized.
        kwargs : dict
            Additional keyword arguments for future extensions.
            - temperature: float
                Controls the randomness of the model's responses.
            - max_tokens: int
                The maximum number of tokens for the model's response.

        Returns
        -------
        model: BaseChatModel
            The initialized chat model.
        """
        try:
            # SECTION: validate model provider
            if model_provider not in llm_providers:
                raise ValueError(
                    f"Invalid model provider: {model_provider}. Supported providers are: {llm_providers}")

            # SECTION: initialize model
            model: BaseChatModel = init_chat_model(
                model=model_name,
                model_provider=model_provider,
                **kwargs
            )
            return model
        except Exception as e:
            logger.error(
                f"Error initializing model {model_name} from {model_provider}: {e}")
            raise
