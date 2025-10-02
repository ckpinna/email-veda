import base64, json, os
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
PROJECT_ID = os.environ["GCP_PROJECT_ID"]

def gmail_client():
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=SCOPES
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def decode_pubsub_message(request_json: dict) -> dict:
    # Pub/Sub push wraps data in message.data base64
    msg = request_json["message"]
    data = base64.b64decode(msg["data"]).decode()
    return json.loads(data)

def fetch_message_by_id(user_id: str, message_id: str):
    svc = gmail_client()
    return svc.users().messages().get(userId=user_id, id=message_id, format="metadata", metadataHeaders=["Subject","From","Date"]).execute()

def normalize_gmail_message(msg: dict) -> dict:
    headers = {h["name"]: h["value"] for h in msg.get("payload",{}).get("headers",[])}
    return {
        "provider": "gmail",
        "message_id": msg["id"],
        "subject": headers.get("Subject",""),
        "sender": headers.get("From",""),
        "body_preview": "",  # use format="full" if you want snippet/body
        "received_at": headers.get("Date",""),
        "headers": headers,
    }
