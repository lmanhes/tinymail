from fastapi import APIRouter

from app.api import contacts, campaigns, mails, webhooks


api_router = APIRouter()
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(mails.router, prefix="/mails", tags=["mails"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
