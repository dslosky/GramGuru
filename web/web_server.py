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
from crawler import Insta

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
@dbconnect
def login(session=None):
    if request.method == 'GET':
        return render_template('login.html')

    username = request.json.get('username', '')
    password = request.json.get('password', '')
    
    registered_user = (session.query(User)
                            .filter(User.username == username).first())
    
    if (registered_user is None or not
            check_password_hash(registered_user.password, password)):
        return jsonify(success=False, 
                       msg='Your username or password is incorrect')

    login_user(registered_user)
    flash('Logged in successfully')

    user = current_user.__dict__.copy()
    user.pop('_sa_instance_state', None)
    return jsonify(success=True, user=user)

@app.route('/logout')
def logout():
    logout_user()
    
    return jsonify(success=True)

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
@dbconnect
def register(session=None):
    username = request.json.get('username', '')
    password = request.json.get('password', '')

    referal = request.json.get('referal', False)

    registered_user = (session.query(User)
                            .filter(User.username == username).first())

    if registered_user is not None:
        return jsonify(success=False, 
                       msg='This Instagram user is already registered')

    if check_login(username, password) is False:
        return jsonify(success=False, 
                       msg='These do not appear to be valid Instagram credentials')

    user = create_user(username, password)

    session.add(user)
    session.commit()

    login_user(user)

    if referal is not False:
        make_referal_discount(referal)

    user = current_user.__dict__.copy()
    user.pop('_sa_instance_state', None)
    return jsonify(success=True, user=user)

@app.route('/user-data/<username>', methods=['GET'])
@login_required
@dbconnect
def get_user_data(session=None, username=None):
    user = (session.query(User)
               .filter(User.username == username)
               .first())

    user_data = []
    for iu in user.i_users:
        data = {}
        data['i_user'] = iu
        data['follows'] = session.query(Job).filter(Job.type == 'follow')\
                                             .filter(Job._user == username)\
                                             .filter(Job.finished == True)\
                                             .all()
        data['likes'] = session.query(Job).filter(Job.type == 'like')\
                                             .filter(Job._user == username)\
                                             .filter(Job.finished == True)\
                                             .all()
        data['unfollows'] = session.query(Job).filter(Job.type == 'unfollow')\
                                             .filter(Job._user == username)\
                                             .filter(Job.finished == True)\
                                             .all()
        data['future_charges'] = session.query(Job).filter(Job.type == 'charge')\
                                             .filter(Job._user == username)\
                                             .filter(Job.run > time.time())\
                                             .all()

        data['payments'] = session.query(Payment).filter(Payment._user == username)\
                                                  .all()

        data['follow_total'] = 0
        for job in data['follows']:
            if job.count:
                data['follow_total'] += job.count
        
        data['like_total'] = 0
        for job in data['likes']:
            if job.count:
                data['like_total'] += job.count

        data['unfollow_total'] = 0
        for job in data['unfollows']:
            if job.count:
                data['unfollow_total'] += job.count

        user_data += [data]

    return jsonify(success=True, data=user_data, user=user)

@app.route('/charge', methods=['POST'])
@login_required
@dbconnect
def charge(session=None):
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

    return jsonify(success=True)

def check_login(username, password):
    i = Insta()
    login_check = i.login(username, password)
    i.driver.quit()

    return login_check

##############################################
################# ADMIN ONLY #################

def admin_only(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if current_user and current_user.is_authenticated:
            if current_user.type == 'admin':
                return func(*args, **kwargs)
            else:
                return jsonify(success=False)
        else:
            return jsonify(success=False)
    return func_wrapper

@app.route('/admin/data')
@login_required
@admin_only
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
    admin_data['future_jobs'] = session.query(Job).filter(Job.finished == False)\
                                                    .filter(Job.running == False)\
                                                    .filter(Job.run > now).all()
    admin_data['recent_jobs'] = session.query(Job).filter(Job.end_time > time.time() - 3600).all()
    
    admin_data['stuck_jobs'] = session.query(Job).filter(Job.finished == False)\
                                                    .filter(Job.running == False)\
                                                    .filter(Job.run < now).all()

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

    return jsonify(success=True, admin_data=admin_data)


@app.route('/admin/run-job', methods=['POST'])
@login_required
@admin_only
@dbconnect
def run_job(session=None):
    job_id = request.json.get('jobID', '')
    job = session.query(Job).filter(Job.id == int(job_id)).first()
    job.run = time.time()
    session.commit()
    return jsonify(success=True)

@app.route('/admin/resolve-error', methods=['POST'])
@login_required
@admin_only
@dbconnect
def resolve_error(session=None):
    job_id = request.json.get('jobID', '')
    job = session.query(Job).filter(Job.id == int(job_id)).first()
    job.error = None
    session.commit()
    return jsonify(success=True)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('index.html')

def start(port=80):
    app.run(host='0.0.0.0', port=port, threaded=True)

@dbconnect
def make_referal_discount(username):
    user = session.query(User).filter(User.username).first()
    if user is not None:
        d = Discount(amount=500, timestamp=time.time())
        d.user = user

        session.add(d)
        session.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':
            # run in debug mode
            app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    else:
        start()