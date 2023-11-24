import uvicorn
from typing import Union
import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app import db, client, success, failed, format_number
from fastapi.responses import JSONResponse
from bson import ObjectId
from classes.Reviews import Review
# from controllers import CustomersController
from models import CustomersModel, TransactionSummaryModel, TransactionsModel
from classes import Transaction, Messaging

# import database
from database import customer_collection, transaction_summary_collection, transaction_collection, review_collection

import hashlib
import datetime
import requests
import constants

# Load from libs
import libs


# entities
from entities.VerifyPasswordEntity import VerifyPasswordEntity
from entities.WalletTransaction import WalletTransactionEntity
from entities.CreditCustomerEntity import CreditCustomerEntity
from entities.GeneratePaymentLinkEntity import GeneratePaymentLinkEntity
from entities.VerifyPaymentEntity import VerifyPaymentEntity
from entities.UpdateTransactionStatusEntity import UpdateTransactionStatusEntity
from entities import GeneralEntities

app = FastAPI()

# Middleware for CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    response_description="Save wallet transaction",
    status_code=status.HTTP_200_OK
)
async def saveWalletTransction(body : WalletTransactionEntity = Body(...)):
    phoneFormatted = format_number(body.phone)
    customer = await customer_collection.find_one({"phone" : phoneFormatted['phone']})
    if customer != None:
        referenceName = str(datetime.datetime.now()) + "_payment_reference"
        reference = hashlib.md5(referenceName.encode()).hexdigest()

        model = TransactionSummaryModel.TransactionSummaryModel(
            reference=reference,
            customer=customer['_id'],
            subTotal=float(body.amount),
            channel=body.channel,
            method=body.channel,
            total=float(body.amount)
        )

        # create record
        transaction_summary_collection.insert_one(model.model_dump(exclude=['id']))

        # all good
        return {
            "message" : "Transaction recorded, reference generated",
            "reference" : model.reference,
            "customer" : str(model.customer),
            "paying" : model.subTotal
        }
    
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message" : "Customer does not exists"
            }
        )
    

# Credit customer wallet (PRIVATE METHOD)
# @app.post('/wallet/credit-customer')
async def creditCustomerWallet(body : CreditCustomerEntity = Body(...)):
    customer = await customer_collection.find_one({"_id" : body.customer})
    if customer != None:
        # update wallet
        walletNewBalance = customer['wallet'] + float(body.total)
        customer_collection.find_one_and_update(
            filter={"_id" : body.customer},
            update={"$set" : {
                "wallet" : walletNewBalance,
                "date_updated" : datetime.datetime.now()
            }}
        )

        return {
            "message" : "Customer wallet updated successfully"
        }
    
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message" : "Customer does not exists"
            }
        )
    

# Generate Payment Link
@app.post(
        '/payment-link',
        status_code=status.HTTP_200_OK
        )
async def generatePaymentLink(body : GeneratePaymentLinkEntity = Body(...)):
    customer = await customer_collection.find_one({"_id" : ObjectId(body.customer)})

    if customer == None :
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message" : "Customer does not exists"
            }
        )
    
    # get transaction summary
    summary = await transaction_summary_collection.find_one({
        "reference" : body.reference,
        "customer" : customer['_id']
    })

    if summary == None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message" : "Reference ID does not exists"
            }
        )
    
    # Get access token
    accessToken = await libs.getPaymentAccessToken()

    # Get customer email
    customerEmail = customer['email'] if customer['email'] != None else "hupchopfood@gmail.com"

    # make request
    try:
        request = requests.post(
            url=constants.PAYMENT_URL + "/api/v1/merchant/transactions/init-transaction",
            json={
                "paymentReference" : body.reference,
                "amount" : summary['total'],
                "paymentDescription" : "Payment to Hupchop Food Tech",
                "currencyCode" : "NGN",
                "redirectUrl" : body.redirect,
                "contractCode" : constants.PAYMENT_CONTRACT_CODE,
                "customerName" : customer['fullname'],
                "customerEmail" : customerEmail,
                "paymentMethods" : ["CARD","ACCOUNT_TRANSFER", "USSD"]
            },
            headers={
                "Authorization" : "Bearer " + accessToken
            }
        )

        response = request.json()

        if request.ok:

            request.close()

            tx_ref = response['responseBody']['transactionReference']

            # save transaction reference
            await transaction_summary_collection.find_one_and_update(
                filter={"reference" : body.reference},
                update={"$set" : {"transaction_reference" : tx_ref} }
            )

            return {
                "url" : response['responseBody']['checkoutUrl'],
                "tx_ref" : tx_ref
            }
        
        else:

           return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message" : response['responseMessage']
                }
            ) 
        
    except:
        
        ...

    return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message" : 'Duplicate payment reference'
                }
            )


# Verify payment
@app.post('/verify/payment/', status_code=status.HTTP_200_OK)
async def verifyPayment(body : VerifyPaymentEntity = Body(...)):

    transaction = await transaction_summary_collection.find_one({"reference" : body.paymentReference})

    if transaction == None or (isinstance(transaction, dict) and transaction["transaction_reference"] == ''):
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message" : 'Transaction does not exists'
                }
            )

    BASE_URL = constants.PAYMENT_URL + '/api/v2/transactions/' + transaction['transaction_reference']
    accessToken = await libs.getPaymentAccessToken()

    # make http request
    request = requests.get(
        url=BASE_URL,
        headers={
            "Authorization" : "Bearer " + accessToken
        }
    )

    response = request.json()

    if request.ok:

        # get amount paid
        amountPaid = float(response['responseBody']['amountPaid'])

        # paid?
        if amountPaid > 0:
            
            paymentStatus = str(response['responseBody']['paymentStatus']).lower()

            # get all transaction ids
            ids = list()

            # get message
            message = ""

            # get payable
            payable = float(response['responseBody']['totalPayable'])

            # check payment status
            if str(response['responseBody']['paymentStatus']).upper == constants.PAID :

                # get amount settled
                settlementAmount = float(response['responseBody']['settlementAmount'])
                app_fee = amountPaid - settlementAmount
                amount_settled = settlementAmount
                processor = 'monnify'

                # post transaction
                await Transaction.TransactionSuccessful(
                    app_fee=app_fee,
                    amount_settled=amount_settled,
                    reference=body.paymentReference,
                    processor=processor
                ).Save()


            transactions = await transaction_collection.find({"reference" : body.paymentReference}).to_list(1000)

            if len(transactions) > 0:
                for row in transactions:
                    ids.append(row['itemid'])

            return {
                "message" : "Payment verified with status",
                "payment_status" : 'success',
                "message" : message,
                "ids" : ids
            }

        else:
            ...

    else:

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message" : response['responseMessage']
            }
        )


# Update transaction status
@app.post('/transactions/update/status', status_code=status.HTTP_200_OK)
async def updatePaymentStatus(body : UpdateTransactionStatusEntity = Body(...)):

    transaction = Transaction.TransactionStatus(
        reference=body.reference,
        status=body.status
    )

    # save now
    await transaction.Update()

    # done
    return {
        "message" : 'Transaction status updated'
    }


# submit a review
@app.post('/review/submit', status_code=status.HTTP_200_OK)
async def submitReview(body : GeneralEntities.SubmitReviewEntity = Body(...)):

    phoneNumber = format_number(body.customer_phone)

    if not phoneNumber['is_valid']:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message" : "Invalid Phone number"
            }
        )
    
    # continue
    foodId, sellerId = body.id

    # manage option
    if body.review_type.lower() == 'food' :
        verifiedPurchase = await Review.verifiedFoodPurchase(
            customer_phone=body.customer_phone,
            foodid=body.id
        )
    else:
        verifiedPurchase = await Review.verifiedRestaurantPurchase(
            customer_phone=body.customer_phone,
            sellerid=body.id
        )

    # insert data
    review_collection.insert_one(
        document={
            "typeid" : body.id,
            "review_type" : body.review_type,
            "customer" : {
                "phone" : body.customer_phone,
                "name" : body.customer_name,
                "id" : Review.customer['_id']
            },
            "experience" : Review.getExperience(body.rating),
            "rating" : body.rating,
            "review_title" : body.review_title,
            "review" : body.review_text,
            "verified_purchase" : verifiedPurchase,
            "date_created" : datetime.datetime.now(),
            "helpful" : 0,
            "not_helpful" : 0
        }
    )

    # update review count
    await Review.updateReviewCount(data=body)

    return {
        "status" : True,
        "message" : 'Thank you '+body.customer_name+'! Your review has been submitted successfully!'
    }


# review was helpful
@app.post('/review/helpful', status_code=status.HTTP_200_OK)
async def reviewWasHelpful(body : GeneralEntities.UpdateReviewActivity = Body(...)):
    review = await review_collection.find_one(
        filter={"_id" : ObjectId(body.id)}
    )

    if review == None :
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message" : "Review with ID does not exists."
            }
        )
    
    # was helpful
    review['helpful'] += 1

    # update record
    await review_collection.update_one(
        filter={"_id" : ObjectId(body.id)},
        update={"$set" : {
            "helpful" : review['helpful']
        }}
    )

    # all good
    return {
        "status" : True,
        "message" : "This review has been marked helpful!",
        "helpful" : review['helpful']
    }


# review was absusive
@app.post('/review/abusive', status_code=status.HTTP_200_OK)
async def reviewWasAbusive(body : GeneralEntities.UpdateReviewActivity = Body(...)):
    review = await review_collection.find_one(
        filter={"_id" : ObjectId(body.id)}
    )

    if review == None :
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message" : "Review with ID does not exists."
            }
        )
    
    # report 
    review['report_abuse'] = 1 if review['report_abuse'] != None else (int(review['report_abuse']) + 1)

    # update record
    await review_collection.update_one(
        filter={"_id" : ObjectId(body.id)},
        update={"$set" : {
            "report_abuse" : review['report_abuse']
        }}
    )

    return {
        "status" : True,
        "message" : "This review has been reported abusive!"
    }


...