from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, TextAreaField, IntegerField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError, Email, Optional
from web.models import User, Listing, ListingStateEnum, ListingTypeEnum, LocationCitiesEnum


class UpdateAccountForm(FlaskForm):
    """
    Form to update the user account

    Fields:
        firstName: The first name of the user
        lastName: The last name of the user
        telegramID: The telegram id of the user
        location: The location of the user
        submit: Submit button
    """
    firstName = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=50)])
    
    lastName = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=50)])
    
    telegramID = StringField('Telegram ID Phone',
                           validators=[DataRequired(), Length(min=10, max=15)])
    
    location = SelectField('Location', 
                           validators = [DataRequired()], 
                           choices = [str(e.value) for e in LocationCitiesEnum])
    
    submit = SubmitField('Update Account')
            
class ListingForm(FlaskForm):
    """
    Form to create a new listing

    Fields:
        title: The title of the listing
        description: The description of the listing
        location: The location of the listing
        price: The price of the listing
        images: The image of the listing
        tags: The tags of the listing
        state: The state of the listing
        listingType: The type of the listing
        submit: Submit button
    """
    title = StringField('Title', 
                        validators = [DataRequired(), 
                                      Length(min = 5, max = 20)])
    
    description = TextAreaField('Description', 
                                validators = [DataRequired(), Length(min=5, max=200)])
    
    location = SelectField('Location', 
                           validators = [DataRequired()], 
                           choices = [str(e.value) for e in LocationCitiesEnum])
    
    price = IntegerField('Price', validators=[Optional()])
    
    images = MultipleFileField('Add listing Image', 
                               validators = [FileAllowed(['jpg', 'png'], 'Please upload only JPG or PNG Images here!')])
    
    tags = SelectMultipleField('Tags')
    
    state = SelectField('Listing State', 
                         validators = [DataRequired()], choices = [str(e.value) for e in ListingStateEnum if e != ListingStateEnum.DELETED])
    
    listingType = SelectField('Listing Type', 
                              validators = [DataRequired()], 
                              choices = [str(e.value) for e in ListingTypeEnum])
    
    submit = SubmitField('Submit listing')