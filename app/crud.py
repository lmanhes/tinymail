from fastapi import HTTPException, Query
from sqlmodel import select, SQLModel
from typing import List

from app.db import Session
from app.models import Contact


class CRUDBase(object):
    def __init__(self, model: SQLModel):
        self.model = model

    def get(self, session: Session, id: int):
        obj = session.get(self.model, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        return obj

    def get_multi(
        self, session: Session, offset: int = 0, limit: int = Query(default=20, lte=100)
    ):
        return session.exec(select(self.model).offset(offset).limit(limit)).all()

    def update(self, session: Session, id: int, obj: SQLModel):
        db_obj = session.get(self.model, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Object not found")

        obj_data = obj.dict(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def create(self, session: Session, obj: SQLModel):
        db_obj = self.model.from_orm(obj)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def create_multi(self, session: Session, objs: List[SQLModel]):
        for obj in objs:
            db_obj = self.model.from_orm(obj)
            session.add(db_obj)
        session.commit()

    def delete(self, session: Session, id: int):
        obj = session.get(self.model, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        session.delete(obj)
        session.commit()


class CRUDContact(CRUDBase):
    def __init__(self, model: SQLModel):
        super().__init__(model)

    def get_by_email(self, session: Session, email: str):
        return session.exec(select(Contact).where(Contact.email == email)).one()


class CRUDCampaign(CRUDBase):
    def __init__(self, model: SQLModel):
        super().__init__(model)

    def create(self, session: Session, obj: SQLModel):
        db_obj = self.model.from_orm(obj)

        obj_data = obj.dict(exclude_unset=True)
        if "contacts_ids_to_add" in obj_data:
            contacts = session.exec(
                select(Contact).where(Contact.id.in_(obj_data["contacts_ids_to_add"]))
            ).all()
            db_obj.contacts.extend(contacts)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(self, session: Session, id: int, obj: SQLModel):
        db_obj = session.get(self.model, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Object not found")

        obj_data = obj.dict(exclude_unset=True)
        for key, value in obj_data.items():
            try:
                setattr(db_obj, key, value)
            except ValueError:
                continue

        if "contacts_ids_to_add" in obj_data:
            contacts = session.exec(
                select(Contact).where(Contact.id.in_(obj_data["contacts_ids_to_add"]))
            ).all()
            db_obj.contacts.extend(contacts)

        if "contacts_ids_to_remove" in obj_data:
            contacts = session.exec(
                select(Contact).where(
                    Contact.id.in_(obj_data["contacts_ids_to_remove"])
                )
            ).all()
            for c in contacts:
                db_obj.contacts.remove(c)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


class CRUDMail(CRUDBase):
    def __init__(self, model: SQLModel):
        super().__init__(model)

    def get_multi(
        self,
        session: Session,
        offset: int = 0,
        limit: int = Query(default=20, lte=100),
        contact_id: int = None,
        campaign_id: int = None,
    ):
        statement = select(self.model)
        if contact_id:
            statement = statement.where(self.model.contact_id == contact_id)
        if campaign_id:
            statement = statement.where(self.model.campaign_id == campaign_id)
        return session.exec(statement.offset(offset).limit(limit)).all()

    def update(self, session: Session, id: int, obj: SQLModel):
        db_obj = session.get(self.model, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Object not found")

        obj_data = obj.dict(exclude_unset=True)
        for key, value in obj_data.items():
            try:
                setattr(db_obj, key, value)
            except ValueError:
                continue

        if "contact_id" in obj_data:
            contact = session.exec(select(Contact, obj_data["contact_id"]))
            if contact:
                db_obj.contact = contact

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
