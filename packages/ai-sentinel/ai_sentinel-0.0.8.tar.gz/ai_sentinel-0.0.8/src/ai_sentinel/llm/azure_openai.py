from typing import Optional, Any

from openai import AzureOpenAI, AuthenticationError
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion

from ai_sentinel.llm.base import BaseLLMClient
from ai_sentinel.core.models import LLMResponse

class AzureOpenAIClient(BaseLLMClient):
    '''Client implementation for Azure OpenAI LLM'''

    def __init__(
            self, 
            api_key: str, 
            model: str, 
            api_version: str,
            azure_endpoint: str,
            timeout: Optional[float] = 30.0, 
            **kwargs
        ):
        super().__init__(api_key, model, timeout, **kwargs)

        if not api_version or not isinstance(api_version, str):
            raise ValueError('API version must be a non-empty string')
        if not azure_endpoint or not isinstance(azure_endpoint, str):
            raise ValueError('Azure Endpoint must be a non-empty string')
        
        self.api_version = api_version
        self.azure_endpoint = azure_endpoint

        self.client = AzureOpenAI( # create instance of azure open ai 
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
            timeout=self.timeout
        )

    async def generate_text_async(
            self, 
            prompt: str, 
            system_prompt: Optional[str] = None, 
            context: Optional[list[dict[str,str]]] = None,
            temperature: Optional[float] = 0.0,
            **kwargs # supply response format in kwargs
        ) -> LLMResponse:
        
        if not prompt or not isinstance(prompt, str):
            raise ValueError('Prompt must be a non-empty string')
        
        response_format: Optional[Any] = kwargs.get('response_format')

        message: list = []
        response = None

        # check if there is a system prompt given
        if system_prompt:
            message.append({
                'role': 'system',
                'content': system_prompt
            })
        # check if there is context given
        if context:
            message.extend(context)

        message.append({
            'role': 'user',
            'content': prompt
        })

        if response_format:
            # use parse instead of create bc using structured output 
            response: ParsedChatCompletion = self.client.chat.completions.parse(
                model=self.model,
                messages=message,
                temperature=temperature,
                response_format=response_format
            )
        else:
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model,
                messages=message,
                temperature=temperature
            )
        formatted_response: LLMResponse = self._format_llm_response(response)
        return formatted_response
    
    def _format_llm_response(self, response: ChatCompletion | ParsedChatCompletion) -> LLMResponse:
        '''Convert response to built in Model type to a response type of LLMResponse'''

        output: LLMResponse = LLMResponse(
            content=response.choices[0].message.content,
            model= self.model
        )
        output.usage = {
            'model_tokens': response.usage.completion_tokens,
            'prompt_tokens': response.usage.prompt_tokens,
            'total_tokens': response.usage.total_tokens,
        }

        output.response_time_ms = output.timestamp.timestamp() - response.created
        output.finish_reason = response.choices[0].finish_reason
        return output


    async def validate_async(self) -> bool:
        # make a simple API call
        try:
            self.client.models.list()
            # if call is successful then the key is valid
            return True
        except AuthenticationError as e: # should I be catching these errors?
            print(f'API key is invalid: {e}')
            return False
        except Exception as e:
            print(f'An unexpected error occurred during API key validation: {e}')
            return False

    @property
    def provider_name(self) -> str:
        return "azure_openai"
    
    @property
    def info(self):
        basic_info = super().info
        basic_info['api_version'] = self.api_version
        basic_info['azure_endpoint'] = self.azure_endpoint
        
        # print(f'API Version: {self.api_version}')
        # print(f'Azure Endpoint: {self.azure_endpoint}')
        return basic_info
