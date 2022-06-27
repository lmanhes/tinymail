from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.models import (
    Mail,
    MailRead,
    MailCreate,
    MailReadWithContact,
    Contact,
)
from app.crud import CRUDMail, CRUDContact
from app.db import Session, get_session
from app.worker import send_email_task


router = APIRouter()


crud_mail = CRUDMail(Mail)
crud_contact = CRUDContact(Contact)


@router.get("", response_model=List[MailRead])
def get_all_mails(
    offset: int = 0,
    limit: int = Query(default=20, lte=100),
    session: Session = Depends(get_session),
    contact_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
):
    return crud_mail.get_multi(
        session=session,
        offset=offset,
        limit=limit,
        contact_id=contact_id,
        campaign_id=campaign_id,
    )


@router.post("")
def create_mail(mail: MailCreate, session: Session = Depends(get_session)):
    # crud_mail.create(session=session, obj=mail)
    contact = crud_contact.get(session=session, id=mail.contact_id)

    html_template = """
    <html>
        <body>
            <div style="font-size: 14px;">
                <p>
                    Bonjour bonjour,<br><br>
                    Message de bienvenue de Tinymail.<br><br>
                    L’équipe Tinymail.
                </p>
            </div>
        </body>
    </html>
    """

    send_email_task.s(
        email_to=contact.email,
        name_from=mail.sender_name,
        html_template=html_template,
        subject=mail.subject,
        infos_to_render=contact.meta,
        unsubscribe_link=True,
        pixel_link=True,
    ).apply_async(eta=mail.time_to_send)

    return {"ok": True}


@router.get("/{mail_id}", response_model=MailReadWithContact)
def get_mail(mail_id: int, session: Session = Depends(get_session)):
    return crud_mail.get(session=session, id=mail_id)


@router.delete("/{mail_id}")
def delete_mail(mail_id: int, session: Session = Depends(get_session)):
    crud_mail.delete(session=session, id=mail_id)
    return {"ok": True}
