from datetime import datetime, timezone, timedelta
from sqlmodel import Field, SQLModel, Column, JSON, Relationship, Session, select
from typing import Optional, Dict, List


############ Contact & Campaign Link ############


class ContactCampaignLink(SQLModel, table=True):
    campaign_id: Optional[int] = Field(
        default=None, foreign_key="campaign.id", primary_key=True
    )
    contact_id: Optional[int] = Field(
        default=None, foreign_key="contact.id", primary_key=True
    )


############ Contact ############


class ContactBase(SQLModel):
    email: str
    meta: Dict = Field(default={}, sa_column=Column(JSON))

    class Config:
        arbitrary_types_allowed = True


class Contact(ContactBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    campaigns: List["Campaign"] = Relationship(
        back_populates="contacts", link_model=ContactCampaignLink
    )
    mails: List["Mail"] = Relationship(back_populates="contact")


class ContactCreate(ContactBase):
    pass


class ContactRead(ContactBase):
    id: int


class ContactUpdate(SQLModel):
    email: Optional[str] = None
    meta: Optional[dict] = {}


############ Campaign ############


class CampaignBase(SQLModel):
    name: str
    html_template: Optional[str] = ""
    sender_name: Optional[str] = ""
    subject: Optional[str] = ""
    started: bool = False


class Campaign(CampaignBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    contacts: List[Contact] = Relationship(
        back_populates="campaigns", link_model=ContactCampaignLink
    )
    mails: List["Mail"] = Relationship(back_populates="campaign")

    def open_rate(self) -> float:
        return sum([mail.is_open for mail in self.mails]) / len(self.mails)

    def send_rate(self) -> float:
        return sum([mail.time_send is not None for mail in self.mails]) / len(
            self.mails
        )

    class Config:
        arbitrary_types_allowed = True


class CampaignCreate(CampaignBase):
    contacts_ids_to_add: List[int] = []


class CampaignRead(CampaignBase):
    id: int


class CampaignUpdate(SQLModel):
    name: Optional[str] = None
    contacts_ids_to_add: List[int] = []
    contacts_ids_to_remove: List[int] = []
    html_template: Optional[str] = None
    sender_name: Optional[str] = None
    subject: Optional[str] = None


############ Mail Templates ############


class MailTemplateBase(SQLModel):
    template: str
    name: Optional[str] = None


class MailTemplate(MailTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class MailTemplateCreate(CampaignBase):
    pass


class MailTemplateRead(CampaignBase):
    id: int


class MailTemplateUpdate(SQLModel):
    template: Optional[str] = None
    name: Optional[str] = None


############ Mails ############


class MailBase(SQLModel):
    # time_send: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)))
    time_send: Optional[datetime] = None
    is_open: bool = False


class Mail(MailBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    contact_id: Optional[int] = Field(default=None, foreign_key="contact.id")
    contact: Optional[Contact] = Relationship(back_populates="mails")

    campaign_id: Optional[int] = Field(default=None, foreign_key="campaign.id")
    campaign: Optional[Campaign] = Relationship(back_populates="mails")

    @classmethod
    def month_count(cls, session: Session):
        # rolling average number of mails send in a month
        return len(
            session.exec(
                select(cls).where(
                    cls.time_send >= (datetime.now(timezone.utc) - timedelta(days=30))
                )
            ).all()
        )

    @classmethod
    def day_count(cls, session: Session):
        # rolling average number of mails send in 24 hours
        return len(
            session.exec(
                select(cls).where(
                    cls.time_send >= (datetime.now(timezone.utc) - timedelta(hours=24))
                )
            ).all()
        )


class MailCreate(MailBase):
    contact_id: int
    sender_name: Optional[str]
    subject: Optional[str]
    campaign_id: Optional[int]
    time_to_send: Optional[datetime]
    html_template: Optional[str] = ""


class MailRead(MailBase):
    id: int
    contact_id: Optional[int]
    campaign_id: Optional[int]


class MailUpdate(SQLModel):
    is_open: Optional[bool]
    time_send: Optional[datetime]


############ Join Contact & Campaign ############


class CampaignReadWithContacts(CampaignRead):
    contacts: List[ContactRead] = []


class ContactReadWithCampaigns(ContactRead):
    campaigns: List[CampaignRead] = []


class MailReadWithContact(MailRead):
    contact: ContactRead
