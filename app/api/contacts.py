from fastapi import APIRouter, Depends, Query
from typing import List

from app.models import (
    Contact,
    ContactRead,
    ContactCreate,
    ContactReadWithCampaigns,
    ContactUpdate,
)
from app.db import Session, get_session
from app.crud import CRUDContact


router = APIRouter()


crud_contact = CRUDContact(Contact)


@router.get("", response_model=List[ContactRead])
def get_all_contacts(
    offset: int = 0,
    limit: int = Query(default=20, lte=100),
    session: Session = Depends(get_session),
):
    return crud_contact.get_multi(session=session, offset=offset, limit=limit)


@router.post("")
def create_contacts(
    contacts: List[ContactCreate], session: Session = Depends(get_session)
):
    contacts = crud_contact.create_multi(session=session, objs=contacts)
    return {"ok": True}


@router.get("/{contact_id}", response_model=ContactReadWithCampaigns)
def get_contact(contact_id: int, session: Session = Depends(get_session)):
    return crud_contact.get(session=session, id=contact_id)


@router.delete("/{contact_id}")
def delete_contact(contact_id: int, session: Session = Depends(get_session)):
    crud_contact.delete(session=session, id=contact_id)
    return {"ok": True}


@router.put("/{contact_id}", response_model=ContactRead)
def update_contact(
    contact_id: int, contact: ContactUpdate, session: Session = Depends(get_session)
):
    return crud_contact.update(session=session, id=contact_id, obj=contact)
