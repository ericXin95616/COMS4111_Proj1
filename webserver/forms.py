from wtforms import Form, StringField, ValidationError, SelectField, FloatField, TextAreaField
from wtforms.validators import InputRequired, Length
from flask import session

from models import *


class LoginForm(Form):
    firstname = StringField('First Name', validators=[InputRequired(), Length(max=20)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(max=20)])
    username = StringField('Username', validators=[InputRequired(), Length(max=20)])

    def validate(self, extra_validators=None):
        # check if credentials exist in database
        cursor = g.conn.execute(
            "SELECT user_id FROM users u WHERE u.first_name=(%s) and u.last_name=(%s) and u.username=(%s)",
            self.firstname.data,
            self.lastname.data,
            self.username.data
        )

        isUserExist = False
        for result in cursor:
            isUserExist += True
            session["user_id"] = result["user_id"]
        if not isUserExist:
            session["user_id"] = None
            self.error = "Such user does not exist!"
            return False
        return True


class SearchForm(Form):
    category = SelectField(u'', choices=[('All', 'All')])
    text = StringField('', validators=[Length(max=50)])


class ProductForm(Form):
    name = StringField('Item Name', validators=[InputRequired(), Length(max=100)])
    category = SelectField(u'Category', choices=[])
    description = TextAreaField('Description', validators=[InputRequired(), Length(max=300)], render_kw={'class': 'form-control', 'rows': 5, 'cols': 50})
    price = FloatField('Price', validators=[InputRequired()])


class CommentForm(Form):
    rating = SelectField(u'Rating', choices=[(0,0), (0.5,0.5), (1.0,1.0), (1.5,1.5), (2.0,2.0), (2.5,2.5), (3.0,3.0), (3.5,3.5), (4.0,4.0), (4.5,4.5), (5.0,5.0)])
    comment = TextAreaField('Comment', validators=[InputRequired(), Length(max=1000)], render_kw={'class': 'form-control', 'rows': 5, 'cols': 100})


