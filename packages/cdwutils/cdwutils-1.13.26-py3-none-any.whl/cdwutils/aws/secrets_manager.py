import base64
import json
from botocore.exceptions import ClientError
from .common import get_client


def get_secret(secret_name, session=None):
    """
    Return dict of the secret value.
    """
    client = get_client("secretsmanager", session)

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return json.loads(secret)
