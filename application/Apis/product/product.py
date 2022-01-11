from application import db,app
from flask import Flask,request,Blueprint,jsonify
from application.models import *
from werkzeug.security import generate_password_hash,check_password_hash

import os
from sqlalchemy import text
from datetime import datetime
from werkzeug.utils import secure_filename
import smtplib
import random
import requests



def remove_file(file, type):
    file_name = file
    folder = os.path.join(app.root_path, "static/" + type + "/"+file_name)
    os.remove(folder)
    return 'File Has Been Removed'


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


def InsertNotification(not_for,created_by,text):
    notification = Notifications(notification_for=not_for,notification_created_by=created_by,text=text,is_seen=0)
    db.session.add(notification)
    db.session.commit()
    return jsonify({
        "msg":"notification inserted"
    })


def GetAllNotifications():
    my_id =request.args.get('my_id')
    notifications = text("SELECT *,(SELECT count(*) from notifications where notification_for="+str(my_id)+" AND is_seen=0) as notification_count FROM notifications LEFT JOIN users on users.id=notification_created_by  WHERE notification_for="+str(my_id)+"  ORDER BY notification_id DESC")
    query = db.engine.execute(notifications)
    notification_schema = NotificationsSchema(many=True)
    notifications = notification_schema.dump(query)
    return jsonify({
        "notifications":notifications
    })


def GetAllNotificationsCount():
    my_id =request.args.get('my_id')
    notifications = text("SELECT *,(SELECT count(*) from notifications where notification_for="+str(my_id)+" AND is_seen=0) as notification_count FROM notifications LEFT JOIN users on users.id=notification_created_by  WHERE notification_for="+str(my_id)+" AND is_seen=0  ORDER BY notification_id DESC")
    query = db.engine.execute(notifications)
    notification_schema = NotificationsSchema(many=True)
    notifications = notification_schema.dump(query)
    return jsonify({
        "notifications":notifications
    })

def SeeNotification():
    my_id = request.args.get('my_id')
    my_notifications = Notifications.query.filter_by(is_seen=0,notification_for=my_id)
    if my_notifications.count() >0:
        check = Notifications.query.filter_by(is_seen=0,notification_for=my_id).all()
        for seen in check:
            
            seen.is_seen = 1
            db.session.commit()
            
    else:
        return jsonify({'msg':'No Notifications'})

    return jsonify({'msg':'checked'})
    

def DeleteNotification():
    notification_id = request.args.get('notification_id')
    notification = Notifications.query.filter_by(notification_id=notification_id).first()
    db.session.delete(notification)
    db.session.commit()
    return jsonify({"msg":'deleted'})

def AddProduct():
    product_title = request.form.get('product_title')
    product_description = request.form.get('product_description')
   
    price = request.form.get('price')
    sku_code = request.form.get('sku_code')
    hsn_code = request.form.get('hsn_code')
    category = request.form.get('category')
    tax_tier = request.form.get('tax_tier')
    stock_keeping_unit = request.form.get('stock_keeping_unit')
    
    ordering_unit = request.form.get('ordering_unit')
    moq = request.form.get('moq')
    tags = request.form.get('tags')
    posted_by = request.form.get('posted_by')
    product_image1 = request.files.get('product_image1')
    product_image2 = request.files.get('product_image2')
    product_image3 = request.files.get('product_image3')
    
    save_file(product_image1,'uploads')
    save_file(product_image2,'uploads')
    save_file(product_image3,'uploads')

    product = Products(
        posted_by=posted_by,posted_date=datetime.now(),
        product_name=product_title,product_description=product_description,
        sku_code=sku_code,hsn_code=hsn_code,
        moq=moq,product_picture1=product_image1.filename,product_picture2=product_image2.filename,
        product_picture3=product_image3.filename,price=price,tags=tags,
        stock_keeping_unit=stock_keeping_unit,tax_tier=tax_tier,order_unit=ordering_unit,category=category


    )
    db.session.add(product)
    db.session.commit()
    return jsonify({
        "msg":"success"
    })





def Index():
    my_id = request.args.get('my_id')
    offset = request.args.get('offset')
   
    products_sql = text("SELECT *,(SELECT count(*) FROM favorite_products WHERE  favorite_products.favorite_by="+str(my_id)+" AND favorite_products.favorite_product_id=products.product_id) as is_favorite  FROM products  LEFT JOIN users on users.id=posted_by WHERE posted_by !="+str(my_id)+" AND users.make_your_product_visible_to_everyone=1 order by product_id DESC  LIMIT 5 OFFSET "+str(offset))
    query = db.engine.execute(products_sql)
    product_schema = ProductSchema(many=True)
    products = product_schema.dump(query)
    
    return jsonify({'products':products})


def DeleteProduct():
    id = request.args.get('id')
    product_name = Products.query.get(id)
    remove_file(product_name.product_picture1,"uploads")
    remove_file(product_name.product_picture2,"uploads")
    remove_file(product_name.product_picture3,"uploads")
    db.session.delete(product_name)
    db.session.commit()
    return jsonify({
        "msg":"Product Deleted Successfully"
    })



def SearchProduct():
    search = request.args.get('search')
    my_id = request.args.get('my_id')
    offset = request.args.get('offset')
    products_sql = text("SELECT *,(SELECT count(*) FROM favorite_products WHERE  favorite_products.favorite_by="+str(my_id)+" AND favorite_products.favorite_product_id=products.product_id) as is_favorite  FROM products  LEFT JOIN users on users.id=posted_by AND users.make_your_product_visible_to_everyone=1 WHERE product_name LIKE'%"+str(search)+"%'   AND posted_by !="+str(my_id)+" order by product_id DESC LIMIT 5 OFFSET "+str(offset))
    query = db.engine.execute(products_sql)
    product_schema = ProductSchema(many=True)
    products = product_schema.dump(query)
    
    return jsonify({'products':products})

def MyProducts():
    my_id = request.args.get('my_id')
    offset = request.args.get('offset')
    products_sql = text("SELECT *,(SELECT count(*) FROM favorite_products WHERE  favorite_products.favorite_by="+str(my_id)+" AND favorite_products.favorite_product_id=products.product_id) as is_favorite   FROM products LEFT JOIN users on users.id=posted_by WHERE posted_by = "+str(my_id)+" order by product_id DESC  LIMIT 5 OFFSET "+str(offset) )
    query = db.engine.execute(products_sql)
    product_schema = ProductSchema(many=True)
    products = product_schema.dump(query)
    return jsonify({'products':products})


def MyFavoriteProducts():

    my_id = request.args.get('my_id')
    offset = request.args.get('offset')
    products_sql = text("SELECT *,(SELECT count(*) FROM favorite_products WHERE  favorite_products.favorite_product_id=products.product_id AND favorite_products.favorite_by="+str(my_id)+") as is_favorite from favorite_products LEFT JOIN products on products.product_id=favorite_products.favorite_product_id LEFT JOIN users on users.id=products.posted_by order by favorite_id DESC  LIMIT 5 OFFSET "+str(offset))
    query = db.engine.execute(products_sql)
    product_schema = ProductSchema(many=True)
    products = product_schema.dump(query)
    return jsonify({'products':products})


def MakeProductFavorite():
    my_id = request.form.get('my_id')
    product_id = request.form.get('product_id')
    favorite = FavoriteProducts.query.filter_by(favorite_by=my_id,favorite_product_id=product_id).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'msg':'unfavorite'})
    else:
        favorite = FavoriteProducts(favorite_by=my_id,favorite_product_id=product_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'msg':'favorite'})


def  ViewProduct():
    product_id = request.args.get('product_id')
    my_id = request.args.get('my_id')
    
    products_sql = text("SELECT *,(SELECT count(*) FROM favorite_products WHERE  favorite_products.favorite_by="+str(my_id)+" AND favorite_products.favorite_product_id=products.product_id) as is_favorite   FROM products LEFT JOIN users on users.id=posted_by WHERE product_id = "+str(product_id))
    query = db.engine.execute(products_sql)
    product_schema = ProductSchema(many=True)
    products = product_schema.dump(query)
    return jsonify({'product':products})



def AddToCartProduct():
    product_id = request.form.get('product_id')
    user_id = request.form.get('user_id')
    quantity = request.form.get('quantity')
    cart = Cart(product_id=product_id, user_id=user_id,quantity=quantity)
    db.session.add(cart)
    db.session.commit()
    return jsonify({'msg':'The product is added To cart'})


def GetCartProducts():
    user_id = request.args.get('user_id')
    products = text("SELECT *,(SELECT count(*) FROM favorite_products WHERE  favorite_products.favorite_by="+str(user_id)+" AND favorite_products.favorite_product_id=products.product_id) as is_favorite,(SELECT count(*) from placed_orders where placed_orders.order_cart_id=cart.cart_id) as is_placed  FROM cart LEFT JOIN products on products.product_id=cart.product_id LEFT JOIN users on users.id=products.posted_by WHERE cart.user_id="+str(user_id))
    engine = db.engine.execute(products)
    cart_schema = CartSchema(many=True)
    cart = cart_schema.dump(engine)
    return jsonify({'cart':cart})


def RemoveFromCartProduct():
    cart_id = request.args.get('cart_id')
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    db.session.delete(cart)
    db.session.commit()
    return jsonify({'msg':'Deleted'})


def PlaceOrder():
    placed_by = request.args.get('placed_by')
    cart_id = request.args.get('cart_id')
    owner_id = request.args.get('owner_id')
    product_id = request.args.get('product_id')
    address = request.args.get('address')
    order = PlacedOrders(order_cart_id=cart_id,placed_by=placed_by,posted_date=datetime.now(),owner_id=owner_id,is_accepted=0,is_completed=0,order_product_id=product_id,is_rejected=0,placed_order_address=address)
    db.session.add(order)
    db.session.commit()
    InsertNotification(owner_id,placed_by,'Placed Order For Your Product')
    return jsonify({'msg':'order has been placed successfully'})



def GetAllPendingOrderFromBuyer():
    my_id = request.args.get('my_id')
    orders_query = text("SELECT * FROM placed_orders LEFT JOIN cart on cart.cart_id=placed_orders.order_cart_id LEFT JOIN users on users.id=placed_orders.placed_by LEFT JOIN products on products.product_id=order_product_id WHERE owner_id="+str(my_id)+" AND is_rejected=0")
    engine = db.engine.execute(orders_query)
    placed_orders_schema = PlacedOrdersSchema(many=True)
    placed_orders = placed_orders_schema.dump(engine)
    return jsonify({'placed_orders':placed_orders})

def AcceptOrderFromBuyer():
    order_id = request.args.get('order_id')
    order = PlacedOrders.query.filter_by(placed_order_id=order_id).first()
    order.is_accepted = 1
    db.session.commit()
    InsertNotification(order.placed_by,order.owner_id,'Accepted Your Order')
    return jsonify({'msg':'accepted'})



def DeletePlacedOrder():
    order_id = request.args.get('order_id')
    order = PlacedOrders.query.filter_by(placed_order_id=order_id).first()
    cart = Cart.query.filter_by(cart_id=order.order_cart_id).first()
    db.session.delete(cart)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"msg":"order deleted"})

def RejectOrderFromBuyer():
    order_id = request.args.get('order_id')
    order = PlacedOrders.query.filter_by(placed_order_id=order_id).first()
    order.is_rejected = 1
    db.session.commit()
    InsertNotification(order.placed_by,order.owner_id,'Rejected Your Order')

    return jsonify({'msg':'request'})

def MyPlacedOrders():
    my_id = request.args.get('my_id')
    orders_query = text("SELECT * FROM placed_orders LEFT JOIN cart on cart.cart_id=placed_orders.order_cart_id LEFT JOIN users on users.id=placed_orders.owner_id LEFT JOIN products on products.product_id=order_product_id WHERE placed_by="+str(my_id))
    engine = db.engine.execute(orders_query)
    placed_orders_schema = PlacedOrdersSchema(many=True)
    placed_orders = placed_orders_schema.dump(engine)
    return jsonify({'placed_orders':placed_orders})



def GetAllCategories():
    categories = Categories.query.all()
    categories_schema = CategoriesSchema(many=True)
    all_categories = categories_schema.dump(categories)
    return jsonify({'all_categories':all_categories})


def CompleteOrder():
    order_id = request.args.get('order_id')
    order = PlacedOrders.query.filter_by(placed_order_id=order_id).first()
    order.is_completed = 1
    order.is_accepted = 0
    db.session.commit()
    InsertNotification(order.placed_by,order.owner_id,'Completed Your Order')
    return jsonify({
        "msg":"order completed"
    })

