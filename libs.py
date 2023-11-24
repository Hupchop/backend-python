import requests
import base64
from bson import ObjectId
from app import db
import datetime
from constants import PAYMENT_URL, PAYMENT_API_KEY, PAYMENT_SECRET_KEY
from database import customer_collection

# Get Payment Access Token  
async def getPaymentAccessToken():

    auth_string = PAYMENT_API_KEY + ":" + PAYMENT_SECRET_KEY
    auth_string_byte = auth_string.encode("ascii")
    base64_bytes = base64.b64encode(auth_string_byte)
    base64_string = base64_bytes.decode("ascii")

    auth = requests.post(
        url=PAYMENT_URL + '/api/v1/auth/login',
        json={},
        headers={
            "Authorization" : "Basic " + base64_string
        }
    )

    response = auth.json()
    auth.close()
    return response['responseBody']['accessToken']


# Generate Tracking Number
async def generateTrackingNumber(reference : str):
    head = 'HC'
    ref = reference[0:5].upper()
    return head + ref


# Credit customer wallet
async def creditCustomerWallet(amount : float, customer : ObjectId) -> str :

    # get customer
    customer_data = await customer_collection.find_one({
        "_id" : customer
    })

    message = 'Could not fund wallet'

    # record exists
    if customer_data != None:
        
        walletBalance = customer_data['wallet'] + amount

        # update customer 
        await customer_collection.update_one(
            filter={"_id" : customer},
            update={"$set" : {
                "wallet" : walletBalance,
                "date_updated" : datetime.datetime.now()
            }}
        )

        message = 'Your wallet has been funded successfully'

    # return 
    return message

