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

## Deploy

```
$ cd ..
$ cdk deploy
```
