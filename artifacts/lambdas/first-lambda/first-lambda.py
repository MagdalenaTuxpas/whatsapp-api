import json
import requests
import os
import boto3

access_token = os.getenv("VERIFY_TOKEN")
phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
whatsapp_app_token = os.getenv("WHATSAPP_APP_TOKEN")
client = boto3.client("lambda")


def check_subscription(event):
    wp_token = access_token
    if event["queryStringParameters"]["hub.verify_token"] == wp_token:
        return {
            "statusCode": 200,
            "body": event["queryStringParameters"]["hub.challenge"],
        }
    else:
        return {"statusCode": 403, "body": "Token doesn't match"}


def invocar(sender_id, sender_text):
    response = client.invoke(
        FunctionName="arn:aws:lambda:us-east-1:949778761636:function:WhatsappApiStack-lambdamllhandlerD67C4352-7JJdipec29Ah",
        InvocationType="RequestResponse",
        Payload=json.dumps(
            {
                "sender_id": sender_id,
                "sender_text": sender_text,
            }
        ),
    )
    response_body = response["Payload"].read().decode("utf-8")
    return json.loads(response_body)


def response_handler(event):
    sender_text = event["sender_text"]
    sender_id = event["sender_id"]
    print(
        f"here i should see the sender text, {sender_text}, and sender id, {sender_id} BACK FROM THE SECOND LAMBDA"
    )
    # Make POST request, echo bot
    url = f"https://graph.facebook.com/v16.0/{phone_number_id}/messages/?access_token={whatsapp_app_token}"
    payload = {
        "messaging_product": "whatsapp",
        "to": sender_id,
        "text": {
            "body": f"Esta fue la respuesta del segundo lambda: {sender_text}. Celebremos :D"
        },
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    return {"statusCode": 200, "body": "success"}


def handler(event, context):
    method = event["requestContext"]["http"]["method"]
    if method == "GET":
        r = check_subscription(event)
        return r

    elif method == "POST":
        try:
            body_data = json.loads(event["body"])
            messaging_data = (
                body_data["entry"][0]["changes"][0]["value"]["messages"][0]
                if (
                    "entry" in body_data
                    and body_data["entry"]
                    and body_data["entry"][0]["changes"]
                    and body_data["entry"][0]["changes"][0]["value"]["messages"]
                )
                else None
            )
            if messaging_data:
                sender_text = messaging_data["text"]["body"]
                sender_id = messaging_data["from"]

                # Invoke second-lambda
                invocar(sender_id, sender_text)

                # Make POST request, echo bot
                url = f"https://graph.facebook.com/v16.0/{phone_number_id}/messages/?access_token={whatsapp_app_token}"
                payload = {
                    "messaging_product": "whatsapp",
                    "to": sender_id,
                    "text": {
                        "body": f"Le envié tu mensaje, '{sender_text}', a la otra lambda, esperemos su respuesta..."
                    },
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, headers=headers, data=json.dumps(payload))

                return {"statusCode": 200, "body": "success"}
            else:
                return {"statusCode": 200, "body": "Invalid message structure"}

        except Exception as e:
            print(e)
            response = {
                "statusCode": 200,
                "body": json.dumps({"message": "can not get all data for response"}),
            }
            return response
