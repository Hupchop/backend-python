from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from data.validators.validator import PyObjectId
from bson import ObjectId
import constants

class TransactionsModel(BaseModel) :

    id : Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    reference : str = Field(...)
    quantity : int = Field(default=1)
    price : float = Field(default=0)
    total : float = Field(default=0)
    status : str = Field(default=constants.PAYMENT_PENDING)
    seller : str = Field(default="")
    customer : ObjectId = Field(...)
    itemid : str = Field(default="")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )