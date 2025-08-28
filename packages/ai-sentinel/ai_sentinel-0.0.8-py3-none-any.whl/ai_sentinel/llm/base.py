from abc import ABC, abstractmethod
from typing import Optional

from ai_sentinel.core.models import LLMResponse

class BaseLLMClient(ABC):
    '''
    Abstract Base Class for LLM Clients
    '''
    def __init__(self, api_key: str, model: str, timeout: Optional[float] = 30.0, **kwargs):
        # validate inputs early - fail fast principle
        if not api_key or not isinstance(api_key, str):
            raise ValueError('API key must be a non-empty string')
        if not model or not isinstance(model, str):
            raise ValueError('Model must be a non-empty string')
        if timeout <= 0:
            raise ValueError('Timeout must be positive')

        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.kwargs = kwargs

    @abstractmethod
    async def generate_text_async(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        context: Optional[list[dict[str,str]]] = None,
        temperature: Optional[float] = 0.7,
        **kwargs
    ) -> LLMResponse:
        '''
        Generate a response from LLM based on the prompt and optional inputs (async).

        Warning: Implementations uses deprecated function "datetime.utcnow()"
        
        Parameters:
        prompt (str): User input
        system_prompt (Optional[str]): System prompt to give the LLM as it's role | default = None 
        context (Optional[list[dict[str,str]]]): Conversation history | default = None
        temperature (Optional[float]): What sampling temperature to use | default = 0.7
        **kwargs: Handles structured output ( ex. {'response_format': [Some Structure]} )

        '''
        pass

    def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        context: Optional[list[dict[str,str]]] = None,
        temperature: Optional[float] = 0.7,
        **kwargs
    ) -> LLMResponse:
        '''
        Generate a response from LLM based on the prompt and optional inputs (sync wrapper).
        
        This is a synchronous wrapper around the async method that is safe to run
        in any environment, including Jupyter notebooks.
        '''
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def run_async_in_thread():
            return asyncio.run(self.generate_text_async(prompt, system_prompt, context, temperature, **kwargs))

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_async_in_thread)
            return future.result()

    @abstractmethod
    async def validate_async(self) -> bool:
        '''
        Validate the provided API key by making a call to the provider (async).
        Return True if the API key is valid, False if not.
        '''
        pass

    def validate(self) -> bool:
        '''
        Validate the provided API key by making a call to the provider (sync wrapper).
        '''
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def run_async_in_thread():
            return asyncio.run(self.validate_async())

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_async_in_thread)
            return future.result()

    @property
    @abstractmethod
    def provider_name(self) -> str:
        '''Get the provider name'''
        pass

    @property
    def info(self) -> dict:
        '''Return clean information about the LLM Client configuration.'''
        return {
            'provider': self.provider_name,
            'model': self.model,
            'timeout': self.timeout,
            'extra_args': self.kwargs
        }