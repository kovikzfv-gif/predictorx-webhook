import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import stripe

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PRO_EMAILS = set()

@app.get("/")
def home():
    return {"ok": True, "stripe_key_set": bool(stripe.api_key), "webhook_secret_set": bool(WEBHOOK_SECRET)}

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET not set")

    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig, secret=WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = (session.get("customer_details") or {}).get("email")
        if email:
            PRO_EMAILS.add(email.lower())

    return JSONResponse({"received": True})

@app.get("/pro/check")
def check_pro(email: str):
    return {"pro": (email or "").lower() in PRO_EMAILS}

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import stripe

app = FastAPI()

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

PRO_EMAILS = set()

@app.get("/")
def home():
    return {"ok": True}

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig,
            secret=WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = (session.get("customer_details") or {}).get("email")
        if email:
            PRO_EMAILS.add(email.lower())

    return JSONResponse({"received": True})

@app.get("/pro/check")
def check_pro(email: str):
    return {"pro": (email or "").lower() in PRO_EMAILS}
