from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from bson import ObjectId
from data.validators.validator import PyObjectId

# Submit a review
class SubmitReviewEntity(BaseModel):
    id : str = Field(...)
    customer_phone : str = Field(...)
    customer_name : str = Field(...)
    rating : int = Field(default=1)
    review_title : Optional[str] = Field(default="")
    review_type : str = Field(...)
    review_text : Optional[str] = Field(default="")


# Review was helpgul
class UpdateReviewActivity(BaseModel):
    id : str = Field(...)

# Cart Item
class CartItems(BaseModel):
    itemid : str = Field(...)
    quantity : int = Field(default=1)
    price : float = Field(...)
    total : float = Field(...)
    reference : Optional[str] = Field(default="")
    status : Optional[str] = Field(default="")
    seller : Optional[str] = Field(default="")
    customer : Optional[PyObjectId] = Field(default_factory=PyObjectId)

# Create transaction
class CreateTransactionEntity(BaseModel):
    phone : str = Field(...)
    delivery : float = Field(...)
    processingFee : float = Field(...) 
    order_note : str = Field(default="")
    subTotal : float = Field(...)
    data : List[CartItems] = Field(...)
    channel : str = Field(default='web')
    delivery_info : Dict = Field(default={})
    method : str = Field(...)
    seller : str = Field(...)
    channel : str = Field(...)


# Place order from wallet
class PlaceOrderFromWalletEntity(BaseModel):
    reference : str = Field(...)

# Suggest food
class SuggestFoodEntity(BaseModel):
    food : str = Field(...)
    vendor_name : str = Field(...)
    vendor_contact_number : str = Field(...)
    about_food : str = Field(...)
    vendor_contact_address : Dict = Field(...)


# Suggest restaurant
class SuggestRestaurantEntity(BaseModel):
    about_vendor : str = Field(...)
    vendor_name : str = Field(...)
    vendor_contact_number : str = Field(...)
    vendor_contact_address : Dict = Field(...)