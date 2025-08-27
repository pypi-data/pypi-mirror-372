from datetime import date, datetime
from typing import Optional, Dict, Union
from boto3.session import Session

from ..__version__ import __title__, __version__, __build__


DEFAULT_REGION = "eu-west-1"


def build_session(
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    *,
    region: Optional[str] = DEFAULT_REGION
) -> Session:
    """
    Build a boto3 session using the provided access credentials if avalialbe, otherwise
    use the default credentials provider chain and the default eu-west-1 region.
    """
    if aws_access_key_id is None:
        return Session(region_name=region)
    else:
        return Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region
        )


def get_default_session(session: Optional[Session] = None, region: str = DEFAULT_REGION) -> Session:
    """
    If `session` is provided return it, otherwise create
    a session using default credentials and provided `region`.
    """
    return session if session is not None else build_session(region=region)


def get_client(service_name: str, session: Optional[Session] = None, region: str = DEFAULT_REGION):
    """
    Return a low level client for `service_name`.
    """
    return get_default_session(session, region).client(service_name)


def get_resource(service_name: str, session: Optional[Session] = None, region: str = DEFAULT_REGION):
    """
    Return a higher level resource client for `service_name`.
    """
    return get_default_session(session, region).resource(service_name)


def get_assumed_role_creds(
    role_arn: str,
    role_session_name: Optional[str] = None,
    *,
    session: Optional[Session] = None
) -> Dict[str, Union[str, datetime]]:
    """
    Assume the role and return the credentials dict that looks like this:
    {
        'AccessKeyId': 'string',
        'SecretAccessKey': 'string',
        'SessionToken': 'string',
        'Expiration': datetime(2021, 1, 1)
    }
    """
    sts = get_client("sts", session=session)

    if role_session_name is None:
        role_session_name = f"{__title__}-{__version__}.{__build__}"

    r = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name
    )
    return r["Credentials"]


def get_assumed_role_session(
    role_arn: str,
    session: Optional[Session] = None,
    region: str = DEFAULT_REGION
) -> Session:
    """
    Assume `role_arn` and return a boto3 session made from the temporary role credentials.
    """
    creds = get_assumed_role_creds(role_arn, session=session)
    return build_session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region=region
    )
