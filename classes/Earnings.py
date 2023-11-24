from pydantic import BaseModel
from database import earnings_collection
from interfaces.TransactionInterface import TransactionInterface
import datetime 

# This credits hupchop balance
class CreditHupchop():

    async def Save(self, transaction : TransactionInterface):
        earnings = await earnings_collection.find_one({"account" : "hupchop"})

        earning = transaction.platform_fee
        delivery = transaction.delivery_commision

        if isinstance(earnings, dict):
            earning += earnings['earnings']
            delivery += earnings['delivery']

        # update earnings
        await earnings_collection.update_one(
            filter={"_id" : earnings['_id']},
            update={"$set" : {
                "earnings" : (earning - transaction.delivery_commision),
                "delivery" : delivery,
                "last_updated" : datetime.datetime.now()
            }},
            upsert=True
        )

        # credit preccessor
        await CreditProcessor.Save()


# This credits the global vendor balance
class CreditVendor():

    async def Save(self, transaction : TransactionInterface):
        amount = transaction.amount_settled - transaction.delivery
        delivery = transaction.delivery

        # credit global vendor account
        globalVendor = earnings_collection.find_one({
            "account" : "global_vendor"
        })

        # global earnings vars
        global_earning = amount
        global_delivery = delivery

        # update values
        if isinstance(globalVendor, dict):
            global_earning += globalVendor['earnings']
            global_delivery += globalVendor['delivery']

        # update record
        await earnings_collection.update_one(
            filter={"_id" : globalVendor['_id']},
            update={"$set" : {
                "earnings" : round(global_earning, 2),
                "delivery" : round(global_delivery, 2),
                "last_updated" : datetime.datetime.now()
            }},
            upsert=True
        )

        # TODO: credit the vendor that owns this transaction


# This credits the processor balance
class CreditProcessor():

    async def Save(self, transaction : TransactionInterface):
        earnings = await earnings_collection.find_one({"account" : transaction.processor})

        earning = transaction.app_fee

        if isinstance(earnings, dict):
            earning += earnings['earnings']

        # update record
        await earnings_collection.update_one(
            filter={"_id" : earnings['_id']},
            update={"$set" : {
                "earnings" : round(earning, 2),
                "last_updated" : datetime.datetime.now()
            }},
            upsert=True
        )

