from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, EditProfileForm
from app.models import User, Contribution
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in if the user's input (form.username) matches (user.username) in the database and if both the user's
    input (form.password) and database's (user.password_hash) produce True when passed to User model's check_password(),
    which is a function imported from werkzeug.security. Imported functions/settings 'current_user' and UserMixin's
    'is_authenticated' from flask_login check if the browser's cached user input has already satisfied these conditions.
    [22/03/2022]
    :return: template 'auth/login.html'
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    """
    Logs user out with logout_user(), a function imported from flask_login. [22/03/2022]
    :return: template '/index', removes cached login data
    """
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])  # decorator associates the URL '/register' to the function register()
def register():
    """
    Updates the database with user input (form.username -> user.username, form.email -> user.email, form.first_name ->
    user.first_name, form.last_name -> user.last_name). Imported functions/settings 'current_user' and UserMixin's
    'is_authenticated' from flask_login check if the browser's cached user input has already satisfied login conditions.
    [22/03/2022]
    :return: template 'register.html', then auth/login() if the template's form is validated
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        last_name = form.last_name.data.upper()
        user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=last_name)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Votre compte est bien enregistré. L'équipe de l'Opéra-Comique Representé vous remercie pour vos contributions au projet.")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register',
                           form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Calls function send_password_reset_email(), imported from module auth/email.py, to the email address (user.email)
    registered with a user in the database if the user input (form.email.data) matches data in the database. Imported
    functions/settings 'current_user' and UserMixin's 'is_authenticated' from flask_login check if the browser's cached
    user input has already satisfied the login conditions, such as a correct password. [22/03/2022]
    :return: template 'reset_password_request.html', then auth/login() if the template's form is validated
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            'Vérifiez la boîte de réception enregistrée avec ce compte pour un mail vous permettant de réinitialiser votre mot de passe.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Réinitialiser votre mot de passe', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Updates database (user.password_hash) with new data generated from user input (form.password) and the User model's
    function set_password(), which relies on the function generate_password_hash() imported from werkzeug.security.
    Imported functions/settings 'current_user' and UserMixin's 'is_authenticated' from flask_login check if the browser's
    cached user input has already satisfied the login conditions, such as a correct password. [22/03/2022]
    :param token: JSON Web Token generated from the User model's function get_reset_password_token()
    :return: template 'reset_password.html', then auth/login() if the template's form is validated
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Votre nouveau mot de passe est enregistré.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/user/<username>')  # URL finishes with a dynamic element
@login_required
def user(username):
    """
    Queries all contributions created by the user and shows a limited amount, with an option to paginate through them,
    if the decorator @login_required, imported from flask_login, is satisfied. [22/03/2022]
    :param username: string value from user.username
    :return: template, 'user.html', with user's contributions lists and paginated
    """
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    contributions = user.contributions.order_by(Contribution.timestamp.desc()).paginate(
        page, current_app.config['RESULTS_PER_PAGE'], False)
    next_url = url_for('auth.user', username=user.username,
                       page=contributions.next_num) if contributions.has_next else None
    prev_url = url_for('auth.user', username=user.username,
                       page=contributions.prev_num) if contributions.has_prev else None
    return render_template('auth/user.html', user=user, contributions=contributions.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/modifier_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Updates the database (user.username, user.about_me) with new data generated from user input (form.username,
    form.about_me) if the decorator @login_required, imported from flask_login, is satisfied. [22/03/2022]
    :return: template 'edit_profile.html', then auth/user() if the template's form is validated
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Vos modifications de profil d'utilisateur sont sauvegardées.")
        return redirect(url_for('auth.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('auth/edit_profile.html', title='Edit Profile',
                           form=form)