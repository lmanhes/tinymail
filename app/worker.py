from celery import Celery
from datetime import datetime, timezone
from loguru import logger

from app import settings
from app.crud import CRUDContact, CRUDMail
from app.db import Session, engine
from app.mails import send_email
from app.models import Mail, MailCreate, Contact


celery_app = Celery(
    "celery_app",
    backend=settings.REDISCLOUD_URL,
    broker=settings.REDISCLOUD_URL,
    celery_task_track_started=True,
)


@celery_app.task(bind=True)
def send_email_task(
    self,
    email_to: str,
    name_from: str,
    html_template: str,
    subject: str,
    campaign_id: int = None,
    infos_to_render: dict = {},
    unsubscribe_link: bool = False,
    pixel_link: bool = False,
):

    crud_contact = CRUDContact(model=Contact)
    crud_mail = CRUDMail(model=Mail)

    with Session(engine) as session:
        day_count = Mail.day_count(session=session)

        contact = crud_contact.get_by_email(session=session, email=email_to)

        mail_obj = MailCreate(contact_id=contact.id, campaign_id=campaign_id)
        mail = crud_mail.create(session=session, obj=mail_obj)

        logger.debug(f"Day count : {day_count}")

        # reschedule task if we reach the daily limit
        # gmail : 500
        # worspace : 2000
        if day_count > 400:
            logger.info("Daily limit reached")
            # retry in one hour
            self.retry(countdown=60 * 60)
        else:
            send_email(
                email_to=email_to,
                name_from=name_from,
                html_template=html_template,
                subject=subject,
                infos_to_render=infos_to_render,
                unsubscribe_link=unsubscribe_link,
                contact_id=contact.id,
                pixel_link=pixel_link,
                email_id=mail.id,
            )
            mail.time_send = datetime.now(timezone.utc)
            logger.debug("Mail is send")
            session.add(mail)
            session.commit()
