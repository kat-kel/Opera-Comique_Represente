from app import db, create_app
from app.models import User, Contribution


app = create_app()
# the function create_app(), imported from the application package's __init__.py module, configures and initializes the
# application object at a local host


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Contribution': Contribution}
