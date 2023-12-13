import aws_cdk as core
import aws_cdk.assertions as assertions

from whatsapp_api_stacks.whatsapp_api_stack import WhatsappApiStack


# example tests. To run these tests, uncomment this file along with the example
# resource in whatsapp_api/whatsapp_api_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WhatsappApiStack(app, "whatsapp-api")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
