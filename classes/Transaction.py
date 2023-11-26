from app import db
import datetime
from classes import Earnings, Orders
from interfaces.TransactionInterface import TransactionInterface
import libs
# import database
from database import transaction_summary_collection, transaction_collection

class TransactionSuccessful(TransactionInterface):        

    # Save transaction
    async def Save(self, request : TransactionInterface):

        # get summary
        summary = await transaction_summary_collection.find_one({
            "reference" : request.reference
        })

        if summary == None:
            return False
        
        # continue
        request.platform_fee = float(summary['processingFee'])

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
            request.delivery = summary['delivery'];

            # add to platform fee
            request.platform_fee += deliveryCommission;

            # set delivery commission
            request.delivery_commision = deliveryCommission;

        # deduct platform fee
        request.amount_settled -= request.platform_fee;

        # generate tracking number
        request.trackingNumber = summary['tracking_number'] if summary['tracking_number'] != "" else libs.generateTrackingNumber(request.reference)

        # update transaction summary
        update = await transaction_summary_collection.update_one(
            filter={"reference" : request.reference},
            update={"$set" : {
                "delivery" : summary['delivery'],
                "platform_fee" : request.platform_fee,
                "payment_fee" : request.app_fee,
                "settlement_to_vendor" : request.amount_settled,
                "processingFee" : 0,
                "status" : "success",
                "tracking_number" : request.trackingNumber,
                "date_updated" : datetime.datetime.now()
            }} 
        )

        # wallet funding?
        if str(request.trackingNumber).upper() == 'WALLET':
            return await libs.creditCustomerWallet(summary['total'], summary['customer'])
        
        # status
        status = 'awaiting delivery' if summary['delivery'] != 0 else 'processing'

        # update transactions with same ref
        await transaction_collection.update_many(
            filter={"reference" : request.reference},
            update={"$set" : {
                "status" : status
            }}
        )

        if str(request.trackingNumber).upper() != 'WALLET':

            # Credit hupchop
            await Earnings.CreditHupchop().Save(transaction=request)

            # Credit vendor
            await Earnings.CreditVendor().Save(transaction=request)

            # send notification to customer
            await Orders.OrderPlacedCustomer().Save(transaction=request)

            # send notification to vendor
            await Orders.OrderPlacedVendor().Save(transaction=request)

        # All good
        return "Your order has been placed with the tracking number " + request.trackingNumber +". You will be contacted shortly. Please take note of the tracking number."
    


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