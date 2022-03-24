from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    """
    This form gathers a registered user's username and password as well as recognizes whether the user wants the
    browser to remember their credentials the next time it gets one of the application's URLs.
    """
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember_me = BooleanField("Souvenez de moi")
    submit = SubmitField("Connectez-vous")


class RegistrationForm(FlaskForm):
    """
    This form gathers a new user's desired username, email address, and password. Two users cannot have the same
    username (though a registered user can change their username) nor email address (immutable). These constraints are
    applied in two methods of the RegistrationForm class: validate_username() and validate_email().
    """
    first_name = StringField('Prénom', validators=[DataRequired()])
    last_name = StringField('Nom', validators=[DataRequired()])
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    email = StringField("Courriel", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    password2 = PasswordField(
        "Répetez votre mot de passe", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Enregistrez")

    def validate_username(self, username):
        """
        The method validate_username() raises an error using Flask WTForm's ValidationError class if the username
        entered into the Login Form could not be queried in the model User; in other words, the 'username' does not
        belong to a user registered in the database's table User.
        :param username: value of username from User table
        :return:
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Veuillez utiliser un autre nom d'utilisateur.")

    def validate_email(self, email):
        """
        The method validate_email() raises an error using Flask WTForm's ValidationError class if the email entered into
        the Login Form could not be queried in the model User; in other words, the 'username' does not belong to a user
        registered in the database's table User.
        :param email: value of email from User table
        :return:
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Veuillez utiliser un autre adresse email")


class ResetPasswordRequestForm(FlaskForm):
    """
    This form gathers a user's email address to which (if the address matches a user's in the User table) will be sent
    an email containing a link to the URL '/reset_password/<...>'. This URL will render a form with which the user can
    update the User table with a new password.
    """
    email = StringField("Courriel", validators=[DataRequired(), Email()])
    submit = SubmitField("Demander un nouveau mot de passe")


class ResetPasswordForm(FlaskForm):
    """
    This form gathers a user's new password two times; the two inputs must match, to prove the user remembers and can
    reproduce the password. The route which renders this form, '/reset_password', will commit the new password to the
    database.
    """
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    password2 = PasswordField(
        "Répetez votre mot de passe", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Enregistrez votre nouveau mot de passe")


class EditProfileForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    about_me = TextAreaField("Affiliation", validators=[Length(min=0, max=140)])
    submit = SubmitField("Enregistrez")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Veuillez utiliser un autre nom d'utilisateur.")
