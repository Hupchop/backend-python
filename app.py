from dotenv import load_dotenv
from fastapi import status
import motor.motor_asyncio
import os
import phonenumbers

load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.get_database(os.getenv("DATABASE"))

def success(message, data):
    return {
        "status" : status.HTTP_200_OK,
        "message" : message,
        "data" : data
    }


def failed(message, data = {}):
    return {
        "status" : status.HTTP_404_NOT_FOUND,
        "message" : message,
        "data" : data
    }

def format_number(phone : str, country : str = "NG") :
    phoneNumber = phonenumbers.parse(phone, country)
    return {
        "phone" : phonenumbers.format_number(phoneNumber, phonenumbers.PhoneNumberFormat.E164),
        "is_valid" : phonenumbers.is_valid_number(phoneNumber)
    }