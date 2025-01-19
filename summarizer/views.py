from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
import os
import requests
import io
from .tasks import *
from .utils import *

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
    type = ""

    if num_media > 0:
        for i in range(num_media):
            media_url = post_data.get(f"MediaUrl{i}")
            media_type = post_data.get(f"MediaContentType{i}")

            # Download media file as binary
            try:
                response = requests.get(media_url, auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
                response.raise_for_status()
                file_bytes = io.BytesIO(response.content)

                if "application/pdf" in media_type:
                    logger.debug("Received PDF file for processing.")
                    client.messages.create(from_='whatsapp:+14155238886', body="Processing PDF file...", to=sender_number)
                    response_body = pdf_to_text(file_bytes)
                    type = "PDF"
                elif "image" in media_type:
                    logger.debug("Received Image file for processing.")
                    client.messages.create(from_='whatsapp:+14155238886', body="Processing image file...", to=sender_number)
                    response_body = image_to_text(file_bytes)
                    type = "image"
                elif "audio" in media_type:
                    logger.debug("Received Audio file for processing.")
                    client.messages.create(from_='whatsapp:+14155238886', body="Processing audio file...", to=sender_number)
                    response_body = audio_to_text(file_bytes)
                    type = "audio"
                elif "video" in media_type:
                    logger.debug("Received Video file for processing.")
                    client.messages.create(from_='whatsapp:+14155238886', body="Processing video file...", to=sender_number)
                    response_body = video_to_text(file_bytes, media_url)
                    type = "video"
                elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in media_type:
                    logger.debug("Received Word file for processing.")
                    client.messages.create(from_='whatsapp:+14155238886', body="Processing Word file...", to=sender_number)
                    response_body = word_to_text(file_bytes)
                    type = "Word"
                elif "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in media_type:
                    logger.debug("Received Excel file for processing.")
                    client.messages.create(from_='whatsapp:+14155238886', body="Processing Excel file...", to=sender_number)
                    response_body = excel_to_text(file_bytes)
                    type = "Excel"
                elif "application/vnd.openxmlformats-officedocument.presentationml.presentation" in media_type:
                    logger.debug("Received PowerPoint file for processing.")
                    client.messages.create(from_='whatsapp:+14155238886', body="Processing PowerPoint file...", to=sender_number)
                    try:
                        response_body = ppt_to_text(file_bytes)
                        type = "PowerPoint"
                    except Exception as e:
                        response_body = handle_error(e, "Error processing PowerPoint file")
                        logger.error(f"Error processing PowerPoint file: {e}")

            except Exception as e:
                response_body = handle_error(e,"Error processing media file") #make sure the file is not corrupted and is in the limit size of __?
                print(f"Media Processing Error: {e}")
                logger.error(f"Error processing media file: {e}")

    else:
        message = post_data.get("Body", "").strip()
        if message.lower() == "hi":
            response_body = f"Hi, how's it going?"
        elif len(message.split()) < 5:
            response_body = "Please provide a longer message for summarization."
        else:
            client.messages.create(from_='whatsapp:+14155238886', body="Processing text...", to=sender_number)
            try:
                response_body = generate_summary(response_body)
            except Exception as e:
                response_body = handle_error(e)

    try:
        response_body = generate_summary(response_body, type)
    except Exception as e:
        response_body = handle_error(e)

    for chunk in split_message(response_body):
        client.messages.create(from_='whatsapp:+14155238886', body=chunk, to=sender_number)

    return HttpResponse("Webhook processed successfully")