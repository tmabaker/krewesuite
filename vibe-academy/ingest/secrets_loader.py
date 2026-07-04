"""Load Skool credentials from AWS Secrets Manager (noit/skool).

Handles both the correct shape {"email": ..., "password": ...} and the
known console entry quirk where the credential values were stored as the
JSON *keys* (e.g. {"tammy@...": "", "<password>": ""}).

Never print, log, or write the returned values anywhere.
"""

import json
import os

import boto3

SECRET_ID = os.environ.get("SKOOL_SECRET_ID", "noit/skool")
REGION = os.environ.get("SECRETS_REGION", "us-east-1")


def get_skool_credentials():
    sm = boto3.client("secretsmanager", region_name=REGION)
    raw = sm.get_secret_value(SecretId=SECRET_ID)["SecretString"]
    data = json.loads(raw)

    # Correct shape
    email = data.get("email") or data.get("username")
    password = data.get("password")
    if email and password:
        return email, password

    # Quirk shape: values stored as keys. The email key contains '@';
    # the remaining key is the password.
    keys = list(data.keys())
    email_keys = [k for k in keys if "@" in k]
    other_keys = [k for k in keys if "@" not in k]
    if len(email_keys) == 1 and len(other_keys) == 1:
        return email_keys[0], other_keys[0]

    raise ValueError(
        f"Unrecognized secret shape for {SECRET_ID}: keys look like "
        f"{[('email-like' if '@' in k else 'other') for k in keys]}. "
        "Re-store as {\"email\": ..., \"password\": ...}."
    )
