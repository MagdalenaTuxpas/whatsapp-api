import json
import requests
import os
import boto3

access_token = os.getenv("VERIFY_TOKEN")
phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
whatsapp_app_token = os.getenv("WHATSAPP_APP_TOKEN")
function_mll_handler_arn = os.getenv("MLL_HANDLER_ARN")
client = boto3.client("lambda")


# Whatsapp API Webhook check
def check_subscription(event):
    wp_token = access_token
    if event["queryStringParameters"]["hub.verify_token"] == wp_token:
        return {
            "statusCode": 200,
            "body": event["queryStringParameters"]["hub.challenge"],
        }
    else:
        return {"statusCode": 403, "body": "Token doesn't match"}


def invoke_second_lambda(sender_id, sender_text):
    response = client.invoke(
        FunctionName=function_mll_handler_arn,
        InvocationType="Event",
        Payload=json.dumps(
            {
                "sender_id": sender_id,
                "sender_text": sender_text,
            }
        ),
    )

    print(f"This is the response sent to the second lambda: {response}")
    response = {"statusCode": 200, "body": json.dumps({"message": "SUCCESS"})}
    return response


def handler(event, context):
    method = event["requestContext"]["http"]["method"]
    if method == "GET":
        r = check_subscription(event)
        print(f"Check subscription: {r}")
        return r

    elif method == "POST":
        try:
            body_data = json.loads(event["body"])
            # Validate Whatsapp API message structure
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
                invocar = invoke_second_lambda(sender_id, sender_text)
                print(f"This is the messsage sent to the second lambda: {invocar}")

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
