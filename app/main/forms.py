from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired


class ContributionForm(FlaskForm):
    source = TextAreaField("Citation", validators=[DataRequired()])
    date_performance = DateField("Date", validators=[DataRequired()])
    opera_id = SelectField("Opéra", coerce=int)  # select one of the primary keys from the Opera table,
    # though when the form renders in the view it will display the corresponding opera.title
    place_id = SelectField("Lieu", coerce=int)
    submit = SubmitField('Enregistrer')


class AdvancedSearch(FlaskForm):
    opera_id = SelectField("Opéra", coerce=int, default=0)
    place_id = SelectField("Commune", coerce=int, default=0)
    submit = SubmitField('Enregistrer')


class CollaboratorForm(FlaskForm):
    person_id = SelectField("Auteur", coerce=int, default=0)
    submit = SubmitField('Sélectionner')