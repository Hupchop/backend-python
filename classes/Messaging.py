import os
import requests
from app import format_number
from interfaces.SmsMessagingInterface import SmsMessagingInterface

class SmsMessaging():

    message : str 
    phone : str

    def __init__(self, message, phone) -> None:
        self.message = message
        self.phone = phone
        
    
    async def Send(self):
        baseUrl = os.getenv("SMS_API")

        # send data
        response = requests.post(
            url=baseUrl, 
            data={
                "token" : os.getenv("SMS_TOKEN"),
                "sender" : "Hupchop",
                "type" : 0,
                "routing" : 3,
                "message" : self.message,
                "to" : format_number(self.phone)['phone']
            }
        )

        print("SMS Sent!")

        response.close()
