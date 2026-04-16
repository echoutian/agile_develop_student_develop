from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, SelectField,FloatField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import date
from app.models import User
from app import db
import sqlalchemy as sa



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')



class CreateplanForm(FlaskForm):
    title = StringField('Plan Title', validators=[DataRequired(), Length(max=256)])
    
    deadline = DateField("Deadline", format="%Y-%m-%d", default=date.today, validators=[DataRequired()])
    submit = SubmitField("Save Plan")


class PlanEditForm(FlaskForm):
    title = StringField('plan Title', validators=[DataRequired()])
    deadline = DateField('Deadline', validators=[DataRequired()])
    submit = SubmitField('Save Plan')

class HealthForm(FlaskForm):
    title = StringField('The Health resources', validators=[DataRequired(), Length(max=255)])
    content=TextAreaField('Content', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired(), Length(max=64)])
    submit=SubmitField("Save resources")








    
    








class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(max=256)])
    task_type = SelectField('Task Type', coerce=int)
    estimated_hours = FloatField('Estimated_hours',validators=[DataRequired()])
    
    submit = SubmitField("Save Task")

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=256)])
    body = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')



class TaskTypeForm(FlaskForm):
    title = StringField('Input the task type U want!', validators=[DataRequired(), Length(max=32)])
    submit = SubmitField('Submit the task type')





class CommentForm(FlaskForm):
    body = TextAreaField('Leave a comment...', validators=[DataRequired()])
    submit = SubmitField('Reply')


