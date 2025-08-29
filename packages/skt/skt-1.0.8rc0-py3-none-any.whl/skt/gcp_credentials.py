from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.oauth2.credentials import Credentials


def _get_jupyterhub_user_id():
    import os

    return os.environ["JUPYTERHUB_USER"] if "JUPYTERHUB_USER" in os.environ else None


def _get_user_credentials() -> "Credentials":
    import os
    import time

    import requests
    from google_auth_oauthlib.flow import InstalledAppFlow

    from .vault_utils import get_secrets

    redirect_url = os.getenv(
        "GCP_AUTH_REDIRECT_URL", "https://aim.yks.sktai.io/api/v1/gcp-authorization/oauth2callback"
    )
    oauth_credentials = get_secrets("gcp/sktaic-datahub/aidp-oauth")
    client_id = oauth_credentials["CLIENT_ID"]
    client_secret = oauth_credentials["CLIENT_SECRET"]

    flow = InstalledAppFlow.from_client_config(
        client_config={
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        redirect_uri=redirect_url,
    )

    url, state = flow.authorization_url()
    print(f"Please visit this URL to authorize this application: {url}")

    stime = time.time()

    oauth_code_url = os.getenv("GCP_AUTH_OAUTH_CODE_URL", "https://aim.yks.sktai.io/api/v1/gcp-authorization/codes")

    code = None
    while stime + 300 > time.time():
        s = requests.Session()

        res = s.get(url=f"{oauth_code_url}/{state}")
        if res.status_code != requests.codes.ok:
            time.sleep(5)
        else:
            code = res.json()["results"]
            break

    if not code:
        raise ValueError("Time out occurred while waiting for authorization code")

    flow.fetch_token(code=code)
    return flow.credentials


def _get_service_account_credentials():
    import json

    from google.oauth2 import service_account

    from .vault_utils import get_secrets

    key = get_secrets("gcp/skt-datahub/dataflow")["config"]
    json_acct_info = json.loads(key)
    credentials = service_account.Credentials.from_service_account_info(json_acct_info)
    scoped_credentials = credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])

    return scoped_credentials


def get_gcp_credentials():
    jupyterhub_user_id = _get_jupyterhub_user_id()
    if jupyterhub_user_id:
        return _get_user_credentials()
    else:
        return _get_service_account_credentials()
