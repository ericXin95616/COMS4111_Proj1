from wtforms import Form, BooleanField, StringField, ValidationError
from wtforms.validators import InputRequired, Length
from flask import g


class LoginForm(Form):
    firstname = StringField('First Name', validators=[InputRequired(), Length(max=20)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(max=20)])
    username = StringField('Username', validators=[InputRequired(), Length(max=20)])

    def validate(self, extra_validators=None):
        cursor = g.conn.execute(
            "SELECT user_id FROM users u WHERE u.first_name=(%s) and u.last_name=(%s) and u.username=(%s)",
            self.firstname.data,
            self.lastname.data,
            self.username.data
        )
        g.user = None
        for result in cursor:
            g.user = result['user_id']
        if g.user is None:
            self.error = "Such user does not exist!"
            return False
        return True
