import json
import requests
import boto3
import os

ec2_id = os.getenv("EC2_ID")
ec2_port = os.getenv("EC2_PORT")
phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
whatsapp_app_token = os.getenv("WHATSAPP_APP_TOKEN")
client = boto3.client("lambda")


# Build message for Whatsapp API
def build_send_message_data(recipient_id, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {"body": message},
    }
    print(f"This is the payload from the build_send_msg_data: {payload}")
    return payload


# Send response to Whatsapp API
def send_response_to_wp(sender_id, sender_text):
    url = f"https://graph.facebook.com/v16.0/{phone_number_id}/messages/?access_token={whatsapp_app_token}"
    payload = build_send_message_data(sender_id, sender_text)
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"This is the response sent to wp: {response}")


# Get LLM EC2 instance IP
def get_public_ipv4(ec2_id: str):
    ec2 = boto3.client("ec2")
    instance_info = ec2.describe_instances(
        Filters=[
            {
                "Name": "instance-type",
                "Values": [
                    "r5.4xlarge",
                ],
            }
        ],
        InstanceIds=[ec2_id],
    )
    public_ip = instance_info["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    return public_ip


# Send request to LLM
def post_prompt(post_prompt, api_url):
    try:
        response = requests.post(api_url, data={"item": post_prompt})
        if response.status_code == 200:
            result = response.json()
            return result
    except Exception as e:
        print(f"Error: {str(e)}")


# Recieve message from first lambda and handle responses
def handler(event, context):
    try:
        # Recover client number and message
        sender_text = event["sender_text"]
        sender_id = event["sender_id"]
        print(f"This is the original text: {sender_text}")
        send_response_to_wp(sender_id, "Su respuesta está siendo procesada.")
        # in case we want to create more endpoints:
        api_post_prompt = "/"

        # Send message and get response from LLM
        ec2_ip = get_public_ipv4(ec2_id)
        print(ec2_ip)
        url_post_prompt = f"http://{ec2_ip}:{ec2_port}{api_post_prompt}"
        answer = post_prompt(sender_text, url_post_prompt)
        response = send_response_to_wp(sender_id, answer["Answer"])
        print(f"This is the response we got from the LLM: {response}")

    except Exception as e:
        print(e)
        send_response_to_wp(sender_id, "No se puede acceder al Modelo de LLM")
