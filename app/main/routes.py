from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import ContributionForm, AdvancedSearch, CollaboratorForm
from app.models import User, Contribution, Opera, Communes, Person, Responsibility, Paris
from app.main import bp
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy


def create_contribution(form, contributor):
    """
    Generate relevant data. From Opera model, query (opera.title) when (opera.id_opera) matches input (form.opera_id) &
    from Commune model, query (commune.commune) when (commune.id_commune) matches input (form.place_id). Synthesize
    these query results and the parameter contributor (current_user.get_id()) with other parsed Form data. [22/03/2022]
    :param form with data fields: source (string), performance (datetime), opera_id (integer), title (string),
    commune_id (integer), commune_name (string), user_id (integer)
    :param contributor: current_user.get_id()
    :return: key-value pairs from the Flask form's fields (key) and user input / contributor value (value)
    """
    contribution = Contribution(source=form.source.data,  # save data from each of the form's fields as a variable
                                date_performance=form.date_performance.data,
                                date_creation=Opera.query.get(form.opera_id.data).date_creation,
                                opera_id=form.opera_id.data,
                                title=Opera.query.get(form.opera_id.data).title,
                                commune_id=form.place_id.data,
                                commune_name=Communes.query.get(form.place_id.data).commune,
                                user_id=contributor)

    return contribution


@bp.before_app_request  # decorator tells Flask to execute the before_request() function before the view function
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')  # associates the URL '/' to the function index()
@bp.route('/index')
def index():
    return render_template('index.html', title='Accueil')


@bp.route('/representations_provinciales', methods=['GET', 'POST'])
def contributions():
    """
    Query all data in Contribution model, count results with len() function, and paginate results. Query results are
    ordered by datetime value (contribution.date_performance) from oldest to newest. [23/03/2022]
    :return: template 'contributions.html'
    """
    page = request.args.get('page', 1, type=int)
    contributions = Contribution.query.order_by(Contribution.date_performance).paginate(
        page, current_app.config['RESULTS_PER_PAGE'], False)
    count = Contribution.query.order_by(Contribution.date_performance).count()
    next_url = url_for('main.contributions', page=contributions.next_num) if contributions.has_next else None
    prev_url = url_for('main.contributions', page=contributions.prev_num) if contributions.has_prev else None
    return render_template('contributions.html', title='Contributions', contributions=contributions.items, count=count,
                       next_url=next_url, prev_url=prev_url)

@bp.route('/representations_provinciales_ensemble', methods=['GET', 'POST'])
def contributions_all():
    """
    Query all data in Contribution model and present in one page viewer. Query results are ordered by datetime value
    (contribution.performance) descending from oldest to newest. If the URL has a search keyword (title), the query
    filters out data lacking a title (contribution.opera_title) that resembles (SQLAlchemy filter method .like()) the
    title/keyword retrieved from the URL (request.args.get()). [23/03/2022]
    :return: template 'contributions.html', accessible from link at URL 'representations_provinciales' and quick search
    """
    keyword = request.args.get('title', None)
    if not keyword:
        all = True
        results = False
        contributions = Contribution.query.order_by(Contribution.date_performance)
        count = contributions.count()
    else:
        all = False
        results = True
        contributions = Contribution.query.filter(Contribution.title.like("%{}%".format(keyword))). \
            order_by(Contribution.date_performance)
        count = contributions.count()
    return render_template('contributions.html', title='Contributions', contributions=contributions, count=count,
                           all=all, results=results)


@bp.route('/contribuer', methods=['GET', 'POST'])
@login_required
def contribuer():
    """
    Render Flask Form, format input in Contribution class, and check if the data are valid. Validation 1: the input
    (contribution.date_performance) is later than, aka less than <, the premiere in Paris (opera.creation_date).
    Validation 2: the input (contribution.date_performance, contribution.title, contribution.commune_id) is not already
    in the database. The entry's existence is checked via an inner join across the three fields (exists_query).
    [23/03/2022]
    :return: template 'index.html' with ContributionForm
    """
    contributor = current_user.get_id()
    form = ContributionForm(request.form)
    form.opera_id.choices = [(o.id_opera, "{title} ({year})".
                              format(title=o.title, year=str(o.date_creation)[:4])) for o in Opera.query.order_by('title')]
    form.place_id.choices = [(c.id_commune, "{name} ({dep})".
                              format(name=c.commune, dep=c.dep)) for c in Communes.query.order_by('commune')]
    if request.method == 'POST' and form.validate_on_submit():
        contribution = create_contribution(form, contributor)
        exists_query = Contribution.query.filter(func.date(Contribution.date_performance) == contribution.date_performance).\
            filter_by(opera_id=contribution.opera_id).filter_by(commune_id=contribution.commune_id).first()
        if contribution.date_performance < Opera.query.get(contribution.opera_id).date_creation.date():
            flash("ERREUR : La date que vous avez essayé d'enregistrer a eu lieu avant la création de l'opéra.")
        elif exists_query:
            work = exists_query.title
            day = exists_query.date_performance.date()
            place = Communes.query.get(exists_query.commune_id).commune
            flash("PAS D'ENREGISTREMENT : Une représentation de {} le {} à {} est déjà présente dans la base de données".format(work, day, place))
        else:
            db.session.add(contribution)
            db.session.commit()
            flash("La base de données a été mise à jour. Merci d'avoir contribué au projet.")
            return redirect(url_for('main.contributions'))
    return render_template('index.html', title='Contribuer', form=form)


@bp.route('/modifier_contribution/<username>/<int:contributionid>', methods=['GET', 'POST'])
@login_required
def modify_contribution(username, contributionid):
    """
    Render Flask Form, format input in Contribution class, and check if the data are valid. Validation 1: the input
    (contribution.date_performance) is later than, aka less than <, the premiere in Paris (opera.creation_date).
    Validation 2: the input (contribution.date_performance, contribution.title, contribution.commune_id) is not already
    in the database. The entry's existence is checked via an inner join across the three fields (exists_query).
    [23/03/2022]
    :param username: string in the URL
    :param contributionid: integer in the URL, which was generated from the link on 'auth/user.html'
    :return: template 'modify_contribution.html' with ContributionForm
    """
    contributor = current_user.get_id()
    user = User.query.filter_by(username=username).first_or_404()
    old_contribution = Contribution.query.get(contributionid)
    form = ContributionForm(request.form)
    form.opera_id.choices = [(o.id_opera, o.title) for o in Opera.query.order_by('title')]
    form.place_id.choices = [(c.id_commune, c.commune) for c in Communes.query.order_by('commune')]
    if request.method == 'POST' and form.validate_on_submit():
        new_contribution = create_contribution(form, contributor)
        exists_query = Contribution.query.filter(func.date(Contribution.date_performance) == new_contribution.date_performance). \
            filter_by(opera_id=new_contribution.opera_id).filter_by(commune_id=new_contribution.commune_id).first()
        if new_contribution.date_performance < Opera.query.get(new_contribution.opera_id).date_creation.date():
            flash("ERREUR : La date que vous avez essayé d'enregistrer a eu lieu avant la création de l'opéra.")
        elif exists_query:
            work = exists_query.title
            day = exists_query.date_performance.date()
            place = Communes.query.get(exists_query.commune_id).commune
            flash("PAS D'ENREGISTREMENT : Une représentation de {} le {} à {} est déjà présente dans la base de données".
                format(work, day, place))
            return redirect(url_for('main.contributions'))
        else:
            db.session.delete(old_contribution)
            db.session.add(new_contribution)
            db.session.commit()
            flash('Vous avez mise à jour la base de données. Merci pour votre contribution.')
            return redirect(url_for('main.contributions'))
    return render_template('modify_contribution.html', user=user, contribution=old_contribution, form=form)


@bp.route('/supprimer_contribution/<username>/<int:contributionid>', methods=['GET', 'POST'])
@login_required
def delete_contribution(username, contributionid):
    """
    Drop from the database all the queried data from the old contribution, whose primary key is requested from the URL.
    [23/03/2022]
    :param username:
    :param contributionid:
    :return: calls auth.user()
    """
    old_contribution = Contribution.query.get(contributionid)
    db.session.delete(old_contribution)
    db.session.commit()
    flash('Vous avez supprimé la donnée sur une représentation de {} le {}.'.format(old_contribution.title, old_contribution.date_performance))
    return redirect(url_for('auth.user', username=username))


@bp.route('/mentions')
def mentions():
    """
    Passes list of users to template and renders template. [23/03/2022]
    :return: template 'mentions.html'
    """
    users = User.query.all()
    return render_template('mentions.html', title='Mentions légales', users=users)


@bp.route('/paris_analyse', methods=['GET', 'POST'])
def paris_tool():

    form = CollaboratorForm(request.form)
    form.person_id.choices = [(0, "-- sélectionner --")] + \
                             [(p.id_person, "{name}".format(name=p.name)) for p in Person.query.order_by('name')]
    if request.method == 'POST' and form.validate_on_submit():
        author = Person.query.filter_by(id_person=form.person_id.data).first().id_person
        return redirect(url_for('main.paris', author=author))
    return render_template('paris_tools.html', form=form)


@bp.route('/paris_analyse_resultat', methods=['GET', 'POST'])
def paris():
    """
    Query all data in Paris model, count results with len() function, and paginate results. Query results are
    ordered by datetime value (paris.date_performance) from oldest to newest. If the URL has a search keyword (title),
    the query filters out data lacking a title (contribution.opera_title) that resembles (SQLAlchemy filter method .
    like()) the title/keyword retrieved from the URL (request.args.get(title)). [23/03/2022]
    :return: template 'paris_analyse.html'
    """
    keyword = request.args.get('author', None)
    author = Person.query.filter(Person.id_person == keyword).first()
    works = db.engine.execute("SELECT DISTINCT responsibility.name, responsibility.role, responsibility.title, opera.acts, opera.date_creation "
                              "FROM responsibility, opera "
                              "WHERE responsibility.opera_id IN("
                              "SELECT responsibility.opera_id "
                              "FROM responsibility WHERE responsibility.person_id = {}) "
                              "AND responsibility.person_id is not {} AND responsibility.opera_id = opera.id_opera".
                              format(author.id_person, author.id_person))
    return render_template('paris_analyse.html', person=author, works=works)


@bp.route('/paris_representations_ensemble', methods=['GET', 'POST'])
def paris_all():
    """
    Query all data in Paris model, count results with len() function, and display in one view. Query results are
    ordered by datetime value (paris.date_performance) from oldest to newest. If the URL has a search keyword (title),
    the query filters out data lacking a title (contribution.opera_title) that resembles (SQLAlchemy filter method .
    like()) the title/keyword retrieved from the URL (request.args.get(title)). [23/03/2022]
    :return: template 'contributions.html', accessible from link at URL 'representations_provinciales' and quick search
    """
    keyword = request.args.get('title', None)
    if not keyword:
        query = Paris.query. \
            join(Opera, Paris.opera_id == Opera.id_opera). \
            filter(Paris.opera_id == Opera.id_opera). \
            add_columns(Paris.date_performance, Opera.title, Paris.age, Opera.acts, Opera.date_creation).order_by(Paris.date_performance)
        count = len(
            Paris.query.join(Opera, Paris.opera_id == Opera.id_opera).filter(Paris.opera_id == Opera.id_opera).all())
    else:
        query = Paris.query.join(Opera, Paris.opera_id == Opera.id_opera).filter(
            Paris.opera_id == Opera.id_opera).filter(Opera.title.like("%{}%".format(keyword))). \
            add_columns(Opera.title, Paris.date_performance, Paris.age, Opera.acts, Opera.date_creation). \
            order_by(Paris.date_performance)
        count = len(
            Paris.query.join(Opera, Paris.opera_id == Opera.id_opera).filter(Paris.opera_id == Opera.id_opera).filter(
                Opera.title.like("%{}%".format(keyword))).all())
    return render_template('paris_all.html', query=query, count=count)


@bp.route('/recherche', methods=['GET', 'POST'])
def recherche():
    """
    Query the Contribution table for works with a title (Contribution.title) similar to the keyword added to the URL
    (?keyword=). Pass that query result to the template 'recherche.html' to list the search results.
    :return: template 'recherche.html' with list of search results
    """
    keyword = request.args.get("keyword", None)
    province = []
    paris = []
    title = "Recherche"
    if keyword:
        province = Contribution.query.filter(
            Contribution.title.like("%{}%".format(keyword))
        ).all()
        paris = Paris.query.\
            join(Opera, Paris.opera_id == Opera.id_opera).filter(
                Opera.title.like("%{}%".format(keyword))
            ).\
            add_columns(Opera.title, Paris.date_performance)
        count = paris.count()
        title = "Résultat pour la recherche '" + keyword + "'"
    return render_template('recherche.html', title=title, province=province, paris=paris, count=count)


@bp.route('/recherche_avancee', methods=['GET', 'POST'])
def advanced_search():
    form = AdvancedSearch(request.form)
    form.opera_id.choices = [(0, "-- sélectionner --")] + [(o.id_opera, o.title) for o in Opera.query.order_by('title')]
    form.place_id.choices = [(0, "-- sélectionner --")] + [(c.id_commune, c.commune) for c in Communes.query.order_by('commune')]
    form.opera_id.default = 0
    form.place_id.default = 0
    if form.validate_on_submit():
        if form.opera_id.data != 0 and form.place_id.data != 0:  # opera and commune selected
            opera = Opera.query.filter_by(id_opera=form.opera_id.data).first().title
            commune = Communes.query.filter_by(id_commune=form.place_id.data).first().commune
            return redirect(url_for('main.advanced_results', opera=opera, commune=commune))
        elif form.opera_id.data != 0 and form.place_id.data == 0:  # opera selected, no commune
            opera = Opera.query.filter_by(id_opera=form.opera_id.data).first().title
            return redirect(url_for('main.advanced_results', opera=opera, commune=None))
        elif form.opera_id.data == 0 and form.place_id.data != 0:  # commune selected, no opera
            commune = Communes.query.filter_by(id_commune=form.place_id.data).first().commune
            return redirect(url_for('main.advanced_results', opera=None, commune=commune))
    return render_template('recherche_avancee.html', form=form)


@bp.route('/resultats', methods=['GET', 'POST'])
def advanced_results():
    opera = request.args.get("opera", None)
    commune = request.args.get("commune", None)
    page = request.args.get('page', 1, type=int)
    results = True
    if opera == None and commune == None:
        contributions = []
    else:
        if opera and commune:
            contributions = Contribution.query.filter_by(title=opera, commune_name=commune).\
                order_by(Contribution.date_performance).paginate(page, current_app.config['RESULTS_PER_PAGE'], False)
            count = len(contributions.items)
            next_url = url_for('main.advanced_results', page=contributions.next_num, opera=opera, commune=commune) \
                if contributions.has_next else None
            prev_url = url_for('main.advanced_results', page=contributions.prev_num, opera=opera, commune=commune) \
                if contributions.has_prev else None
        elif opera:
            contributions = Contribution.query.filter_by(title=opera).\
                order_by(Contribution.date_performance).paginate(page, current_app.config['RESULTS_PER_PAGE'], False)
            count = len(contributions.items)
            next_url = url_for('main.advanced_results', page=contributions.next_num, opera=opera) \
                if contributions.has_next else None
            prev_url = url_for('main.advanced_results', page=contributions.prev_num, opera=opera) \
                if contributions.has_prev else None
        elif commune:
            contributions = Contribution.query.filter_by(commune_name=commune).\
                order_by(Contribution.date_performance).paginate(page, current_app.config['RESULTS_PER_PAGE'], False)
            count = len(contributions.items)
            next_url = url_for('main.advanced_results', page=contributions.next_num, commune=commune) \
                if contributions.has_next else None
            prev_url = url_for('main.advanced_results', page=contributions.prev_num, commune=commune) \
                if contributions.has_prev else None
    return render_template('contributions.html', contributions=contributions.items, count=count,
                           next_url=next_url, prev_url=prev_url, results=results)