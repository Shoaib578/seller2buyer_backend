from application import db,app
from flask import Flask,request,Blueprint,jsonify
from application.models import RecentChats,RecentChatsSchema,Notifications,NotificationsSchema,Messages,MessagesSchema
from werkzeug.security import generate_password_hash,check_password_hash

import os
from sqlalchemy import text
from datetime import datetime
from werkzeug.utils import secure_filename
import smtplib
import random
import requests


def save_file(file, type):
    file_name = secure_filename(file.filename)
    file_ext = file_name.split(".")[1]
    folder = os.path.join(app.root_path, "static/" + type + "/")
    file_path = os.path.join(folder, file_name)
    try:
        file.save(file_path)
        return True, file_name
    except:
        return False, file_name



def InsertRecentChats(my_id,user_id):
    recent_chat = RecentChats.query.filter_by(recent_chat=user_id,recent_chat_for=my_id).first()
    if recent_chat:
        return jsonify({'msg':'already exist'})
    else:
        recent_chat = RecentChats(recent_chat=user_id,recent_chat_for=my_id)
        db.session.add(recent_chat)
        db.session.commit()


def GetRecentChats():
    my_id = request.args.get('my_id')
    recent_chats_sql = text("SELECT * FROM recent_chats LEFT JOIN users on users.id=recent_chats.recent_chat WHERE  recent_chat_for="+str(my_id))
    recent_chats_query = db.engine.execute(recent_chats_sql)
    recent_chats_schema = RecentChatsSchema(many=True)
    recent_chats = recent_chats_schema.dump(recent_chats_query)
    
    return jsonify({'recent_chats':recent_chats})




def InsertNotification(not_for,created_by,text):
    notification = Notifications(notification_for=not_for,notification_created_by=created_by,text=text,is_seen=0)
    db.session.add(notification)
    db.session.commit()
    return jsonify({
        "msg":"notification inserted"
    })


def SendMessage():
    image = request.files.get('image')
    msg_txt = request.form.get('msg')
    inserted_by = request.form.get('inserted_by')
    msg_for = request.form.get('msg_for')
    msg=''
    if image:
        save_file(image,'message_images')
        msg = Messages(sended_by=inserted_by,text=msg_txt,media=image.filename,reciever=msg_for,posted_date=datetime.now())

    else:
        msg = Messages(sended_by=inserted_by,text=msg_txt,media='',reciever=msg_for,posted_date=datetime.now())

    InsertRecentChats(msg_for,inserted_by)
    InsertNotification(msg_for,inserted_by,'Sent You a Message')


    db.session.add(msg)
    db.session.commit()
    return jsonify({'msg':'Message has been inserted'})

def SeeMessagesNotifications():
    my_id = request.args.get('my_id')
    user_id= request.args.get('user_id')
    my_notifications = Notifications.query.filter_by(is_seen=0,notification_for=my_id,text="Sent You a Message",notification_created_by=user_id)
    if my_notifications.count() >0:
        check = Notifications.query.filter_by(is_seen=0,notification_for=my_id).all()
        for seen in check:
            
            seen.is_seen = 1
            db.session.commit()
            
    else:
        return jsonify({'msg':'No Notifications'})

    return jsonify({'msg':'checked'})



def GetMessages():
    my_id = request.args.get('my_id')
    user_id = request.args.get('user_id')
    
    get_msg_sql = text("SELECT * FROM messages LEFT JOIN users on id=messages.reciever WHERE  reciever="+str(user_id)+" OR sended_by="+str(user_id))
    get_msg_query = db.engine.execute(get_msg_sql)
    msgSchema = MessagesSchema(many=True)
    msgs = msgSchema.dump(get_msg_query)
    SeeMessagesNotifications()
    return jsonify({'msgs':msgs})

