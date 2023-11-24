from app import db
import datetime
from classes import Earnings, Orders
from interfaces.TransactionInterface import TransactionInterface
import libs
# import database
from database import transaction_summary_collection, transaction_collection

class TransactionSuccessful(TransactionInterface):

    # Save transaction
    async def Save(self):

        # get summary
        summary = await transaction_summary_collection.find_one({
            "reference" : self.reference
        })

        if summary == None:
            return False
        
        # continue
        self.platform_fee = float(summary['processingFee'])

        # check delivery
        if summary['delivery'] != 0:

            # set commission
            inPercentage = (summary['delivery'] * 10) / 100

            # percentage higher
            if inPercentage > deliveryCommission :
                deliveryCommission = inPercentage;

            # deduct delivery
            summary['delivery'] -= deliveryCommission;

            # set the new delivery fee
            self.delivery = summary['delivery'];

            # add to platform fee
            self.platform_fee += deliveryCommission;

            # set delivery commission
            self.delivery_commision = deliveryCommission;

        # deduct platform fee
        self.amount_settled -= self.platform_fee;

        # generate tracking number
        self.trackingNumber = summary['tracking_number'] if summary['tracking_number'] != "" else libs.generateTrackingNumber(self.reference)

        # update transaction summary
        await transaction_summary_collection.find_one_and_update(
            filter={"reference" : self.reference},
            update={"$set" : {
                "delivery" : summary['delivery'],
                "platform_fee" : self.platform_fee,
                "payment_fee" : self.app_fee,
                "settlement_to_vendor" : self.amount_settled,
                "processingFee" : 0,
                "status" : "success",
                "tracking_number" : self.trackingNumber,
                "date_updated" : datetime.datetime.now()
            }} 
        )

        # wallet funding?
        if str(self.trackingNumber).upper() == 'WALLET':
            return await libs.creditCustomerWallet(summary['total'], summary['customer'])
        
        # status
        status = 'awaiting delivery' if summary['delivery'] != 0 else 'processing'

        # update transactions with same ref
        await transaction_collection.update_many(
            filter={"reference" : self.reference},
            update={"$set" : {
                "status" : status
            }}
        )

        # Credit hupchop
        Earnings.CreditHupchop().Save(transaction=self)

        # Credit vendor
        Earnings.CreditVendor().Save(transaction=self)

        # send notification to customer
        Orders.OrderPlacedCustomer().Save(transaction=self)

        # send notification to vendor
        Orders.OrderPlacedVendor().Save(transaction=self)

        # All good
        return "Your order has been placed with the tracking number " + self.trackingNumber +". You will be contacted shortly. Please take note of the tracking number."
    


# This updates a transaction status
class TransactionStatus:

    reference : str 
    status : str 

    def __init__(self, reference, status) -> None:
        self.reference = reference
        self.status = status

    async def Update(self):

        filter = {"reference" : self.reference}
        update = {"status" : self.status}

        await transaction_summary_collection.update_one(
            filter=filter,
            update={"$set" : update}
        )

        # update transactions
        await transaction_collection.update_many(
            filter=filter,
            update={"$set" : update}
        )


...