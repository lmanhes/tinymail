from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from io import BytesIO
from loguru import logger
from PIL import Image

from app.crud import CRUDMail, CRUDContact
from app.db import get_session, Session
from app.models import Mail, Contact
from app.utils import confirm_token


router = APIRouter()


crud_mail = CRUDMail(Mail)
crud_contact = CRUDContact(Contact)


@router.get("/pixel/{token}")
async def pixel_tracking(token: str, session: Session = Depends(get_session)):
    mail_id = confirm_token(token)
    logger.info(f"Receive pixel tracking request from : {mail_id}")
    mail = crud_mail.get(session=session, id=mail_id)
    mail.is_open = True
    session.add(mail)
    session.commit()

    pixel = Image.new("RGB", size=(1, 1))
    pixel_bytes = BytesIO()
    pixel.save(pixel_bytes, "PNG")
    pixel_bytes.seek(0)

    return StreamingResponse(pixel_bytes, media_type="image/png")


@router.get("/unsubscribe/{token}")
async def unsubscribe_from_email(token: str, session: Session = Depends(get_session)):
    contact_id = confirm_token(token)
    logger.info(f"Receive unsubscribe request from : {contact_id}")
    contact = crud_mail.get(session=session, id=contact_id)
    contact.status = "unsubscribed"
    session.add(contact)
    session.commit()
    html_content = """
    <html>
        <body>
            <h3 style="margin-top: 30px; color: #999999; text-align: center;">Votre désinscription est prise en compte.</h3>
        </body>
    </html>
    """
    return HTMLResponse(html_content)
