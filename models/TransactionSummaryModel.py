from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import datetime
from data.validators.validator import PyObjectId
from bson import ObjectId
from constants import NOT_PAID, WALLET_FUNDING, WALLET_TRACKING_IDENTIFIER

class TransactionSummaryModel(BaseModel):

    id : Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    reference : str = Field(...)
    customer : ObjectId = Field(...)
    subTotal : float = Field(...)
    delivery : int = Field(default=0)
    processingFee : float = Field(default=0)
    total : float = Field(default=0)
    status : str = Field(default=NOT_PAID)
    items : int = Field(default=0)
    channel : str = Field(...)
    method : str = Field(...)
    note : str = Field(default=WALLET_FUNDING)
    delivery_info : str = Field(default="")
    tracking_number : str = Field(default=WALLET_TRACKING_IDENTIFIER)
    date_created : datetime.datetime = datetime.datetime.now()
    date_updated : Optional[datetime.datetime] = Field(default=None)
    payment_fee : Optional[float] = Field(default=0)
    platform_fee : Optional[float] = Field(default=0)
    settlement_to_vendor : Optional[float] = Field(default=0)
    tracking_number : Optional[str] = Field(default="")
    transaction_reference : str = Field(default="")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
