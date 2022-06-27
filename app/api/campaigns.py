from celery import group
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from loguru import logger

from app.models import (
    Campaign,
    CampaignRead,
    CampaignCreate,
    CampaignReadWithContacts,
    CampaignUpdate,
)
from app.db import Session, get_session
from app.crud import CRUDCampaign
from app.worker import send_email_task


router = APIRouter()


crud_campaign = CRUDCampaign(model=Campaign)


@router.get("", response_model=List[CampaignRead])
def get_all_campaigns(
    offset: int = 0,
    limit: int = Query(default=20, lte=100),
    session: Session = Depends(get_session),
):
    return crud_campaign.get_multi(session=session, offset=offset, limit=limit)


@router.post("", response_model=CampaignReadWithContacts)
def create_campaign(campaign: CampaignCreate, session: Session = Depends(get_session)):
    return crud_campaign.create(session=session, obj=campaign)


@router.get("/{campaign_id}", response_model=CampaignReadWithContacts)
def get_campaign(campaign_id: int, session: Session = Depends(get_session)):
    return crud_campaign.get(session=session, id=campaign_id)


@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int, session: Session = Depends(get_session)):
    crud_campaign.delete(session=session, id=campaign_id)
    return {"ok": True}


@router.put("/{campaign_id}", response_model=CampaignReadWithContacts)
def update_campaign(
    campaign_id: int, campaign: CampaignUpdate, session: Session = Depends(get_session)
):
    return crud_campaign.update(session=session, id=campaign_id, obj=campaign)


@router.post("/{campaign_id}/start")
def start_campaign(campaign_id: int, session: Session = Depends(get_session)):
    campaign = crud_campaign.get(session=session, id=campaign_id)
    if campaign.started:
        raise HTTPException(status_code=409, detail="Campaign already started")

    html_template = """
    <html>
        <body>
            <div style="font-size: 14px;">
                <p>
                    Bonjour bonjour,<br><br>
                    Merci d’avoir rejoint Tinymail.<br><br>
                    L’équipe Tinymail.
                </p>
            </div>
        </body>
    </html>
    """

    logger.debug(f"Campaign contacts : {campaign.contacts}")

    tasks = []
    for contact in campaign.contacts:
        logger.info(f"Sending mail to {contact.email}")
        tasks.append(
            send_email_task.s(
                campaign_id=campaign.id,
                email_to=contact.email,
                name_from=campaign.sender_name,
                html_template=html_template,
                subject=campaign.subject,
                infos_to_render=contact.meta,
                unsubscribe_link=True,
                pixel_link=True,
            )
        )

    group(tasks)()
    campaign.started = True
    session.add(campaign)
    session.commit()

    return {"ok": True}


@router.get("/{campaign_id}/stats")
def get_campaign_stats(campaign_id: int, session: Session = Depends(get_session)):
    campaign = crud_campaign.get(session=session, id=campaign_id)
    return {"open_rate": campaign.open_rate(), "send_rate": campaign.send_rate()}
