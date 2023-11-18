from pydantic import Field, BaseModel

class VerifyPasswordEntity(BaseModel):
    phone : str = Field(...)
    password : str = Field(...)