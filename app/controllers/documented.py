#!/usr/bin/env python
# coding: latin1

from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage
from functools import wraps

from flask_restx import Namespace, Resource, Api, reqparse

import services.service as service
from models.announcements import Announcements
from models.user import User

import json

import os
from config import app
from flask_cors import CORS
from flask import send_file

from flask_firebase_admin import FirebaseAdmin
from firebase_admin import firestore, messaging

class ThreatStackError(Exception):
    '''Base Threat Stack error.'''
    status_code = 500

class ThreatStackRequestError(ThreatStackError):
    '''Threat Stack request error.'''

class ThreatStackAPIError(ThreatStackError):
    '''Threat API Stack error.'''

firebase = FirebaseAdmin(app)

CORS(app)
#pip install -U flask-cors

blueprint = Blueprint('documented', __name__, url_prefix='/api/v1.0')

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api_extension = Api(
    blueprint,
    title='API Mosque',
    version='1.0',
    description='This API is designed to store and deliver content for the mobile and tv Mosque Apps.',
    doc='/doc',
    authorizations=authorizations,
    security='apikey'
)

namespace = Namespace('announcements', 'mosque announcements related endpoints')
api_extension.add_namespace(namespace)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if app.config.get('API_KEY') and app.config['API_KEY'] == token:
            return f(*args, **kwargs)
        else:
            return {'message': 'Invalid or missing token'}, 401
    return decorated


upload_parser = namespace.parser()
upload_parser.add_argument('image', type=FileStorage, location='files', required=True)
upload_parser.add_argument('item', type=str, location='form', required=True, help='JSON-Daten im Format { "title": "announcement title", "body": "announcement body", "url": "www.example.url.com" }')

@namespace.route('/')
class AnnouncementCollection(Resource):
    @token_required
    def get(self):
        '''Get all entities'''
        #print('get all entities')
        nList = service.get_all()
        # return jsonify([announcements.as_dict() for announcements in nList])
        return nList
    
    @namespace.response(201, 'Item successfully created.')
    @namespace.response(500, 'Internal Server error')
    # @namespace.doc(params={'data': {'in': 'formData', 'type': 'object', 'required': True, 'description': 'JSON-Daten im Format { "title": "announcement title", "body": "announcement body", "url": "www.example.url.com" }'}})
    @namespace.expect(upload_parser)
    @token_required
    def post(self):
        '''Creates a new entity'''
        args = upload_parser.parse_args()
        try:
            # save image
            file = args['image']
            filename = (file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # save content to db
            content = json.loads(args['item'])
            #content = json.loads(request.form.get('item'))
            content['image'] = filename
            if not service.post(content):
                namespace.abort(500, 'Internal Server error')

            return None, 201

        except Exception as e:
            namespace.abort(500, str(e))

    @namespace.response(204, 'Item successfully updated.')
    @namespace.response(404, 'Item not found.')
    @namespace.expect(upload_parser)
    @token_required
    def put(self):
        ''' Update entity by id'''
        args = upload_parser.parse_args()
        try:
            newItem = json.loads(args['item'])
            itemID = newItem['id']

            oldItem = service.get(itemID)
            if not oldItem:
                namespace.abort(404)

            # delete old image
            # TODO
            # check if image exists & not used in another item
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], oldItem['image']))

            # save new image
            # TODO
            # check if new item has an image
            file = args['image']
            filename = (file.filename)
            newItem['image'] = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # update item
            updated = service.put(newItem)
            if not updated:
                namespace.abort(404)
            
            return None, 204

        except Exception as e:
            namespace.abort(500, str(e))

@namespace.route('/<string:id>')
@namespace.response(404, 'Item not found.')
@namespace.response(500, 'Internal Server error')
class AnnouncementItem(Resource):
    @token_required
    def get(self, id):
        """Returns details of a entity"""
        item = service.get(id)
        if not item:
            namespace.abort(404)

        return item
    
    @namespace.response(204, 'Item successfully deleted.')
    @token_required
    def delete(self, id):
        ''' Delete entity by id'''
        itemToDelete = service.get(id)
        if not itemToDelete:
            namespace.abort(404)

        imageName = itemToDelete['image']
        items = service.getItemsByImageName(imageName)
        if len( items ) == 1:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imageName))

        if not service.delete(id):
            namespace.abort(500)

        return None, 204
    
@namespace.response(404, 'Image not found.')
@namespace.route('/img/<string:filename>')
class Image(Resource):
    @token_required
    def get(self, filename):
        '''Get an image by filename'''
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


namespace2 = Namespace('notifications', 'push notification related endpoints')
api_extension.add_namespace(namespace2)
@namespace2.response(404, 'User not found.')
@namespace2.route('/message')
class Message(Resource):
    @token_required
    def post(self):
        postBody = request.get_json(silent=True)
        #print(postBody,flush=True)
        
        ''' User ID '''
        id = postBody['id']
        
        ''' Message Title '''
        notificationTitle = postBody['title']
        
        ''' Message Body '''
        notificationBody = postBody['body']
        
        ''' Get FireStore Client '''
        db = firestore.client()
            
        ''' init registration Token '''
        registration_token = ''
        
        '''  Get Messaging Token of User From FireStore '''
        doc = db.collection(u'users').document(id).get()
        if doc.exists:
            print(f'Document data: {doc.to_dict()}')
            user = User.from_dict(doc.id, doc.to_dict())
            if user.role == 'user':
                registration_token = user.token
        else:
            namespace.abort(404)
            
        response = ''      
        if isNotBlank(registration_token):
            message = messaging.Message(
                notification=messaging.Notification(
                    title= notificationTitle,
                    body= notificationBody,
                ),
                token = registration_token
            )

            response = messaging.send(message)
            return response, 201

@namespace2.response(404, 'User not found.')
@namespace2.route('/multicastmessage/<string:id>')
class MulticastMessage(Resource):
    @token_required
    def get(self, id):
            
        ''' Get announcement from db '''
        announcement = service.getItem(id)
        
        ''' Get FireStore Client '''
        firestore_db = firestore.client()
            
        ''' init Array for Tokens '''
        registration_tokens = []
        
        '''  Get Token of User '''
        docs = firestore_db.collection(u'users').stream()
        for doc in docs:
            #print(f'{doc.id} => {doc.to_dict()}',flush=True)
            user = User.from_dict(doc.id, doc.to_dict())
            
            ''' only registered Users & Anonymous Users '''
            if user.role == 'anonymous' or user.role == 'user':
                #print('allowed id: '+user.id,flush=True)
                registration_tokens.append(user.token)
        
        cnt=0
        response = ''      
        if len(registration_tokens) > 0:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title= announcement.title,
                    body= announcement.body,
                ),
                data={
                    'navigation': '/announcements', 
                    'id': '{}'.format(id)
                },
                tokens=registration_tokens,
            )
            response = messaging.send_multicast(message)
            cnt = response.success_count
            return cnt, 201
    
topic_arguments = reqparse.RequestParser()
topic_arguments.add_argument('topic', type=str, required=True, help='topic name')
topic_arguments.add_argument('id', type=str, required=True, help='announcement id')
@namespace2.response(500, 'Internal Server error')
@namespace2.route('/topicmessage')
class Topic(Resource):
    @namespace2.expect(topic_arguments, validate=True)
    @token_required
    def get(self):
        '''Sends an announcement as push notification to a given topic'''
            
        args = topic_arguments.parse_args()
        topic = args.get('topic')
        id = args.get('id')

        ''' Get announcement from db '''
        announcement = service.getItem(id)
        
        message = messaging.Message(
            notification=messaging.Notification(
                title= announcement.title,
                body= announcement.body,
            ),
            data={
                'navigation': '/announcements', 
                'id': '{}'.format(id)
            },
            topic = topic,
        )

        response = messaging.send(message)  
        return response, 201

def isNotBlank (myString):
    return bool(myString and myString.strip())