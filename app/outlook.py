# import os, requests, datetime as dt

# TENANT = os.environ["GRAPH_TENANT_ID"]
# CLIENT_ID = os.environ["GRAPH_CLIENT_ID"]
# CLIENT_SECRET = os.environ["GRAPH_CLIENT_SECRET"]

# def graph_token(scope="https://graph.microsoft.com/.default"):
#     url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
#     data = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "scope": scope, "grant_type": "client_credentials"}
#     r = requests.post(url, data=data, timeout=10)
#     r.raise_for_status()
#     return r.json()["access_token"]

# def get_message(user_id: str, message_id: str, token: str):
#     url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}"
#     r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
#     r.raise_for_status()
#     return r.json()

# def normalize_outlook_message(msg: dict) -> dict:
#     return {
#         "provider": "outlook",
#         "message_id": msg["id"],
#         "subject": msg.get("subject",""),
#         "sender": (msg.get("from") or {}).get("emailAddress",{}).get("address",""),
#         "body_preview": msg.get("bodyPreview",""),
#         "received_at": msg.get("receivedDateTime",""),
#         "headers": {},
#     }

# def create_outlook_subscription(user_id: str, notification_url: str, token: str, minutes=55):
#     # subscribe to newly created messages
#     url = "https://graph.microsoft.com/v1.0/subscriptions"
#     expiry = (dt.datetime.utcnow() + dt.timedelta(minutes=minutes)).replace(microsecond=0).isoformat() + "Z"
#     payload = {
#         "changeType": "created",
#         "notificationUrl": notification_url,
#         "resource": f"/users/{user_id}/messages",
#         "expirationDateTime": expiry
#     }
#     r = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=payload, timeout=10)
#     r.raise_for_status()
#     return r.json()
