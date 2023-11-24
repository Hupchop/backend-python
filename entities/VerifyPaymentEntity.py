from pydantic import Field, BaseModel

class VerifyPaymentEntity(BaseModel):
    reference : str = Field(min_length=8)
    paymentReference : str = Field(min_length=8)