from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from .common_schema import BaseFieldSchema, ValidationRules, FieldType

class Validation(ValidationRules):
    unique: Optional[bool] = Field(default=False)
    index: Optional[bool] = Field(default=False)

    
class FieldSchema(BaseFieldSchema):
    is_protected: bool = Field(default=False)
    entity_id: str
    description: Optional[str] = None
    validations: Optional[Validation] = None

    @model_validator(mode='after')
    def validate_options_sources(self) -> 'FieldSchema':
        if self.type in [FieldType.DROPDOWN, FieldType.CHECKBOX, FieldType.RADIO]:
            if not self.options and not (self.endpoint_url and self.reference):
                raise ValueError(f"For '{self.type}' type, either 'options' or both 'endpoint_url' and 'reference' must be provided.")
            if self.options and len(self.options) < 2:
                raise ValueError(f"For '{self.type}' type, 'options' must contain at least 2 items.")
        return self

    model_config = ConfigDict(extra="ignore")
        
