import os, requests, datetime as dt

TENANT = os.environ["GRAPH_TENANT_ID"]
CLIENT_ID = os.environ["GRAPH_CLIENT_ID"]
CLIENT_SECRET = os.environ["GRAPH_CLIENT_SECRET"]
USER = os.environ["OUTLOOK_USER_ID"]
NOTIFY = os.environ["OUTLOOK_NOTIFICATION_URL"]

def token(scope="https://graph.microsoft.com/.default"):
    url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
    data = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "scope": scope, "grant_type": "client_credentials"}
    return requests.post(url, data=data, timeout=10).json()["access_token"]

def main():
    t = token()
    expiry = (dt.datetime.utcnow() + dt.timedelta(minutes=55)).replace(microsecond=0).isoformat() + "Z"
    payload = {
        "changeType": "created",
        "notificationUrl": NOTIFY,
        "resource": f"/users/{USER}/messages",
        "expirationDateTime": expiry
    }
    r = requests.post("https://graph.microsoft.com/v1.0/subscriptions",
                      headers={"Authorization": f"Bearer {t}", "Content-Type": "application/json"},
                      json=payload, timeout=10)
    print(r.status_code, r.text)

if __name__ == "__main__":
    main()
