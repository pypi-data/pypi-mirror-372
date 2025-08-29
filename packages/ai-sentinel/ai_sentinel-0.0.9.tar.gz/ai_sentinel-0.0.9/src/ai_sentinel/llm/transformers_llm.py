import json
import jsonschema
import re

from typing import Optional, Any
from datetime import datetime

from transformers import AutoTokenizer, AutoModelForCausalLM

from ai_sentinel.llm.base import BaseLLMClient
from ai_sentinel.core.models import LLMResponse
from ai_sentinel.guards.toxicity_guard import ToxicityResult

class TransformersClient(BaseLLMClient):
    '''Open Source LLM client implementation using Transformers framework from Huggingface'''

    def __init__(
            self, 
            model: str,
            api_key: Optional[str] = 'EMPTY',
            timeout: Optional[float] = 30.0, 
            **kwargs
        ):
        super().__init__(api_key, model, timeout, **kwargs)

        self.tokenizer = AutoTokenizer.from_pretrained(self.model)
        self.client = AutoModelForCausalLM.from_pretrained(self.model)

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
        
        message = []

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

        inputs = self.tokenizer.apply_chat_template(
            message,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            temperature=temperature
        ).to(self.client.device)

        response_start_time: datetime = datetime.utcnow()
        response = self.client.generate(**inputs, max_new_tokens=512)
        response = self.tokenizer.decode(response[0][inputs["input_ids"].shape[-1]:])
        response_end_time: datetime = datetime.utcnow()

        formatted_response: LLMResponse = self._format_llm_response(response, response_start_time, response_end_time)
        return formatted_response

    def _clean_response(self, response) -> str:
        cleaned = response.strip('```')
        cleaned = re.sub(r'<.*?>', '', cleaned)

        dict_start_idx = response.find('{')
        dict_end_idx = response[dict_start_idx:].find('}')
        if dict_start_idx == -1 or dict_end_idx == -1:
            raise ValueError('LLM response does not contain a dictionary/json-compatible object')
        return cleaned

    def _format_llm_response(self, response, start_time: datetime, end_time: datetime) -> LLMResponse:
        '''Convert response to built in Model type to a response type of LLMResponse'''
        
        cleaned_response = self._clean_response(response)
        toxicity_schema = ToxicityResult.model_json_schema()

        try:
            response_dict = json.loads(cleaned_response)
            jsonschema.validate(instance=response_dict, schema=toxicity_schema)
        except jsonschema.ValidationError as e:
            print(f"Validation Error: {e.message}")
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e.message}")

        output: LLMResponse = LLMResponse(
            content=json.dumps(response_dict),
            model = self.model,
            response_time_ms = start_time.timestamp() - end_time.timestamp()
        )
        return output

    async def validate_async(self):
        try:
            self.client.models.list()
            return True
        except Exception as e: 
            print(f'An unexpected error occurred during API key validation: {e}')
            return False
    
    def provider_name(self):
        return 'transformers'