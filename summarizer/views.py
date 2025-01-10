from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
import os

client = Client(os.getenv("TWILIO_ACCOUNT_SID"),os.getenv("TWILIO_AUTH_TOKEN"))

@csrf_exempt
def whatsapp_webhook(request):
    message = request. POST ["Body"]
    sender_name = request. POST ["ProfileName"]
    sender_number = request. POST ["From" ]
    if message == "hi":
        client.messages.create(
                            from_= 'whatsapp:+14155238886',
                            body="Hi {}, how's it going".format(sender_name), 
                            to=sender_number
        )
    return HttpResponse ("hello" )
'''
    if request.method == "POST":
        # Create a Twilio MessagingResponse
        response = MessagingResponse()
        # Add a reply to the incoming message
        response.message("Thanks for your message! We'll get back to you.")
        # Return the Twilio response as an HTTP response
        return HttpResponse(str(response), content_type="application/xml")
    return HttpResponse("Invalid request method.", status=405)
'''