from pydantic import Field, BaseModel
from bson import ObjectId

class CreditCustomerEntity(BaseModel):
    customer : str = Field(...)
    total : float = Field(...)