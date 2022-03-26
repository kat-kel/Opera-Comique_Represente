from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired


class ContributionForm(FlaskForm):
    source = TextAreaField("Citation", validators=[DataRequired()])
    date_performance = DateField("Date", validators=[DataRequired()])
    opera_id = SelectField("Opéra", coerce=int)
    place_id = SelectField("Lieu", coerce=int)
    submit = SubmitField('Enregistrer')


class AdvancedSearch(FlaskForm):
    opera_id = SelectField("Opéra", coerce=int, default=0)
    place_id = SelectField("Commune", coerce=int, default=0)
    submit = SubmitField('Enregistrer')


class CollaboratorForm(FlaskForm):
    person_id = SelectField("Auteur", coerce=int, default=0)
    submit = SubmitField('Sélectionner')


class DateFilterForm(FlaskForm):
    start = DateField("À partir de", validators=[DataRequired()])
    end = DateField("Jusqu'à", validators=[DataRequired()])
    submit = SubmitField('Sélectionner')