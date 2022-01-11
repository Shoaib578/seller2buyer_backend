from application import db,login_manager,ma
from flask_login import UserMixin
import datetime 


@login_manager.user_loader
def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
    return Users.query.get(int(user_id))



class Users(db.Model,UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100),nullable=True)
    firstname = db.Column(db.String(100),nullable=True)
    lastname = db.Column(db.String(100),nullable=True)
    companyname = db.Column(db.String(100),nullable=True)
    make_your_product_visible_to_everyone = db.Column(db.Integer,nullable=True)
    password = db.Column(db.String(200),nullable=False)
    phone_no = db.Column(db.String(100),nullable=True)
    role = db.Column(db.String(100),nullable=True)
    primary_contact = db.Column(db.String(100),nullable=True)
    postal_code = db.Column(db.String(100),nullable=True)

    
class UsersSchema(ma.Schema):
    class Meta:
        fields = ('id','email','password','phone_no','make_your_product_visible_to_everyone','firstname','has_susbs','lastname','companyname','role','primary_contact','postal_code','sellers_count','buyers_count')




class Products(db.Model):
    product_id = db.Column(db.Integer,primary_key=True)
    posted_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    posted_date = db.Column(db.Date())
    product_name = db.Column(db.String(200))
    product_description = db.Column(db.String(1000))
    
    sku_code = db.Column(db.String(100))
    moq = db.Column(db.String(100))
    product_picture1 = db.Column(db.String(200))
    product_picture2 = db.Column(db.String(200))
    product_picture3 = db.Column(db.String(200))
    price = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    stock_keeping_unit = db.Column(db.String(100))
  
    tax_tier = db.Column(db.String(100))
    order_unit = db.Column(db.String(100))
    hsn_code = db.Column(db.String(100))
    category = db.Column(db.String(100))
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('product_id','product_name','make_your_product_visible_to_everyone','product_description','is_favorite','quality_description','posted_by','sku_code','hsn_code','product_picture1','product_picture2','product_picture3','moq','price','tags','stock_keeping_unit','variant','tax_tier','order_unit','posted_date','companyname','category','phone_no',)




class FavoriteProducts(db.Model):
    favorite_id = db.Column(db.Integer,primary_key=True)
    favorite_product_id = db.Column(db.Integer,db.ForeignKey('products.product_id',ondelete='CASCADE'))
    favorite_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))

class FavoriteProductsSchema(ma.Schema):
    class Meta:
        fields = ('favorite_id','favorite_product_id','favorite_by','is_favorite','product_id','product_name','product_description','is_favorite','quality_description','posted_by','sku_code','hsn_code','product_picture1','product_picture2','product_picture3','moq','price','tags','stock_keeping_unit','variant','tax_tier','order_unit','posted_date','companyname','category')


class PlacedOrders(db.Model):
    placed_order_id = db.Column(db.Integer(), primary_key=True)
    posted_date = db.Column(db.Date())
    owner_id = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    order_product_id = db.Column(db.Integer,db.ForeignKey('products.product_id',ondelete='CASCADE'))

    placed_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    order_cart_id = db.Column(db.Integer,db.ForeignKey('cart.cart_id',ondelete='CASCADE'))
    is_accepted = db.Column(db.Integer)
    is_completed = db.Column(db.Integer)
    is_rejected = db.Column(db.Integer)
    placed_order_address = db.Column(db.String(200))


class PlacedOrdersSchema(ma.Schema):
    class Meta:
        fields = ('placed_order_id','posted_date','placed_by','cart_id','is_favorite','is_accepted','is_completed','owner_id','order_product_id','product_id','user_id','product_name','product_description','is_placed','quality_description','posted_by','sku_code','hsn_code','product_picture1','product_picture2','product_picture3','moq','price','tags','stock_keeping_unit','variant','tax_tier','order_unit','posted_date','companyname','category','is_favorite','product_name','product_description','is_favorite','quality_description','posted_by','sku_code','hsn_code','product_picture1','product_picture2','product_picture3','moq','price','tags','is_rejected','firstname','lastname','placed_order_address','quantity')




class Cart(db.Model):
    cart_id = db.Column(db.Integer,primary_key=True)
    product_id = db.Column(db.Integer,db.ForeignKey('products.product_id',ondelete='CASCADE'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    quantity = db.Column(db.Integer)


class CartSchema(ma.Schema):
    class Meta:
        fields = ('cart_id','product_id','user_id','product_name','product_description','is_placed','quality_description','posted_by','sku_code','hsn_code','product_picture1','product_picture2','product_picture3','moq','price','tags','stock_keeping_unit','variant','tax_tier','order_unit','posted_date','companyname','category','is_favorite')


class Notifications(db.Model):
    notification_id = db.Column(db.Integer,primary_key=True)
    notification_created_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    notification_for = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    text= db.Column(db.String(100))
    is_seen = db.Column(db.Integer)
class NotificationsSchema(ma.Schema):
    class Meta:
        fields=("notification_id","notification_created_by",'notification_count',"notification_for","text","is_seen",'firstname','lastname','companyname')


class Messages(db.Model):
    message_id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(1000))
    media = db.Column(db.String(200))
    reciever = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    sended_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    posted_date = db.Column(db.Date())

class MessagesSchema(ma.Schema):
    class Meta:
        fields = ('message_id','text','media','reciever','sended_by','posted_date')
    



class RecentChats(db.Model):
    recent_chat_id = db.Column(db.Integer,primary_key=True)
    recent_chat = db.Column(db.Integer,db.ForeignKey('users.id'))
    recent_chat_for = db.Column(db.Integer,db.ForeignKey('users.id'))

class RecentChatsSchema(ma.Schema):
    class Meta:
        fields = ('recent_chat_id','recent_chat','recent_chat_for','companyname','firstname','lastname')


class Categories(db.Model):
    category_id = db.Column(db.Integer,primary_key=True)
    category_name = db.Column(db.String(100))

class CategoriesSchema(ma.Schema):
    class Meta:
        fields = ('category_id','category_name')



class Subscriptions(db.Model):
    subscription_id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer)
    price = db.Column(db.Integer)

class SubscriptionsSchema(ma.Schema):
    class Meta:
        fields = ('subscription_id','duration','price')


class UserSubscription(db.Model):
    user_subscription_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    start_date = db.Column(db.Date())
    expiration_date = db.Column(db.Date())

class UserSubscriptionSchema(ma.Schema):
    class Meta:
        fields = ("user_subscription_id","user_id","start_date","expiration_date",'remaing_time')



class Countries(db.Model):
    country_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class CountriesSchema(ma.Schema):
    class Meta:
        fields = ("country_id","name")