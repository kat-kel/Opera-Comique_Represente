import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))  #
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """
    The Config class assigns variables for THREE FUNCTIONS.

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
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ne-hackez-pas-mon-site'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'bd.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RESULTS_PER_PAGE = 5
