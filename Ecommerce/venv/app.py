from flask import Flask, jsonify,request, redirect, session
import psycopg2
from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, set_access_cookies,set_refresh_cookies,\
                                unset_refresh_cookies, JWTManager
from admin import admin
from user import user
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)
auth = HTTPBasicAuth()

app.config['SECRET_KEY'] = 'secretkey'

app.config["JWT_SECRET_KEY"] = "jwtsecretKey"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)

app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=20)

jwt = JWTManager(app)

def db_conn():
    conn = psycopg2.connect(database='sql_demo', host='localhost', user='postgres', password='postgres', port='5432') # always check the port number
    print(conn)
    print("Connection to database successful")
    return conn

@app.route("/")
def func():
    return "Hello world123456"


@app.route("/register", methods=['POST'])
def register():
    """To register the admin"""
    conn = db_conn()
    curr = conn.cursor()
    data = request.get_json()
    user = data["user"]["userName"]
    email = data["user"]["email"]
    phone = data["user"]["phoneNo"]
    pwd =data["user"]["password"]
    cpwd = data['user']['cPassword']
    role = "user"
    if cpwd == pwd:
        curr.execute("""SELECT * FROM admins
                 WHERE username = %s AND
                 email=%s AND phone=%s 
                 AND pwd=%s""",(user, email, phone, pwd))
        res = curr.fetchall()
    
        if len(res) == 0:
            curr.execute("""INSERT INTO admins(username, email, phone, pwd, role) 
                     VALUES (%s, %s, %s, %s, %s)""", (user, email, phone, pwd, role))
            conn.commit()
            curr.close(); conn.close()
            return jsonify(message='Register successful'), 200
        else:
            return jsonify(message="Username already exists"), 401
    else:
        return jsonify(message="password and confirm password are different!")

@app.route("/login", methods=['POST'])
def login():
    """Admin login"""
    conn = db_conn()
    curr = conn.cursor()
    data = request.get_json()
    email = data['user']['email']
    pwd = data['user']['password']
    
    curr.execute("""SELECT * FROM admins
                 WHERE email = %s
                 AND pwd=%s""",(email, pwd))
    res = curr.fetchall()
    curr.close(); conn.close()
    if len(res) == 1:
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        response = {"access_token":access_token,"role": res[0][5], "user": res[0][1], "refresh_token": refresh_token}
        response = jsonify(response)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200
    else:
        return jsonify(message="Incorrect username or password"), 401
    
@app.route('/logout')
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    unset_refresh_cookies(response)
    return response, 200


@app.route("/addcategory", methods=['POST'])
@jwt_required()
def addCategory():
    a = admin()
    data = request.get_json()
    print(data)
    name = data['category']
    print(name)
    res = a.addCategory(name)
    if res:
        return jsonify({"message": "New category created"}), 200
    else:
        return jsonify({"message": "New category not created"}), 401


@app.route("/addnewitem", methods=['POST'])
@jwt_required()
def addNewItem():
    a = admin()
    data = request.get_json()
    res = a.addItem(data['item']['name'], data['item']['price'], data['item']['brand'], data['itemCat'])
    if not res:
        return jsonify({"message":"Item already exists"}), 401
    return jsonify({"message": "Item created" , 'itemId': res}), 200


@app.route('/categorylist', methods=['GET'])
@jwt_required()
def categoryList():
    a = admin()
    res = a.categoryList()
    return jsonify(res)


@app.route('/itemlist', methods=['GET'])
@jwt_required()
def itemList():
    a = admin()
    res = a.itemList()
    return jsonify(res)

@app.route('/delete/<item_id>', methods=['DELETE'])
@jwt_required()
def delete(item_id):
    a = admin()
    res = a.deleteItem(item_id)

    if res == 1 :
        return jsonify({"message": "Successfully deleted"}), 200
    elif res == -1:
        return jsonify({"message": "The item is present in a cart. The item cannot be deleted!"}), 401
    else:
        return jsonify({"message": "The item is not found"}), 401

@app.route('/userlist', methods=['GET'])
@jwt_required()
def userList():
    a = admin()
    res = a.userList()
    return jsonify(res)

#----------------------------------------------------USER----------------------------------------------

@app.route('/addtocart', methods=['POST'])
@jwt_required()
def addToCart():
    data = request.get_json()
    u = user(data['userName'])
    itemId = data['itemId']
    quantity = data['quantity']
    res = u.addToCart(itemId, quantity)
    if res:
        return jsonify({"message": "Added to cart successfully"}), 200
    return jsonify({"message": "Unable to add to cart"}), 401
    

@app.route('/cartlist', methods=['POST'])
@jwt_required()
def cartList():
    u = get_jwt_identity()
    data = request.get_json()
    u = user(data['userName'])
    res = u.cartList()
    if len(res) == 0:
        return jsonify(res), 401
    return jsonify(res), 200


@app.route('/gettotal', methods=['POST'])
@jwt_required()
def getTotal():
    userName = request.get_json()['userName']
    u = user(userName)
    total = u.totalPayment()
    return jsonify(total), 200


@app.route('/updatequantity', methods=['PUT'])
@jwt_required()
def updatequantity():
    data = request.get_json()
    u = user(data['userName'])
    quantity = data['quantity']
    itemId = data['itemId']
    res = u.updateQuantity(itemId=itemId, quantity=quantity)
    if res == 1:
        return jsonify({'message': 'Successfully updated'}), 200
    elif res == 2:
        return jsonify({'message': 'Item already exists in cart'}), 200
    return jsonify({'message': 'Unable to update!'}), 401


@app.route('/clearcart', methods=['POST'])
@jwt_required()
def clearcart():
    data = request.get_json()
    u = user(data['userName'])
    res = u.clearCart()
    if res: 
        return jsonify({"message": "Cart cleared!"}), 200
    return jsonify({"message": "Cart cannot be deleted!"}), 401


@app.route('/deleteitem', methods=['DELETE'])
@jwt_required()
def deleteitem():
    data = request.get_json()
    u = user(data['userName'])
    itemId = data['itemId']
    res = u.deleteItem(itemId)
    if res :
        return jsonify({'message': 'Item deleted'}), 200
    return jsonify({'message': 'Unable to delete the item'}), 401

@jwt.expired_token_loader
# @app.route('/error', methods=['GET'])
def expired_token_callback(jwt_header, jwt_data):
    # logout()
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The token has expired'
    }), 401

if __name__ == "__main__":
    app.run(debug=True)