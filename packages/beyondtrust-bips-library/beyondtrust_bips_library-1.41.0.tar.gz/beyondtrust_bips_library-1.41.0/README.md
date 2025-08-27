# Password Safe API integration
[![License](https://img.shields.io/badge/license-MIT%20-brightgreen.svg)](LICENSE)

Password Safe API integration written in Python, Abstract complexity of managing secrets with the API

## Python version compatibility
  
This library is compatible with Python >= v3.11.

## Install Package

```sh
# PyPI
pip install beyondtrust-bips-library
```
## Arguments

### Retrieve Secrets
- api_url:
    - description: BeyondTrust Password Safe API URL.
    - type: string
    - required: True
- api_key:
    - description: The API Key configured in BeyondInsight for your application. If not set, then client credentials must be provided.
    - type: string
    - required: False
- client_id:
    - description: API OAuth Client ID.
    - type: string
    - required: True
- client_secret:
    - description: API OAuth Client Secret.
    - type: string
    - required: True
- secret_list:
    - description: List of secrets ["path/title","path/title"] or managed accounts ["ms/ma","ms/ma"] to be retrieved, separated by a comma.
    - type: list
    - required: True
- certificate_path:
    - description: Password Safe API pfx Certificate Path. For use when authenticating using a Client Certificate.
    - type: string
    - required: False
- certificate_password:
    - description: Password Safe API pfx Certificate Password. For use when authenticating using a Client Certificate.
    - type: string
    - required: False
- verify_ca:
    - description: Indicates whether to verify the certificate authority on the Secrets Safe instance.
    - type: boolean 
    - default: True
    - required: False

## Methods
- get_secrets(self, paths)
	- Invoked for Managed Account or Secrets Safe secrets.
	- Returns a list of secrets in the requested order.
- get_secret(self, path)
	- Invoked for Managed Account or Secrets Safe secrets.
	- Returns the requested secret.

## Example of usage

We strongly recommend you to use a virtual environment and install dependences from requirements.txt file.

Import `secrets_safe_library`

```sh
pip install -r ~/requirements.txt
```

By default urllib3 logs are not shown, If need to show them:

```sh
export URLLIB3_PROPAGATE=True
```

script example using library:
```python
import  os
import  logging
from  secrets_safe_library  import  secrets_safe, authentication, utils, managed_account
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

env  =  os.environ
LOGGER_NAME  =  "custom_logger"

logging.basicConfig(format  =  '%(asctime)-5s  %(name)-15s  %(levelname)-8s  %(message)s',

level  =  logging.DEBUG)

# logger object is optional but is strongly recommended
logger  =  logging.getLogger(LOGGER_NAME)

TIMEOUT_CONNECTION_SECONDS = 30
TIMEOUT_REQUEST_SECONDS = 30

CERTIFICATE = env['CERTIFICATE']
CERTIFICATE_KEY = env['CERTIFICATE_KEY']

def  main():
    try:
        with requests.Session() as session:
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.2,
                status_forcelist=[400, 408, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            
            certificate, certificate_key = utils.prepare_certificate_info(CERTIFICATE, CERTIFICATE_KEY)
            
            authentication_obj = authentication.Authentication(
                req=session,
                timeout_connection=TIMEOUT_CONNECTION_SECONDS,
                timeout_request=TIMEOUT_REQUEST_SECONDS,
                api_url="https://example.com:443/BeyondTrust/api/public/v3",
                client_id="<client_id>",
                client_secret="<client_secret>",
                certificate=certificate,
                certificate_key=certificate_key,
                verify_ca=True,
                logger=None
            )

            # sign app in password safe API
            get_api_access_response  =  authentication_obj.get_api_access()

            if  get_api_access_response.status_code ==  200:
                # instantiate secrets safe object
                secrets_safe_obj  =  secrets_safe.SecretsSafe(authentication_obj, logger)

                get_secrets_response  =  secrets_safe_obj.get_secrets(["oagrp/text,oagrp/credential"])
                utils.print_log(logger, f"=> Retrive secrets: {get_secrets_response}", logging.DEBUG)
            else:
                print(f"Please check credentials, error {get_api_access_response.text}")
            
            authentication_obj.sign_app_out()

    except  Exception  as  e:
        utils.print_log(logger, f"Error: {e}", logging.ERROR)

# calling main method
main()
```
