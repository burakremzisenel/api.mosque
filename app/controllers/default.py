#!/usr/bin/env python
# coding: latin1
from flask import Blueprint, jsonify, request

import services.service as service
from models.announcements import Announcements
from models.user import User


import json

import os
from config import app
from flask import make_response
from flask import Response
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

blueprint = Blueprint('default', __name__, url_prefix='/api/v1.0')
   
""" Gets All Announcements """
@blueprint.route('/announcements/all', methods=['GET'])
@firebase.jwt_required
def get_all():
    ''' Get all entities'''
    #print('get all entities')
    nList = service.get_all()
    return jsonify([announcements.as_dict() for announcements in nList])

""" Gets Image """
@blueprint.route('/img/<string:filename>', methods=['GET'])
def get_image(filename):
    if request.method == 'GET':
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

""" Uploads Image & Item """
@blueprint.route('/img/upload', methods=['POST'])
@firebase.jwt_required
def upload_file():
    if request.method == 'POST':

        try:
            # save image
            file = request.files['image']
            filename = (file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # save content to db
            content = json.loads(request.form.get('content'))
            announcements = service.post((content))

            #response
            msg = json.dumps({'success': True})
            resp = Response(msg, status=200, mimetype='application/json')
            #resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

        except Exception as e:
            msg = json.dumps({'success': False, 'msg':str(e)})
            resp = Response(msg, status=500, mimetype='application/json')
            return resp

    else:
        msg = json.dumps({'success': False, 'msg':'HTTPException'})
        resp = Response(msg, status=500, mimetype='application/json')
        #resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

""" Updates Item """
@blueprint.route('/announcements/<string:id>', methods=['PUT'])
@firebase.jwt_required
def api_put(id):
    ''' Update entity by id'''
    body = request.json
    body['id'] = int( id )
    res = service.put(body)
    return jsonify(res.as_dict()) if isinstance(res, Announcements) else jsonify(res)

""" Deleted Item """
@blueprint.route('/announcements/<string:id>', methods=['DELETE'])
@firebase.jwt_required
def api_delete(id):
    ''' Delete entity by id'''
    itemToDelete = service.get(id)
    items = service.getItemsByImageName(itemToDelete.image)
    if len( items ) == 1:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], itemToDelete.image))
    res = service.delete(id)
    return jsonify(res)

""" Sends Message by User ID """
@blueprint.route('/sendMessage', methods=['POST'])
@firebase.jwt_required
def send_message_by_id():
    if request.method == 'POST':
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
            print(u'No such document!')
            
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
        
        return jsonify({"success":True, "data": response})

""" Sends Multicast Message """
@blueprint.route('/sendMulticastMessage/<string:announcementID>', methods=['GET'])
@firebase.jwt_required
def send_multicast_message(announcementID):
        
    ''' Get announcement from db '''
    announcement = service.getItem(announcementID)
    
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
                'id': '{}'.format(announcementID)
            },
            tokens=registration_tokens,
        )
        response = messaging.send_multicast(message)
        cnt = response.success_count
    
    return jsonify({"success":True, "cnt": cnt})
    
""" Sends Topic Message """
@blueprint.route('/sendTopicMessage/<string:topicName>/<string:announcementID>', methods=['GET'])
@firebase.jwt_required
def send_topic_message(topicName, announcementID):
        
    ''' Get announcement from db '''
    announcement = service.getItem(announcementID)
    
    message = messaging.Message(
        notification=messaging.Notification(
            title= announcement.title,
            body= announcement.body,
        ),
        data={
            'navigation': '/announcements', 
            'id': '{}'.format(announcementID)
        },
        topic = topicName,
    )

    response = messaging.send(message)  
    
    return jsonify({"success":True, "data": response})
 
""" Error Handler """
@blueprint.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON format for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        'success': False,
        "message": e.description
    })
    response.content_type = "application/json"
    return response

def isNotBlank (myString):
    return bool(myString and myString.strip())