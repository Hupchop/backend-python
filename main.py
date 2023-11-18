import uvicorn
from typing import Union
import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app import db, client, success, failed, format_number
from fastapi.responses import JSONResponse
# from controllers import CustomersController
from models import CustomersModel

# entities
from entities.VerifyPasswordEntity import VerifyPasswordEntity
from entities.WalletTransaction import WalletTransactionEntity

app = FastAPI()

# Middleware for CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# collections
customer_collection = db.get_collection('customers')

# start application
if __name__ == '__main__':
    uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv("PORT")), reload=True)

"""
    APP ROUTES
"""
# Get all customers
@app.get(
        "/customers",
        response_description="Showing all customers",
        status_code=status.HTTP_200_OK,
        response_model=CustomersModel.CustomerCollection)
async def getAllCustomers():
    return CustomersModel.CustomerCollection(customers=await customer_collection.find().to_list(1000))


# Try verify password
@app.post(
    '/verify/password',
    status_code=status.HTTP_200_OK,
    response_description="Verify Password"
    )
async def verifyPassword(request : VerifyPasswordEntity = Body(...)):
    phoneFormatted = format_number(request.phone)
    return {"phone" : request.phone}


# Check phone number
@app.get(
    '/customer/check-phone-number/{phone}',
    # response_model=CustomersModel.CustomerModel,
    response_description="Checking customer phone number")
async def checkCustomerPhone(phone : str) :
    phoneFormatted = format_number(phone)
    customer = await customer_collection.find_one({'phone' : phoneFormatted['phone']})
    response : dict = {}

    if type(customer) == dict:

        if customer['date_updated']:
            customer['date_updated'] = customer['date_updated'].isoformat()

        del customer['_id']
        # doesn't have a password
        customer['hasPassword'] = False
        
        if customer['password']:
            customer['hasPassword'] = True
            del customer['password']

        # all good
        response['flag'] = 'existing'
        response['customer'] = customer
        response['message'] = 'Phone number verified'

    else:

        response = {
            'flag' : 'new',
            'message' : 'Phone number verified'
        }

        if not phoneFormatted['is_valid']:
            
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'Message' : 'invalid phone number'
                }
            )
        
    # all good
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )


# Save wallet transaction
@app.put(
    '/wallet/save-transaction',
    response_description="Save wallet transaction"
)
async def saveWalletTransction(body : WalletTransactionEntity = Body(...)):
    phoneFormatted = format_number(body.phone)
    customer = await customer_collection.find_one({"phone" : phoneFormatted['phone']})
    if customer != None:
        ...
    else:
        ...