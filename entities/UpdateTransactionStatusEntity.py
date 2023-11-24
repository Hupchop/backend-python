from pydantic import BaseModel, Field


class UpdateTransactionStatusEntity(BaseModel):
    reference : str = Field(...)
    status : str = Field(...)