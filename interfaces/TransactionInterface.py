class TransactionInterface:
    app_fee : float 
    amount_settled : float
    reference : str 
    platform_fee : float = 0
    delivery : int = 0
    delivery_commision : float = 0
    processor : str
    trackingNumber : str