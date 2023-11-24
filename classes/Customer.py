from database import customer_collection

class Customer:

    async def createCustomer(self, name : str, phone : str):
        customer = customer_collection.find_one(
            filter={"phone" : phone}
        )

        # customer exists
        if customer == None:
            ...