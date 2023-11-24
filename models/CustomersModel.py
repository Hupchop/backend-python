from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from data.validators.validator import PyObjectId
import datetime

# Model for customers
class CustomerModel(BaseModel):

    id : Optional[PyObjectId] = Field(alias='_id', default=None)
    fullname : str = Field(...)
    email : Optional[str] = None
    country : Optional[str] = None
    phone : str = Field(...)
    wallet : Optional[float] = None
    OTP : Optional[int] = None
    expire_otp : Optional[int] = None 
    otp_verified : Optional[bool] = False
    password : Optional[str] = None
    otp_log : Optional[dict] = None
    date_updated : Optional[datetime.datetime] = None


# Collection for customers
class CustomerCollection(BaseModel) :

    customers : List[CustomerModel]