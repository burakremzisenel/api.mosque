#!/usr/bin/env python
# coding: latin1

from config import db
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from marshmallow_sqlalchemy import auto_field, SQLAlchemyAutoSchema, SQLAlchemySchema

class Announcements(db.Model):
    ''' The data model'''
    # table name
    __tablename__ = 'announcements'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(400), nullable=False)
    url = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    published_at = db.Column(DateTime(timezone=True), nullable=True)
    createdAt = db.Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = db.Column(DateTime(timezone=True), onupdate=func.now())
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class AnnouncementSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Announcements
        load_instance = True

    # id = auto_field()
    # username = auto_field()
    # email = auto_field()