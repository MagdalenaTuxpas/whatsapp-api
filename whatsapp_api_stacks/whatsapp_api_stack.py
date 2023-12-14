from aws_cdk import Stack, aws_lambda as _lambda
from constructs import Construct

path_lambdas = "./artifacts/lambdas/"


class WhatsappApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_webhook_whatsapp = _lambda.Function(
            self,
            "lambda_webhook_whatsapp",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="first-lambda.handler",
            code=_lambda.Code.from_asset(path_lambdas + "first-lambda"),
        )

        lambda_mll_handler = _lambda.Function(
            self,
            "lambda_mll_handler",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="second-lambda.handler",
            code=_lambda.Code.from_asset(path_lambdas + "second-lambda"),
        )
