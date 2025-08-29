
from pydantic import (
    BaseModel, 
    BeforeValidator, 
    Field, 
    model_validator
)
from typing import (
    Annotated, 
    Any, 
    Optional, 
    Self
)
from enum import Enum


class ToxicityCategories(str, Enum):
    '''Specify Toxicity Categories'''

    HATE_SPEECH = 'hate_speech'
    HARASSMENT = 'harassment'
    THREATS = 'threats'
    SEXUAL_CONTENT = 'sexual_content'
    SELF_HARM = 'self_harm'
    VIOLENCE = 'violence'
    BULLYING = 'bullying'
    DISCRIMINATION = 'discrimination'    

class ToxicityScore(str, Enum):
    '''Toxicity severity levels'''

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

def _ensure_categories_type(value: Any) -> ToxicityCategories:
    '''Modify {value} to ensure it meets type requirements'''
    categories: list = []
    result: list = []
    # make value a list
    if not isinstance(value, list):  
        categories = [value]
    else:
        categories = value

    # loop through the list of values
    for entry in categories:
        if not isinstance(entry, ToxicityCategories):
            if isinstance(entry, str):
                entry: str = entry.upper().strip()
            result.append(getattr(ToxicityCategories, entry))
        else:
            result.append(entry)
    return result

class ToxicityResult(BaseModel):
    '''Structured output from LLM toxicity assessment'''
    
    is_toxic: bool = Field(description='assessment of whether the content is toxic')
    confidence: float = Field(
        ge=0.0, 
        le=1.0, 
        description='confidence that the text is toxic (0.0-1.0)'
    )
    categories: Annotated[list[ToxicityCategories], BeforeValidator(_ensure_categories_type)] = Field(
        default_factory=list, 
        description='list of toxic categories detected in content'
    )
    reason: str = Field(description='explanation of the assessment')
    score: Optional[ToxicityScore] = Field(
        default=None,
        description='Simplified confidence score (low, medium, high)'
        )

    @model_validator(mode='after')
    def assign_score(self) -> Self:
        '''Assign the instances score variable'''
        expected_score: ToxicityScore = None
        if self.confidence > 0.7:
            expected_score = ToxicityScore.HIGH
        elif self.confidence <= 0.3:
            expected_score = ToxicityScore.LOW
        else:
            expected_score = ToxicityScore.MEDIUM
        
        self.score = expected_score
        return self