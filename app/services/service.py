#!/usr/bin/env python
# coding: latin1
from models.announcements import Announcements, AnnouncementSchema
from config import db

announcement_schema = AnnouncementSchema()
announcements_schema = AnnouncementSchema(many=True)

def get_all():
    '''
    Get all entities
    :returns: all entity
    '''
    announcements = Announcements.query.order_by(Announcements.createdAt.desc()).all()  
    return announcements_schema.dump(announcements)
    
def get_published():
    return Announcements.query.filter(Announcements.published_at.isnot(None)).order_by(Announcements.createdAt.desc()).all()

def getItemsByImageName(imageName):
    return Announcements.query.filter_by(image = imageName).all()

def get(id):
    item = Announcements.query.get(id)
    if item:
        return announcement_schema.dump(item)

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    item = Announcements(**body)
    db.session.add(item)
    db.session.commit()
    return item

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    item = Announcements.query.get(body['id'])
    if item:
        item = Announcements(**body)
        db.session.merge(item)
        db.session.flush()
        db.session.commit()
        return item
    
def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    item = Announcements.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return True