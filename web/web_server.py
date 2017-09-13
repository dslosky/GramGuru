from flask import Flask, render_template, url_for, request, session, flash, redirect, send_file, send_from_directory, Response, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import os, sys
import copy

# add the app to the path
path = os.path.dirname(os.path.abspath(__file__))
path = path.split(os.sep)
del path[-1]
path += ['app']
directory = os.path.normpath(os.sep.join(path))
if directory not in sys.path:
    sys.path += [directory]

# import database connection
from orm import *
from util import app_path, stripe, WEEK

def web_path():
    path = os.path.dirname(os.path.abspath(__file__))
    path = path.split(os.sep)
    directory = os.path.normpath(os.sep.join(path))
    return directory

BASE_DIR = os.path.join(web_path(), 'view')
STATIC_DIR = os.path.join(web_path(),'view','static')
app = Flask(__name__,
            template_folder=BASE_DIR,
            static_folder=STATIC_DIR)

################################ Login ################################

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.json_encoder = AlchemyEncoder

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).filter(User.username==user_id).first()
    Session.remove()
    return user

# send Angular 2 files
@app.route('/<path:filename>')
def client_app_angular2_folder(filename):
    return send_from_directory(os.path.join(BASE_DIR), filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    session = Session()
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    
    registered_user = (session.query(User)
                            .filter(User.username == username).first())
    
    if (registered_user is None or not
            check_password_hash(registered_user.password, password)):
        Session.remove()
        return jsonify(success=False)

    login_user(registered_user)
    flash('Logged in successfully')
    Session.remove()

    user = current_user.__dict__.copy()
    user.pop('_sa_instance_state', None)
    return jsonify(success=True, user=user)


@app.route('/logged_in')
def logged_in():
    if current_user.is_authenticated:
        user = current_user.__dict__.copy()
        user.pop('_sa_instance_state', None)
    else:
        user = None
    return jsonify(success=True, 
                   loggedIn=bool(current_user.is_authenticated),
                   user=user)

@app.route('/register', methods=['POST'])
def register():
    session = Session()
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    tags = request.json.get('tags', '').split(',')

    registered_user = (session.query(User)
                            .filter(User.username == username).first())

    if registered_user is not None:
        Session.remove()
        return jsonify(success=False)

    user = create_user(username, password, tags=tags)

    session.add(user)
    session.commit()

    login_user(user)

    user = current_user.__dict__.copy()
    user.pop('_sa_instance_state', None)
    return jsonify(success=True, user=user)

@app.route('/charge', methods=['POST'])
def charge():
    session = Session()
    sub_type = request.json.get('type', '')
    token = request.json.get('token', '')

    user = (session.query(User)
                .filter(User.username == current_user.username)
                .first())

    if user.stripe_id is None:
        # Create a Customer:
        customer = stripe.Customer.create(
            email=user.email,
            source=token['id'],
        )

        user.stripe_id = customer.id

    user.subscription = sub_type
    user.setup_payments()
    session.commit()


    Session.remove()
    return jsonify(success=True)

@login_required
@app.route('/admin/data')
@dbconnect
def get_admin_data(session=None):
    now = time.time()
    last_week = now - WEEK
    admin_data = {}
    admin_data['total_users'] = session.query(User).all()
    admin_data['past_charges'] = session.query(Payment).filter(Payment.timestamp < now).all()
    admin_data['weekly_charges'] = session.query(Payment).filter(Payment.timestamp > last_week) \
                                           .filter(Payment.timestamp < now).all()
    admin_data['future_charges'] = session.query(Job).filter(Job.type == 'charge').all()
    admin_data['weekly_users'] = session.query(User).filter(User.timestamp > last_week).all()
    
    admin_data['current_jobs'] = session.query(Job).filter(Job.running == True).all()
    admin_data['future_jobs'] = session.query(Job).filter(Job.run > now).all()
    admin_data['recent_jobs'] = session.query(Job).filter(Job.end_time > time.time() - 3600).all()
    
    admin_data['errors'] = session.query(Job).filter(Job.error != '') \
                                             .filter(Job.run > last_week).all()

    admin_data['past_charges_sum'] = 0
    admin_data['future_charges_sum'] = 0
    admin_data['weekly_charges_sum'] = 0

    for charge in admin_data['past_charges']:
        admin_data['past_charges_sum'] += charge.amount
    for charge in admin_data['future_charges']:
        if charge.i_user.user.subscription:
            admin_data['future_charges_sum'] += charge.i_user.user.subscription.cost
    for charge in admin_data['weekly_charges']:
        admin_data['weekly_charges_sum'] += charge.amount

    return json.dumps(admin_data, cls=AlchemyEncoder)


#@app.errorhandler(404)
#def page_not_found(error):
#    return render_template('index.html')

def start(port=80):
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':
            # run in debug mode
            app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    else:
        start()