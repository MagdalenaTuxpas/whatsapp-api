import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import boto3
import os

chatbot_id = os.getenv("CHATBOT_ID")
ec2_id = os.getenv("EC2_ID")
ec2_port = os.getenv("EC2_PORT")
phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
whatsapp_app_token = os.getenv("WHATSAPP_APP_TOKEN")
client = boto3.client("lambda")


def build_send_message_data(recipient_id, message):
    payload = {
        "to": recipient_id,
        "text": f"I am the second lambda, I got this message: '{message}'",
    }
    return payload


def send_message_back(sender_id, sender_text):
    payload = build_send_message_data(sender_id, sender_text)
    response = client.invoke(
        FunctionName="arn:aws:lambda:us-east-1:949778761636:function:WhatsappApiStack-lambdawebhookwhatsapp7651717B-6ah5rN1GKEbA:response_handler",
        InvocationType="RequestResponse",
        Payload=json.dumps(
            {
                "sender_id": payload["to"],
                "sender_text": payload["text"],
            }
        ),
    )
    response_body = response["Payload"].read().decode("utf-8")
    return json.loads(response_body)


def handler(event, context):
    try:
        print(f"this is the event we got from the first lambda: {event}")
        sender_text = event["sender_text"]
        sender_id = event["sender_id"]
        print(
            f"here i should see the sender text, {sender_text}, and sender id, {sender_id}"
        )
        send_message_back(sender_id, sender_text)
        return {"statusCode": 200, "body": "success"}

    except Exception as e:
        print(e)
        send_message_back(sender_id, "No se puede acceder al Modelo de LLM")
