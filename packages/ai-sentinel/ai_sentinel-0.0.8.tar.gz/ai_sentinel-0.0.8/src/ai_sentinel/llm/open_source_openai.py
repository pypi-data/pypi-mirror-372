from typing import Optional, Any

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion

from ai_sentinel.llm.base import BaseLLMClient
from ai_sentinel.core.models import LLMResponse

class OpenAIClient(BaseLLMClient):
    '''
    Client implementation for Open Source LLM using a local server 
    that offers compatibility with the OpenAI SDK
    '''

    def __init__(
            self,
            base_url: str,  
            model: str,
            api_key: Optional[str] = 'EMPTY', # no auth by default
            timeout: Optional[float] = 30.0, 
            **kwargs
        ):
        super().__init__(api_key, model, timeout, **kwargs)

        if not base_url or not isinstance(base_url, str):
            raise ValueError('Base URL must be a non-empty string')
        
        self.base_url = base_url
        
        self.client = OpenAI( # create instance of open ai 
            base_url=self.base_url,
            api_key=self.api_key,
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
        
        # check if there is any context given
        if context:
            message.extend(context)
        
        # finally add the user prompt
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
            content= response.choices[0].message.content,
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
        
        except Exception as e:
            print(f'An unexpected error occurred in creating a sever connection: {e}')
            return False
        
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def info(self):
        basic_info = super().info
        basic_info['base_url'] = self.base_url
        
        return basic_info