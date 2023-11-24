# import database
from classes import Messaging
from database import transaction_summary_collection, transaction_collection, customer_collection
from interfaces.TransactionInterface import TransactionInterface

# Order placed for customer
class OrderPlacedCustomer:

    async def Save(self, transaction : TransactionInterface):
        transaction_summary = await transaction_summary_collection.find_one(
            filter={"reference" : transaction.reference}
        )

        # get customer
        customer = await customer_collection.find_one(
            filter={"_id" : transaction_summary['customer']}
        )

        # has delivery
        hasDelivery = True if transaction_summary['delivery'] > 0 else False

        # set message
        deliveryMessage = 'You will be notified when your order is ready for delivery.' if hasDelivery == True else 'You will be notified when your order is ready for pickup.'

        # build message
        message = "Thank you for choosing Hupchop. This is your order tracking number "+transaction.trackingNumber+". " + deliveryMessage

        # send message
        await Messaging.SmsMessaging(
            message=message,
            phone=customer['phone']
        ).Send()


# Order placed for vendor
class OrderPlacedVendor:

    async def Save(self, transaction : TransactionInterface):

        pass