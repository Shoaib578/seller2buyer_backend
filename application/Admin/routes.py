from application import app,db
import os
from sqlalchemy import text
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash

from flask import Flask,request,Blueprint,jsonify,flash,render_template,redirect,url_for
from application.Admin.forms import LoginForm
from application.models import *

from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import text
import random
import razorpay
admin = Blueprint('admin', __name__,static_folder='../static')

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





@admin.route('/',methods=['GET','POST'])
@login_required

def Home():
    

    hash_pw = generate_password_hash('Games587')

    if Users.query.filter_by(role='admin').count()==1:

        pass
    else:
        
        admin = Users(email='theadmin21@gmail.com',password=hash_pw,firstname="admin",role='admin')
        db.session.add(admin)
        db.session.commit()

    if request.method == 'POST':
        
        name = request.form.get('name')
        email = request.form.get('email')
        amount = request.form.get('amount')
        
        supplier_payment = SupplierPayments(supplier_name= name,supplier_email= email,amount= amount,payment_date = datetime.now())
        db.session.add(supplier_payment)
        db.session.commit()
        return redirect(url_for('admin.Pay',id=supplier_payment.payment_id))

    return render_template('home.html')





@admin.route('/login',methods=['GET', 'POST'])
def Login():
    useremail = request.form.get('useremail')
    userpassword = request.form.get('userpassword')
    hash_pw = generate_password_hash('Games587')

    if Users.query.filter_by(role='admin').count()==1:

        pass
    else:
        
        admin = Users(email='theadmin21@gmail.com',password=hash_pw,firstname="admin",role='admin')
        db.session.add(admin)
        db.session.commit()
        
  
    if current_user.is_authenticated:
        return redirect(url_for('admin.Home'))
    
    user = Users.query.filter_by(email=useremail).first()

    if request.method == 'POST':
        if user and check_password_hash(user.password,userpassword) and user.role == 'admin': 
            login_user(user, True)
            return redirect(url_for('admin.Home'))

        
    return render_template('login.html')





@admin.route('/logout')
@login_required
def Logout():
    logout_user()
    return redirect(url_for('admin.Login'))


@admin.route('/add_category', methods=['GET', 'POST'])
@login_required

def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        new_category = Categories(category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
    all_categories = Categories.query.all()
    return render_template('categories.html', all_categories=all_categories)


@admin.route('/delete_category/<int:id>', methods=['POST'])
@login_required

def delete_category(id):
    if request.method == 'POST':
        category_name = Categories.query.get(id)
        db.session.delete(category_name)
        db.session.commit()
        return redirect(url_for('admin.add_category'))

@admin.route('/get_products', methods=['GET'])
@login_required

def get_products():
    all_products = Products.query.all()
    products_count = Products.query.count()
    return render_template('products.html', all_products=all_products,products_count=products_count)


@admin.route('/delete_product/<int:id>', methods=['POST'])
@login_required

def delete_product(id):
    if request.method == 'POST':
        product_name = Products.query.get(id)
        remove_file(product_name.product_picture1,"uploads")
        remove_file(product_name.product_picture2,"uploads")
        remove_file(product_name.product_picture3,"uploads")

        db.session.delete(product_name)
        db.session.commit()
        return redirect(url_for('admin.get_products'))


@admin.route('/get_sellers', methods=['GET'])
@login_required

def get_sellers():
    sql = text("SELECT *,(SELECT count(*) FROM users WHERE role='seller') as sellers_count FROM users WHERE role = 'seller'")
    all_sellers = db.engine.execute(sql)
    sellers_schema = UsersSchema(many=True)
    sellers = sellers_schema.dump(all_sellers)
    sellers_count = Users.query.filter_by(role='seller').count()
    return render_template('sellers.html', all_sellers=sellers,sellers_count=sellers_count)


@admin.route('/delete_seller/<int:id>', methods=['POST'])
@login_required

def delete_seller(id):
    if request.method == 'POST':
        seller = Users.query.get(id)
        db.session.delete(seller)
        db.session.commit()
        return redirect(url_for('admin.get_sellers'))


@admin.route('/get_buyers', methods=['GET'])
@login_required
def get_buyers():
    sql = text("SELECT *,(SELECT count(*) FROM users WHERE role='buyer') as buyers_count FROM users WHERE role = 'buyer'")
    all_buyers = db.engine.execute(sql)
    buyers_schema = UsersSchema(many=True)
    buyers = buyers_schema.dump(all_buyers)
    buyers_count = Users.query.filter_by(role="buyer").count()
    return render_template('buyers.html', all_buyers=buyers,buyers_count=buyers_count)

@admin.route('/delete_buyer/<int:id>', methods=['POST'])
@login_required
def delete_buyer(id):
    if request.method == 'POST':
        buyer = Users.query.get(id)
        db.session.delete(buyer)
        db.session.commit()
        return redirect(url_for('admin.get_buyers'))




@admin.route('/orders', methods=['GET','POST'])
@login_required

def Orders():

    sql = text("SELECT * FROM placed_orders LEFT JOIN cart on cart.cart_id=placed_orders.order_cart_id  WHERE is_accepted=1")
    engine = db.engine.execute(sql)
    placed_order_schema = PlacedOrdersSchema(many=True)
    placed_orders = placed_order_schema.dump(engine)
    orders_count = PlacedOrders.query.filter_by(is_accepted=1).count()

    return render_template('placedorders.html',orders=placed_orders,orders_count=orders_count)




@admin.route('/completed_orders',methods=['POST','GET'])
@login_required
def CompletedOrders():
    sql = text("SELECT * FROM placed_orders LEFT JOIN cart on cart.cart_id=placed_orders.order_cart_id  WHERE is_completed=1")
    engine = db.engine.execute(sql)
    placed_order_schema = PlacedOrdersSchema(many=True)
    placed_orders = placed_order_schema.dump(engine)
    orders_count = PlacedOrders.query.filter_by(is_completed=1).count()

    return render_template('completed_orders.html',orders=placed_orders,orders_count=orders_count)


@admin.route("/delete_completed_order/<int:id>",methods=[ "POST"])
@login_required

def DeleteCompleteOrder(id):
    order = PlacedOrders.query.filter_by(placed_order_id=id).first()
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('admin.Orders'))


@admin.route('/countries',methods=[ "GET", "POST"])
@login_required
def Country():
    if request.method == 'POST':
        country_name = request.form.get('country_name')
        country = Countries(name=country_name)
        db.session.add(country)
        db.session.commit()
        return redirect(url_for('admin.Country'))
    all_countries = Countries.query.all()
    return render_template('countries.html',countries=all_countries)



@admin.route('/delete_country/<int:id>',methods=['POST'])
def DeleteCountry(id):
    country = Countries.query.get(id)
    db.session.delete(country)
    db.session.commit()
    return redirect(url_for('admin.Country'))


@admin.route('/subscriptions',methods=['GET', 'POST'])
def Subscription():
    if request.method == 'POST':
        duration = request.form.get('duration')
        price = request.form.get('price')
        subscription = Subscriptions(duration=duration, price=price)
        db.session.add(subscription)
        db.session.commit()
        return redirect(url_for('admin.Subscription'))
    subscriptions = Subscriptions.query.all()
    return render_template('subscriptions.html',subscriptions=subscriptions)


@admin.route('/delete_subscription/<int:id>', methods=['POST'])
def DeleteSubscription(id):
    subscription = Subscriptions.query.get(id)
    db.session.delete(subscription)
    db.session.commit()
    return redirect(url_for('admin.Subscription'))