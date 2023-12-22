import json
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import boto3
import os
from typing import Dict, List

ec2_id = os.getenv("EC2_ID")
ec2_port = os.getenv("EC2_PORT")
phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
whatsapp_app_token = os.getenv("WHATSAPP_APP_TOKEN")
client = boto3.client("lambda")
SAGEMAKER_ENDPOINT = "llama-2-test-magdis"
INFERENCE_COMPONENT_NAME = (
    "jumpstart-dft-meta-textgeneration-l-20231222-2-20231222-2047570"
)
sgmk = boto3.client("runtime.sagemaker")


def session_with_retries():
    s = requests.Session()
    retries = Retry(
        total=3, backoff_factor=0.1, status_forcelist=[408, 500, 502, 503, 504]
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


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
    session = session_with_retries()
    url = f"https://graph.facebook.com/v16.0/{phone_number_id}/messages/?access_token={whatsapp_app_token}"
    payload = build_send_message_data(sender_id, sender_text)
    headers = {"Content-Type": "application/json"}
    response = session.post(url, headers=headers, data=json.dumps(payload))
    print(f"This is the response sent to wp: {response}")


# Build message for MLL
def format_messages(messages: List[Dict[str, str]]) -> List[str]:
    """Format messages for Llama-2 chat models.

    The model only supports 'system', 'user' and 'assistant' roles, starting with 'system', then 'user' and
    alternating (u/a/u/a/u...). The last message must be from 'user'.
    """
    prompt: List[str] = []

    if messages[0]["role"] == "system":
        content = "".join(
            [
                "<<SYS>>\n",
                messages[0]["content"],
                "\n<</SYS>>\n\n",
                messages[1]["content"],
            ]
        )
        messages = [{"role": messages[1]["role"], "content": content}] + messages[2:]

    for user, answer in zip(messages[::2], messages[1::2]):
        prompt.extend(
            [
                "<s>",
                "[INST] ",
                (user["content"]).strip(),
                " [/INST] ",
                (answer["content"]).strip(),
                "</s>",
            ]
        )

    prompt.extend(["<s>", "[INST] ", (messages[-1]["content"]).strip(), " [/INST] "])

    return "".join(prompt)


def print_messages(prompt: str, response: str) -> None:
    bold, unbold = "\033[1m", "\033[0m"
    print(
        f"{bold}> Input{unbold}\n{prompt}\n\n{bold}> Output{unbold}\n{response[0]['generated_text']}\n"
    )


# Send request to LLM
def query_endpoint(payload):
    client = boto3.client("sagemaker-runtime")
    response = client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps(payload),
    )
    response = response["Body"].read().decode("utf8")
    response = json.loads(response)
    return response


# Recieve message from first lambda and handle responses
def handler(event, context):
    try:
        # Recover client number and message
        sender_text = event["sender_text"]
        sender_id = event["sender_id"]
        print(f"This is the original text: {sender_text}")
        send_response_to_wp(sender_id, "Su respuesta está siendo procesada.")
        # payload = format_prompt(sender_text)

        # # Send message to LLM
        # answer = post_prompt(sender_text)
        # print(f"This is the response from the LLM: {answer}")
        dialog = [
            {"role": "system", "content": "Always answer with emojis"},
            {"role": "user", "content": "How to go from Beijing to NY?"},
        ]
        prompt = format_messages(dialog)
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256, "top_p": 0.9, "temperature": 0.6},
        }
        response = query_endpoint(payload)
        print_messages(prompt, response)
        # Sent MLL response to wp
        # response = send_response_to_wp(sender_id, answer[0]["generated_text"])
        print(f"This is the response we sent to the user: {response}")

    except Exception as e:
        print(e)
        send_response_to_wp(sender_id, "No se puede acceder al Modelo de LLM")
