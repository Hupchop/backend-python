from pydantic import Field, BaseModel

class WalletTransactionEntity(BaseModel):
    phone : str = Field(...);
    amount : float = Field(...);
    channel : str = Field(...);
    method : str = Field(...);