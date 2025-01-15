from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
import os
import requests
import io
from .tasks import *

# Initialize Twilio Client
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

def split_message(message, max_length=1600):
    """Split message into chunks of a specified maximum length."""
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

@csrf_exempt
def whatsapp_webhook(request):
    post_data = request.POST
    num_media = int(post_data.get("NumMedia", 0))
    sender_number = post_data.get("From")
    response_body = ""

    if num_media > 0:
        for i in range(num_media):
            media_url = post_data.get(f"MediaUrl{i}")
            media_type = post_data.get(f"MediaContentType{i}")

            # Download media file as binary
            try:
                response = requests.get(media_url, auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
                response.raise_for_status()
                file_bytes = io.BytesIO(response.content)

                # Handle PDFs
                if "application/pdf" in media_type:
                    client.messages.create(
                        from_='whatsapp:+14155238886',
                        body="Processing PDF file...",
                        to=sender_number
                    )
                    response_body = pdf_to_text(file_bytes)
                    
                # Handle Images
                elif "image" in media_type:
                    client.messages.create(
                        from_='whatsapp:+14155238886',
                        body="Processing image file...",
                        to=sender_number
                    )
                    response_body = image_to_text(file_bytes)

                # Handle Audio
                elif "audio" in media_type:
                    client.messages.create(
                        from_='whatsapp:+14155238886',
                        body="Processing audio file...",
                        to=sender_number
                    )
                    response_body = audio_to_text(file_bytes)

                # Handle Videos
                elif "video" in media_type:
                    client.messages.create(
                        from_='whatsapp:+14155238886',
                        body="Processing video file...",
                        to=sender_number
                    )
                    response_body = video_to_text(file_bytes,media_url)

            except Exception as e:
                response_body += f"\nFailed to download or process media file: {str(e)}"

    else:
        # Handle plain text messages
        message = post_data.get("Body", "").strip()
        if message.lower() == "hi":
            response_body = f"Hi, how's it going?"
        elif len(message.split()) < 5:
            response_body = "Please provide a longer message for summarization."
        else:
            # Here you can add summarization logic for text input
            response_body = f"Thanks for your message: {message}"

    # Send responses in batches of 1600 characters
    for chunk in split_message(response_body):
        client.messages.create(
            from_='whatsapp:+14155238886',
            body=chunk,
            to=sender_number
        )

    return HttpResponse("Webhook processed successfully")