from typing import Optional, Any
from datetime import datetime

from google import genai
from google.genai import types, errors

from ai_sentinel.llm.base import BaseLLMClient
from ai_sentinel.core.models import LLMResponse

class GeminiClient(BaseLLMClient):
    '''Client implementation for Google Gemini LLM'''

    def __init__(
            self, 
            api_key: str, 
            model: str, 
            timeout: Optional[float] = 30.0, 
            **kwargs
        ):
        super().__init__(api_key, model, timeout, **kwargs)

        self.client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=timeout*1000)) 
            
    async def generate_text_async(
            self, 
            prompt: str, 
            system_prompt: Optional[str] = None, 
            context: Optional[list[dict[str,str]]] = None,
            temperature: Optional[float] = None,
            **kwargs # supply response format in kwargs
        ) -> LLMResponse:
        
        if not prompt or not isinstance(prompt, str):
            raise ValueError('Prompt must be a non-empty string')
        
        
        response_type: Optional[str] = kwargs.get('response_type')
        response_schema: Optional[Any] = kwargs.get('response_schema')
        if (not response_schema) ^ (not response_type): # ^ stands for xor operator
            raise ValueError('Response Schema and Response Type must both be passed if one is present')

        message: list = []
        config = None

        # check if there is a system prompt given
        if system_prompt or temperature or response_schema:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                response_mime_type=response_type,
                response_schema=response_schema,
            )
            
        # check if there is context (aka. history) given
        if context:
            message.extend(context)

        message.append(
            types.Content(
                role='user',
                parts=[types.Part.from_text(text=prompt)]
            )
        )

        response_start_time: datetime = datetime.utcnow()
        response: types.GenerateContentResponse = self.client.models.generate_content( # returns 
            model=self.model,
            config=config,
            contents=message,
        )
        if not response.create_time: # gemini keeps not returning shit
            response.create_time = response_start_time

        formatted_response: LLMResponse = self._format_llm_response(response)
        return formatted_response
    
    def _format_llm_response(self, response: types.GenerateContentResponse) -> LLMResponse:
        '''Convert response to built in Model type to a response type of LLMResponse'''
        output: LLMResponse = LLMResponse(
            content=response.text,
            model = response.model_version
        )
        output.usage = {
            'model_tokens': response.usage_metadata.candidates_token_count,
            'prompt_tokens': response.usage_metadata.prompt_token_count,
            'total_tokens': response.usage_metadata.total_token_count,
        }
        if response.create_time:
            output.response_time_ms = output.timestamp.timestamp() - response.create_time.timestamp()
        else:
            output.response_time_ms = 0.0
        output.finish_reason = response.candidates[0].finish_reason.name
        return output
    
    async def validate_async(self) -> bool:
        # make a simple API call
        try:
            self.client.models.list()
            return True
        except errors.APIError as e: # should I be catching these errors?
            print(f'API key is invalid or general Gemini API Error occured: {e}')
            return False
        except Exception as e: 
            print(f'An unexpected error occurred during API key validation: {e}')
            return False

    @property
    def provider_name(self) -> str:
        return 'google_gemini'
    
    @property
    def info(self):
        return super().info
