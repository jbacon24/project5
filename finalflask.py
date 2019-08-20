
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, abort
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Beauty, BeautyItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

auth = HTTPBasicAuth()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Beauty Items Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///beautyitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@auth.verify_password
def verify_password(username_or_token, password):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/clientOAuth')
def start():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return render_template('clientOAuth.html')

@app.route('/oauth/<provider>', methods = ['POST'])
def login(provider):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    #STEP 1 - Parse the auth code
    auth_code = request.json.get('auth_code')
    print("Step 1 - Complete, received auth code %s") % auth_code
    if provider == 'google':
        #STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
          
        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            
        # # Verify that the access token is used for the intended user.
        # gplus_id = credentials.id_token['sub']
        # if result['user_id'] != gplus_id:
        #     response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response

        # # Verify that the access token is valid for this app.
        # if result['issued_to'] != CLIENT_ID:
        #     response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response

        # stored_credentials = login_session.get('credentials')
        # stored_gplus_id = login_session.get('gplus_id')
        # if stored_credentials is not None and gplus_id == stored_gplus_id:
        #     response = make_response(json.dumps('Current user is already connected.'), 200)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response
        print("Step 2 Complete! Access Token : %s ") % credentials.access_token

        #STEP 3 - Find User or make a new one
        
        #Get user info
        h = httplib2.Http()
        userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
      
        data = answer.json()

        name = data['name']
        picture = data['picture']
        email = data['email']
        
        
     
        #see if user exists, if it doesn't make a new one
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username = name, picture = picture, email = email)
            session.add(user)
            session.commit()

        

        #STEP 4 - Make token
        token = user.generate_auth_token(600)

        

        #STEP 5 - Send back token to the client 
        return jsonify({'token': token.decode('ascii')})
        
        #return jsonify({'token': token.decode('ascii'), 'duration': 600})
    else:
        return 'Unrecoginized Provider'

@app.route('/token')
@auth.login_required
def get_auth_token():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})



@app.route('/users', methods = ['POST'])
def new_user():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print("missing arguments")
        abort(400) 
        
    if session.query(User).filter_by(username = username).first() is not None:
        print("existing user")
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200#, {'Location': url_for('get_user', id = user.id, _external = True)}
        
    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201#, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/users/<int:id>')
def get_user(id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/resource')
@auth.login_required
def get_resource():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# def createUser(login_session):
#     newUser = User(name=login_session['username'], email=login_session[
#                    'email'], picture=login_session['picture'])
#     session.add(newUser)
#     session.commit()
#     user = session.query(User).filter_by(email=login_session['email']).one()
#     return user.id


# def getUserInfo(user_id):
#     user = session.query(User).filter_by(id=user_id).one()
#     return user


# def getUserID(email):
#     try:
#         user = session.query(User).filter_by(email=email).one()
#         return user.id
#     except:
#         return None

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s') % access_token
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Display a product in JSON format
@app.route('/product/<int:beauty_id>/item/JSON')
def beautyProductsJSON(beauty_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    beauty = session.query(Beauty).filter_by(id=beauty_id).one()
    items = session.query(BeautyItem).filter_by(beauty_id=beauty_id).all()
    return jsonify(BeautyItems=[i.serialize for i in items])

# Display beauty item in JSON format
@app.route('/product/<int:beauty_id>/item/<int:item_id>/JSON')
def beautyItemJSON(beauty_id, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Beauty_Item = session.query(BeautyItem).filter_by(id=item_id).one()
    return jsonify(Beauty_Item=Beauty_Item.serialize)

# Display all products in JSON format
@app.route('/product/JSON')
def productsJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    beauty = session.query(Beauty).all()
    return jsonify(beauty=[r.serialize for r in beauty])


# Show all products on homepage of app
@app.route('/')
@app.route('/product/')
def showProducts():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    products = session.query(Beauty).order_by(asc(Beauty.name))
    return render_template('products.html', products=products)

# Create a new product
@app.route('/product/new/', methods=['GET', 'POST'])
def newProduct():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        newProduct = Beauty(name=request.form['name'])
        session.add(newProduct)
        session.commit()
        return redirect(url_for('showProducts'))
    else:
        return render_template('newProduct.html')

# Edit a product
@app.route('/product/<int:beauty_id>/edit/', methods=['GET', 'POST'])
def editProduct(beauty_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedProduct = session.query(
        Beauty).filter_by(id=beauty_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedProduct.name = request.form['name']
            return redirect(url_for('showProducts'))
    else:
        return render_template(
            'editProduct.html', product=editedProduct)

# Delete a product
@app.route('/product/<int:beauty_id>/delete/', methods=['GET', 'POST'])
def deleteProduct(beauty_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    productToDelete = session.query(
        Beauty).filter_by(id=beauty_id).one()
    if request.method == 'POST':
        session.delete(productToDelete)
        session.commit()
        return redirect(
            url_for('showProducts', beauty_id=beauty_id))
    else:
        return render_template(
            'deleteProduct.html', product=productToDelete)

# Show a beauty item
@app.route('/product/<int:beauty_id>/')
@app.route('/product/<int:beauty_id>/item/')
def showItem(beauty_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    beauty = session.query(Beauty).filter_by(id=beauty_id).one()
    items = session.query(BeautyItem).filter_by(
        beauty_id=beauty_id).all()
    return render_template('item.html', items=items, beauty=beauty)

# Create a new beauty item
@app.route(
    '/product/<int:beauty_id>/item/new/', methods=['GET', 'POST'])
def newBeautyItem(beauty_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        newItem = BeautyItem(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], feature=request.form['feature'], beauty_id=beauty_id)
        session.add(newItem)
        session.commit()

        return redirect(url_for('showItem', beauty_id=beauty_id))
    else:
        return render_template('newbeautyitem.html', beauty_id=beauty_id)

# Edit a beauty item
@app.route('/product/<int:beauty_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editBeautyItem(beauty_id, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedItem = session.query(BeautyItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['feature']:
            editedItem.feature = request.form['feature']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItem', beauty_id=beauty_id))
    else:

        return render_template(
            'editbeautyitem.html', beauty_id=beauty_id, item_id=item_id, item=editedItem)

# Delete a beauty item
@app.route('/product/<int:beauty_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteBeautyItem(beauty_id, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    itemToDelete = session.query(BeautyItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItem', beauty_id=beauty_id))
    else:
        return render_template('deleteBeautyItem.html', item=itemToDelete)


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
