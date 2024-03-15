from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField
from wtforms.validators import InputRequired, Length, Optional, URL, AnyOf

class LoginForm(FlaskForm):
    """Form for loggin in user"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )



class SignupForm(FlaskForm):
    """Form for signing up a new user"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)]
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=25)]
    )

    last_name = StringField(
        "Last Name (Optional)",
        validators=[Length(max=25), Optional()]
    )

    bio = TextAreaField(
        "Bio (Optional)"
    )

    image_url = StringField(
        "Image URL (Optional)",
        validators=[URL(), Length(max=255), Optional()]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)]
    )


class EditUserForm(FlaskForm):
    """Form for editing a user"""

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=25)]
    )

    last_name = StringField(
        "Last Name (Optional)",
        validators=[Length(max=25), Optional()]
    )

    bio = TextAreaField(
        'Bio (Optional)'
    )

    image_url = StringField(
        "Image URL (Optional)",
        validators=[URL(), Length(max=255), Optional()]
    )


class AddRatingForm(FlaskForm):
    """Form for creating a rating for an album"""

    rating = RadioField(
        "Stars",
        choices=[(0.5, 0.5), (1, 1), (1.5, 1.5), (2, 2), (2.5, 2.5), (3, 3), (3.5, 3.5), (4, 4), (4.5, 4.5), (5, 5)],
        validators=[InputRequired(), AnyOf(['0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5'])]
    )

    favorite_song = SelectField(
        "Favorite Song (Optional)"
    )

    text = TextAreaField("Thoughts")



class EditRatingForm(FlaskForm):
    """Form for creating a rating for an album"""

    rating = RadioField(
        "Stars",
        choices=[(0.5, 0.5), (1, 1), (1.5, 1.5), (2, 2), (2.5, 2.5), (3, 3), (3.5, 3.5), (4, 4), (4.5, 4.5), (5, 5)],
        validators=[InputRequired(), AnyOf(['0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5'])]
    )

    favorite_song = SelectField(
        "Favorite Song (Optional)",
        validators=[Optional()]
    )

    text = TextAreaField("Thoughts")



class CSRFProtectForm(FlaskForm):
    """Form for CSRF protection"""