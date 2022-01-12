from application import db,app
from flask import Flask,request,Blueprint,jsonify
from application.models import *
from werkzeug.security import generate_password_hash,check_password_hash
from twilio.rest import Client

import os
from sqlalchemy import text
from datetime import datetime
from werkzeug.utils import secure_filename
import smtplib
import random
import requests

account_sid = 'ACd820a45f33eb7218a944714763d8dbbb'
auth_token = 'b60b8a0b7ad5c7550063858bef9506ee'
client = Client(account_sid, auth_token)


def SignUp():
    role = request.form.get('role')
    phone_number = request.form.get('phone_number')

    if role == 'seller':
        company_name = request.form.get('company_name')
        make_your_product_visible_to_everyone = request.form.get('make_your_product_visible_to_everyone')
        email = request.form.get('email')
        password = request.form.get('password')
        primary_contact = request.form.get('primary_contact')
        postal_code = request.form.get('postal_code')
        hash_pw = generate_password_hash(password)
        user = Users.query.filter_by(phone_no=phone_number).first()
        if user:
            return jsonify({
                "msg":"Phone Number Already Exists.Please Try Another One"
            })
        else:
            user = Users(email=email, phone_no=phone_number,make_your_product_visible_to_everyone=make_your_product_visible_to_everyone,companyname=company_name,password=hash_pw,primary_contact=primary_contact,role='seller',postal_code=postal_code)
            db.session.add(user)
            db.session.commit()
            return jsonify({
                "msg":"User Registered Successfully"
            })

    else:
        user = Users.query.filter_by(phone_no=phone_number).first()
        if user:
            return jsonify({
                "msg":"Phone Number Already Exists.Please Try Another One"
            })
        else:
            firstname = request.form.get('first_name')
            lastname = request.form.get('last_name')
            password = request.form.get('password')
            
            
            primary_contact = request.form.get('primary_contact')
            postal_code = request.form.get('postal_code')
            hash_pw = generate_password_hash(password)
            
            user = Users(phone_no=phone_number, primary_contact=primary_contact, postal_code=postal_code,firstname=firstname, lastname=lastname, password=hash_pw,role=role)
            db.session.add(user)
            db.session.commit()
            return jsonify({
                "msg":"User Registered Successfully"
            })



def SendOTP():
    
    phone_no = request.form.get('phone_no')
    user = Users.query.filter_by(phone_no=phone_no).first()
    if user:
        return jsonify({
            "msg":"User Already Exist"
        })
    else:

        random_v = 0
        for rand in random.sample(range(1000, 2000),4):
            random_v =  rand
        message = client.messages.create(
        
            from_='whatsapp:14155238886',
            body="Your Manish App varification code is "+str(random_v),
            to='whatsapp:'+str(phone_no)
            )
        return jsonify({
            "otp":random_v,
            "msg":"success"
        })

def SignIn():
    phone_no = request.form.get('phone_no')
  
    


    password = request.form.get('password')
    
    user = Users.query.filter_by(phone_no=phone_no).first()
    if user and check_password_hash(user.password,password) and user.role !="admin":
        users_schema = UsersSchema(many=False)
        user = users_schema.dump(user)
        
       
        return jsonify({
            "user":user,
          
            "msg":"success"
        })
    else:
        return jsonify({
            "msg":"not found"
        })



def ForgotPassword():
    phone_no = request.form.get('phone_no')
    random_v = 0
    for rand in random.sample(range(1000, 2000),4):
        random_v =  rand
    user = Users.query.filter_by(phone_no=phone_no).first()
    if user:
        message = client.messages.create(
        
            from_='whatsapp:14155238886',
            body="Your Manish App varification code is "+str(random_v),
            to='whatsapp:'+str(phone_no)
            )
        return jsonify({
            "msg":"success",
            "otp":random_v,
            "user_id":user.id
        })
    else:
        return jsonify({
            "msg":"Phone Number Not Found"
        })


def  CreateNewPassword():
    user_id = request.form.get('user_id')
    user = Users.query.filter_by(id=user_id).first()
    user.password = generate_password_hash(request.form.get('password'))
    db.session.commit()
    return jsonify({
        "msg":"success"
    })
def Profile():
    user_id = request.args.get('user_id')
    user = Users.query.filter_by(id=user_id).first()
    users_schema = UsersSchema(many=False)
    user = users_schema.dump(user)
    return jsonify({
        "user":user
    })

def GetAllCountries():
    countries = Countries.query.all()
    country_schema = CountriesSchema(many=True)
    all_countries = country_schema.dump(countries)
    return jsonify({
        "countries":all_countries
    })


def GetAllSubscriptions():
    subscriptions = Subscriptions.query.all()
    subscriptions_schema = SubscriptionsSchema(many=True)
    subs = subscriptions_schema.dump(subscriptions)
    return jsonify({
        "subs":subs,
    })

def CheckMySubscription():
    my_id = request.args.get('my_id')
    subscription = text("select *,(select count(*) from user_subscription where user_id="+str(my_id)+" and NOW() <= DATE(expiration_date) ) as has_susbs  from users where id="+str(my_id)+"")
    engine = db.engine.execute(subscription)
    user_subscription_schema = UsersSchema(many=True)
    check  = user_schema = user_subscription_schema.dump(engine)
    return jsonify({
        "check":check,
    })

def BuySubscription():
    user_id = request.form.get('user_id')
    duration = request.form.get('duration')
    # DATE_ADD(NOW(), INTERVAL "+str(duration)+" DAY)
    subscription = text("INSERT INTO user_subscription(user_id,start_date,expiration_date) VALUES("+str(user_id)+",NOW(),DATE_TRUNC('DAY',NOW())+INTERVAL '30 DAY' )")
    engine = db.engine.execute(subscription)
    return jsonify({
        "msg":"You Have Bought Subscription Successfully",
    })

def GetMySubscription():
    user_id =request.args.get('user_id')
    subscription = text("select  DATE_PART('day',expiration_date-NOW()) AS remaing_time, expiration_date,start_date,user_subscription_id   from  user_subscription  where user_id="+str(user_id)+" AND NOW() <= DATE(expiration_date) ")
    engine = db.engine.execute(subscription)
    user_subscription_schema = UserSubscriptionSchema(many=True)
    sub = user_subscription_schema.dump(engine)
    return jsonify({
        "subscriptions":sub
    })


def UpdateProfile():
    user_id = request.form.get('user_id')
    user = Users.query.filter_by(id=user_id).first()
    print(user_id)
    if user.role == 'seller':
        company_name = request.form.get('company_name')
        make_product_visible  = request.form.get('make_product_visible')
        primary_contact = request.form.get('primary_contact')
        email = request.form.get('email')
        phone_no = request.form.get('phone_no')
        make_your_product_visible_to_everyone = request.form.get('make_your_product_visible_to_everyone')
        user.companyname = company_name
        user.make_your_product_visible_to_everyone = make_product_visible
        user.make_your_product_visible_to_everyone = make_your_product_visible_to_everyone
        user.email = email
        user.phone_no = phone_no
        user.primary_contact = primary_contact
        db.session.commit()
        return jsonify({
            "msg":"User Profile Update Successfully"

        })
    elif user.role == 'buyer':
        firstname = request.form.get("firstname")
        phone_no = request.form.get("phone_no")
        primary_contact = request.form.get("primary_contact")
        postal_code = request.form.get("postal_code")
        user.firstname = firstname
        user.phone_no = phone_no
        user.primary_contact = primary_contact
        user.postal_code = postal_code
        db.session.commit()
        return jsonify({
            "msg":"User Profile Update Successfully"
        })