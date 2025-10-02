import hmac, os, base64, json
from fastapi import FastAPI, Request, HTTPException
from google.cloud import pubsub_v1
from app.gmail import decode_pubsub_message, fetch_message_by_id, normalize_gmail_message
from app.outlook import graph_token, get_message, normalize_outlook_message
from app.schemas import NormalizedEmail

app = FastAPI()

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
TOPIC = os.environ["PUBSUB_TOPIC"]
PUSH_TOKEN = os.environ.get("PUBSUB_PUSH_TOKEN","")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC)

def publish_event(event: NormalizedEmail):
    publisher.publish(topic_path, json.dumps(event.model_dump()).encode("utf-8")).result()

@app.get("/healthz")
def healthz():
    return {"ok": True}

# Gmail Pub/Sub push endpoint
@app.post("/gmail/webhook")
async def gmail_webhook(request: Request):
    if PUSH_TOKEN:
        # optional shared-secret verification
        if request.headers.get("X-Goog-Resource-State") is None:
            # For Pub/Sub push, use a custom header or query param; adjust as needed
            token = request.headers.get("X-Pubsub-Token","")
            if token != PUSH_TOKEN:
                raise HTTPException(401, "bad token")
    body = await request.json()
    envelope = body.get("message")
    if not envelope:
        return {"ignored": True}
    data_json = json.loads(base64.b64decode(envelope["data"]).decode())
    # data_json contains historyId; fetch specific messages via history or poll recent and dedupe.
    # If you also include messageId in your pipeline, fetch directly:
    message_id = data_json.get("messageId")
    user = os.environ.get("GMAIL_USER","me")
    if message_id:
        msg = fetch_message_by_id(user, message_id)
        event = NormalizedEmail(**normalize_gmail_message(msg))
        publish_event(event)
    return {"ok": True}

# Outlook webhook endpoint
@app.post("/outlook/webhook")
async def outlook_webhook(request: Request):
    # Graph validation handshake uses validationToken query param, must echo raw text.
    token = request.query_params.get("validationToken")
    if token:
        return token
    payload = await request.json()
    access = graph_token()
    for n in payload.get("value", []):
        # resourceData.id is the message id
        rid = n.get("resourceData", {}).get("id")
        user = os.environ["OUTLOOK_USER_ID"]
        if rid:
            msg = get_message(user, rid, access)
            event = NormalizedEmail(**normalize_outlook_message(msg))
            publish_event(event)
    return {"ok": True}
