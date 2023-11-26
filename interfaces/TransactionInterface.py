from pydantic import BaseModel

class TransactionInterface(BaseModel):
    app_fee : float = 0
    amount_settled : float = 0
    reference : str  = ""
    platform_fee : float = 0
    delivery : int = 0
    delivery_commision : float = 0
    processor : str = ""
    trackingNumber : str = ""