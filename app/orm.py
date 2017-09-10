from sqlalchemy import  (MetaData, create_engine, Column, 
                        String, Integer, Float, Boolean, Text,
                        ForeignKey, not_, and_)
from sqlalchemy.orm import sessionmaker, Session, scoped_session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import base64
import json
import time
from util import stripe

from util import Configs, rando_hour
CONFIGS = Configs()

metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_engine(CONFIGS['database'])

class User(Base):
    __tablename__ = 'users'
    email = Column(String(50))
    username = Column(String(50), primary_key=True)
    password = Column(String(255))
    stripe_id = Column(String(255))
    subscription = Column(String(255))
    type = Column(String(10), default='user')

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha512')

    def check_password(self, check):
        return check_password_hash(self.password, check)

    def charge(self, amount):
        charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            customer=self.stripe_id
        )

    def setup_payments(self):
        session = Session()
        job = Job(type='charge', run=time.time())
        job._user = self.username
        session.add(job)
        session.commit()
        Session.remove()

    def cancel_subscription(self):
        self.subscription = 'none'

    @staticmethod      
    def is_authenticated():
        return True
 
    @staticmethod
    def is_active():
        return True
 
    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    def __repr__(self):
        return 'User(username={}, password={})'.format(self.username, 
                                                        bool(self.password))

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    _user = Column(String(50), ForeignKey('users.username'))
    timestamp = Column(Integer)
    amount = Column(Integer)
    paid_through = Column(Float)

    user = relationship("User", backref=backref('payments'))

    def __repr__(self):
        return 'Payment(user={}, timestamp={}, amount={}, paid_through={}'.format(self._user, 
                                                            self.timestamp,
                                                            self.amount,
                                                            self.paid_through)

class IUser(Base):
    __tablename__ = 'i_users'
    username = Column(String(50), primary_key=True)
    password = Column(String(255))
    _user = Column(String(50), ForeignKey('users.username'))

    user = relationship("User", backref=backref('i_users'))

    def set_password(self, password):
        # encrypt the password and save it
        f = Fernet(CONFIGS['encryptionKey'])
        self.password = f.encrypt(password.encode())

    def get_password(self):
        f = Fernet(CONFIGS['encryptionKey'])
        return f.decrypt(self.password).decode()

    def __repr__(self):
        return 'IUser(user={}, username={}, password={})'.format(self._user, 
                                                                    self.username, 
                                                                    bool(self.password))

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    type = Column(String(16))
    _user = Column(String(50), ForeignKey('i_users.username'))
    run = Column(Integer)
    start_time = Column(Integer)
    end_time = Column(Integer)
    running = Column(Boolean, default=False)
    finished = Column(Boolean, default=False)
    count = Column(Integer)
    error = Column(Text)

    i_user = relationship("IUser", backref=backref('jobs'))

    def __repr__(self):
        return 'Job(type={},user={}, run={}, start_time={},\n \
                    end_time={}, running={}, count={})'.format(self.type,
                                                                self._user, 
                                                                self.run, 
                                                                self.start_time, 
                                                                self.end_time, 
                                                                self.running, 
                                                                self.count)

class Following(Base):
    __tablename__ = 'following'
    id = Column(Integer, primary_key=True)
    _user = Column(String(50), ForeignKey('i_users.username'))
    other_user = Column(String(50))
    timestamp = Column(Integer)

    i_user = relationship("IUser", backref=backref('following', order_by=timestamp))

    def __repr__(self):
        return 'Following(user={}, other_user={}, timestamp={})'.format(self._user, 
                                                                            self.other_user,
                                                                            self.timestamp)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    _user = Column(String(50), ForeignKey('i_users.username'))
    tag = Column(String(50))

    i_user = relationship("IUser", backref=backref('tags'))

    def __repr__(self):
        return 'Tag(user={}, tag={})'.format(self._user, 
                                                        self.tag)

    def __str__(self):
        return self.tag

def create_i_user(username, password, tags=None):
    i = IUser()
    i.username = username
    i.set_password(password)

    # initiate jobs
    jobs = [Job(type='like', run=time.time()),
                Job(type='follow', run=time.time() + (2.5 * rando_hour())),
                Job(type='unfollow', run=time.time() + (3600 * 24 * 7))]
    i.jobs = jobs

    if tags is not None:
        for tag in tags:
            t = Tag()
            t.tag = tag
            i.tags.append(t)

    return i

def create_user(username, password, tags=None):
    u = User()
    u.username = username
    u.set_password(password)

    i = create_i_user(username,password,tags=tags)
    u.i_users.append(i)

    return u

def create_user_from_config(file='user.json'):
    with open('user.json', 'r') as file_:
        user = json.loads(file_.read())

    u = create_user(user['username'], user['password'], user['tags'])
    return u

def add_column(engine, table_name, column):
    '''
    Add a column to an existing table
    '''
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    engine.execute('ALTER TABLE "%s" ADD COLUMN %s %s' % (table_name, column_name, column_type))


db_sql = metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)