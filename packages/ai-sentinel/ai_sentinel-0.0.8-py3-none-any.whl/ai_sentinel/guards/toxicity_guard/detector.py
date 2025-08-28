# where all the stuff will happen
import json

from ai_sentinel.llm.base import BaseLLMClient
from ai_sentinel.core.models import LLMResponse
from ai_sentinel.guards.toxicity_guard.models import ToxicityResult
from ai_sentinel.guards.toxicity_guard.prompts import SYSTEM_PROMPT


class ToxicityGuard:
    '''Toxicity Guard implementation for input'''
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client: BaseLLMClient = llm_client 
        self.system_prompt: str = SYSTEM_PROMPT

    async def analyze_async(self, text: str) -> ToxicityResult: 
        '''
        Analyze the toxicity in the user input using LLM-as-a-judge (async)
        Return the finished evaluation as a ToxicityResult object
        '''
        response: LLMResponse = await self.llm_client.generate_text_async(text, self.system_prompt, **self._structure_output())
        toxicity_response: dict = json.loads(response.content)

        result = ToxicityResult(**toxicity_response)
        return result

    def analyze(self, text: str) -> ToxicityResult: 
        '''
        Analyze the toxicness in the user input using LLM-as-a-judge (sync wrapper)
        Return the finished evaluation as a ToxicityResult object
        '''
        response: LLMResponse = self.llm_client.generate_text(text, self.system_prompt, **self._structure_output())
        toxicity_response: dict = json.loads(response.content)

        result = ToxicityResult(**toxicity_response)
        return result

    def _structure_output(self) -> dict:
        '''Return the nessessary args to generate structured output for the specific LLM client'''
        provider: str = self.llm_client.provider_name
        response_format: dict = {}
        if 'gemini' in provider:
            response_format = {
                'response_type': 'application/json',
                'response_schema': ToxicityResult
            }
        elif 'openai' in provider:
            response_format = {
                'response_format': ToxicityResult
            }

        return response_format
