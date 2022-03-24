import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))  #
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """
    The Config class assigns variables for FOUR FUNCTIONS.

    1. FORMS
        The extension Flask WTForms uses the SECRET_KEY variable with a hidden field to secure forms from malicious user
        input. This hidden field is hidden in called 'hidden_tag()' in my application's HTML code.
        Example: app/templates/user.html
    2. DATABASE
        The extension SQLAlchemy needs to know where the database is located / how to access it, and it needs to know
        whether to track changes. Because I don't want to be alerted every time the database is updated, I have set that
        variable to False.
    3. PAGINATION
        The quantity of queried results rendered on a single page
    4. EMAIL
        In order to issue emails, the Flask-Mail extension needs to know five configuration variables: the server, port,
        Transport Layer Security (TLS), the email address, and the email address's password. Rather than store some of this
        information in the code of this application, I have let the developer set them as environment variables in the
        terminal using os.environ.get(). The developer will type in the terminal the following commands after launching
        the flask app ($ flask run):
            $ export MAIL_SERVER=smtp.googlemail.com    <---for a Gmail account
            $ export MAIL_PORT=587
            $ export MAIL_USE_TLS=1    <---to secure the communication
            $ export MAIL_USERNAME=<developers-email@gmail.com>
            $ export MAIL_PASSWORD=<developers-gmail-password>
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ne-hackez-pas-mon-site'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'bd.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RESULTS_PER_PAGE = 5

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['prof.k.christensen@gmail.com']
