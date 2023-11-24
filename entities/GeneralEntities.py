from pydantic import BaseModel, Field


# Submit a review
class SubmitReviewEntity(BaseModel):
    id : str = Field(...)
    customer_phone : str = Field(...)
    customer_name : str = Field(...)
    rating : str = Field(...)
    review_title : str = Field(...)
    review_type : str = Field(...)
    review_text : str = Field(...)


# Review was helpgul
class UpdateReviewActivity(BaseModel):
    id : str = Field(...)


