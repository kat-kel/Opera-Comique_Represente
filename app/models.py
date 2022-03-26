from datetime import datetime
from hashlib import md5
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):  # UserMixin sets generic settings for Flask-Login's four required items :
    # the is_authenticated variable, the is_active variable, the is_anonymous variable, the get_id() method
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    about_me = db.Column(db.String)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    contributions = db.relationship('Contribution', backref='contributor', lazy='dynamic')  # 'Contributions' is not a
    # field in the table User, but rather a many-to-one relationship between 'contributions' and one 'contributor'
    # (aka User.id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Opera(db.Model):
    id_opera = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    acts = db.Column(db.Integer)
    date_creation = db.Column(db.DateTime)

    def __init__(self, id_opera, title, acts, date_creation):
        self.id_opera = id_opera
        self.title = title
        self.acts = acts
        self.date_creation = date_creation

    def __repr__(self):
        return '<Opera : {}>'.format(self.title)


class Communes(db.Model):
    id_commune = db.Column(db.Integer, primary_key=True)
    commune = db.Column(db.String)
    dep = db.Column(db.String)

    def __init__(self, id_commune, commune, dep):
        self.id_commune = id_commune
        self.commune = commune
        self.dep = dep


class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(240))
    date_performance = db.Column(db.DateTime)  # YYYY-MM-JJ
    date_creation = db.Column(db.DateTime)
    opera_id = db.Column(db.Integer, db.ForeignKey('opera.id_opera'))
    title = db.Column(db.String(80))
    commune_id = db.Column(db.Integer, db.ForeignKey('communes.id_commune'))
    commune_name = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __init__(self, source, date_performance, date_creation, opera_id, title, commune_id, commune_name, user_id):
        self.source = source
        self.date_performance = date_performance
        self.date_creation = date_creation
        self.opera_id = opera_id
        self.title = title
        self.commune_id = commune_id
        self.commune_name = commune_name
        self.user_id = user_id

    def __repr__(self):
        return '<Contribution : {}, date : {}, title : {}>'.\
            format(self.id, self.date_performance,
                   self.opera_id, self.title)


class Responsibility(db.Model):
    id_responsibility = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    opera_id = db.Column(db.Integer, db.ForeignKey('opera.id_opera'))
    performance_date = db.Column(db.DateTime)
    performance_id = db.Column(db.Integer, db.ForeignKey('paris.id_performance'))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id_person'))
    role = db.Column(db.String(20))

    def __init__(self, id_responsibility, title, opera_id, performance_date, performance_id, person_id, role):
        self.id_responsibility = id_responsibility
        self.title = title
        self.opera_id = opera_id
        self.performance_date = performance_date
        self.performance_id = performance_id
        self.person_id = person_id
        self.role = role

    def __repr__(self):
        return '<Responsibility : {}, title : {}, person_id : {}'.\
            format(self.id_responsibility, self.title, self.person_id)


class Person(db.Model):
    id_person = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __int__(self, id, name):
        self.id = id
        self.name = name


class Paris(db.Model):
    id_performance = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    opera_id = db.Column(db.Integer, db.ForeignKey('opera.id_opera'))
    date_performance = db.Column(db.DateTime)
    source = db.Column(db.String(80))
    age = db.Column(db.Float)

    def __init__(self, id_performance, title, opera_id, date_performance, source, age):
        self.id_performance = id_performance
        self.title = title
        self.opera_id = opera_id
        self.date_performance = date_performance
        self.source = source
        self.age = age