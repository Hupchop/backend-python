from pydantic import Field, BaseModel

class GeneratePaymentLinkEntity(BaseModel):
    customer : str = Field(...)
    redirect : str = Field(...)
    reference : str = Field(...)