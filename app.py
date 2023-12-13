#!/usr/bin/env python3
import os

import aws_cdk as cdk

from whatsapp_api_stacks.whatsapp_api_stack import WhatsappApiStack


app = cdk.App()
first_lambda_stack = WhatsappApiStack(
    app,
    "WhatsappApiStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
