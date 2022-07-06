import emails
from emails.template import JinjaTemplate as T
from lxml import html

from app.utils import generate_confirmation_token
from settings import settings


def add_unsubscribe_link(
    html_template: str,
    contact_id: str,
    target_base_url: str,
    message_before: str = "You don't want to hearing from us ? ",
    message: str = "Unsubscribe",
) -> str:
    token = generate_confirmation_token(contact_id)
    unsubscribe_url = target_base_url + f"/{token}"
    unsubscribe_link = f"""
    <div class="footer" style="clear: both; margin-top: 30px; width: 100%; font-size: 10px;">
        <br> {message_before} <a href={unsubscribe_url} style="text-decoration: underline; color: #999999; text-align: center;">{message}</a>.
    </div>"""
    element = html.fromstring(unsubscribe_link)
    html_template_tree = html.fromstring(html_template)
    html_template_tree.body.append(element)
    return html.tostring(html_template_tree).decode("utf-8")


def add_pixel_link(html_template: str, email_id: str, target_base_url: str) -> str:
    token = generate_confirmation_token(email_id)
    image_url = target_base_url + f"/{token}"
    pixel_link = f"""<img src={image_url} style="height: 1px !important; max-height: 1px !important; max-width: 1px !important; width: 1px !important"/>"""
    element = html.fromstring(pixel_link)
    html_template_tree = html.fromstring(html_template)
    html_template_tree.body.append(element)
    return html.tostring(html_template_tree).decode("utf-8")


def send_email(
    email_to: str,
    name_from: str,
    html_template: str,
    subject: str,
    infos_to_render: dict,
    unsubscribe_link: bool = False,
    contact_id: int = None,
    pixel_link: bool = False,
    email_id: int = None,
):

    if unsubscribe_link:
        html_template = add_unsubscribe_link(
            html_template,
            contact_id=contact_id,
            target_base_url=settings.UNSUBSCRIBE_URL,
        )

    if pixel_link:
        html_template = add_pixel_link(
            html_template, email_id=email_id, target_base_url=settings.PIXEL_URL
        )

    message = emails.html(
        subject=T(subject),
        html=T(html_template),
        mail_from=(name_from, settings.MAIL_ADDRESS),
    )

    r = message.send(
        to=email_to,
        render=infos_to_render,
        smtp={
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "ssl": settings.SMTP_SSL,
            "user": settings.MAIL_ADDRESS,
            "password": settings.MAIL_PWD,
        },
    )

    return r
