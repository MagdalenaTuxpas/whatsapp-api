To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

To activate the virtualenv:

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

To install the required dependencies.

```
$ pip install -r requirements.txt
```

## Create .zip file for the Lambda function

If you modify the lambda function, you need to re-create the .zip file:

- inside the folder that includes the lambda.py file, delete the folders **pycache**, package, and the file my_deployment_package.zip
- re-create the .zip file:

```
$ cd whatsapp_api_stacks
$ pip install -r requirements.txt --target ./packages
$ cd packages
$ zip -r ../deployment_webhook.zip . && zip -r ../deployment_mll.zip .
$ cd ..
$ zip deployment_webhook.zip first-lambda.py && zip deployment_mll.zip second-lambda.py

```

## Deploy

```
$ cd ..
$ cdk deploy
```
