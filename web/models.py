from web import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from flask import current_app
import enum

class ListingTypeEnum(enum.Enum):
    """
    Stores the different types of listings
    """
    BUY = 'Buy'
    SELL = 'Sell'
    INQUIRY = 'Inquiry'
    
class ListingStateEnum(enum.Enum):
    """
    Stores the different states of listings
    """
    AVAILABLE = 'Available'
    UNAVAILABLE = 'Unavailable'
    SATISFIED = 'Satisfied'
    DELETED = 'Deleted'
    
class LocationCitiesEnum(enum.Enum):
    """
    Stores the difernt locations of the listings
    """
    SANFRANCISCO = "San Francisco"
    BERLIN = "Berlin"
    BUENOSAIRES = "Buenos Aires"
    LONDON = "London"
    TAIPEI = "Taipei"
    SEOUL = "Seoul"
    HYDERABAD = "Hyderabad"
    REMOTE = "Remote"

@login_manager.user_loader
def load_user(user_id):
    """
    Queries the database for the user with the given id
    """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    Crate a table for the users

    Columns:
        id: The id of the user
        firstName: The first name of the user
        lastName: The last name of the user
        emailAddress: The email address of the user
        listings: connections to the listings table to get all the items of teh user
        satisfied: current sate of the item of the user that had been satisfied
        location: location of the user
        telegramID: telegram id of the user

    """
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable = False)
    lastName = db.Column(db.String(50), nullable = False)
    emailAddress = db.Column(db.String(120), unique = True, nullable = False)
    listings = db.relationship('Listing', backref = 'author', foreign_keys='Listing.user_id', lazy = True)
    satisfied = db.relationship('Listing', backref = 'satisfier', foreign_keys='Listing.satisfier_id', lazy = True)
    location = db.Column(db.Enum(LocationCitiesEnum, values_callable=lambda x: [str(e.value) for e in LocationCitiesEnum]), nullable = False, default = LocationCitiesEnum.SANFRANCISCO) 
    telegramID = db.Column(db.String, unique = True)
    
    def __repr__(self):
        return f"User('{self.firstName} {self.lastName}', '{self.emailAddress}', '{self.satisfied}', '{self.listings}', '{self.telegramID}')"
    
    
class Listing(db.Model):
    """
    Create a table for the listings

    Columns:
        id: The id of the listing
        user_id: The id of the user that created the listing
        satisfier_id: The id of the user that satisfied the listing
        title: The title of the listing
        description: The description of the listing
        state: The state of the listing
        location: The location of the listing
        datePosted: The date the listing was posted
        price: The price of the listing
        images: The images of the listing
        listingType: The type of the listing
        tags: The tags of the listing

    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    satisfier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = False)
    state = db.Column(db.Enum(ListingStateEnum, values_callable=lambda x: [str(e.value) for e in ListingStateEnum]), nullable = False, default = ListingStateEnum.AVAILABLE)
    location = db.Column(db.Enum(LocationCitiesEnum, values_callable=lambda x: [str(e.value) for e in LocationCitiesEnum]), nullable = False, default = LocationCitiesEnum.SANFRANCISCO)  
    datePosted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    price = db.Column(db.Float)
    images = db.relationship('Image')
    listingType = db.Column(db.Enum(ListingTypeEnum, values_callable=lambda x: [str(e.value) for e in ListingTypeEnum]), nullable = False)
    tags = db.relationship('Tag', secondary='tagToListing', back_populates='listings')
    
    def __repr__(self):
        return f"Listing('{self.title}',\n'{self.description}',\nState: '{self.state}',\nLocation: '{self.location}',\nPrice: '{self.price}')"
    
class Tag(db.Model):
    """
    Table that stores all the tags

    Columns:
        id: The id of the tag
        name: The name of the tag
        listings: The listings that have the tag
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique = True, nullable = False)
    listings = db.relationship('Listing', secondary='tagToListing', back_populates='tags')
    
class Image(db.Model):
    """
    Table that stores all the images
    
    Columns:

        id: The id of the image
        listing_id: The id of the listing that the image belongs to
        image_file: The name of the image file
    """
    id = db.Column(db.Integer, primary_key = True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable = False)
    image_file = db.Column(db.String(20), default = 'defaultListing.png')
    
tagToListing = db.Table('tagToListing',
                    db.Column('tag_id', db.Integer, db.ForeignKey("tag.id"), primary_key = True),
                    db.Column('listing_id', db.Integer, db.ForeignKey("listing.id"), primary_key = True)) 

    
class MessageEvent(db.Model):
    """
    Table that stores all the message events

    Columns:
        id: The id of the message event
        messageID: The id of the message
        relayID: The id of the relay
        eventType: The type of the event
        messageEvent: The event itself
    """
    __bind_key__ = 'messageDB'
    id = db.Column(db.Integer, primary_key = True)
    messageID = db.Column(db.String)
    relayID = db.Column(db.String)
    eventType = db.Column(db.String, nullable = False)
    messageEvent = db.Column(db.PickleType, nullable = False)
    
    def __repr(self):
        return f"Message Event('{self.messageID}, relay: {self.relayID}, event: {self.eventType}')"
    
    
class Relay(db.Model):
    """
    Table that stores all the relays
    
    Columns:
        id: The id of the relay
        name: The name of the relay
        token: The token of the relay
    """
    __bind_key__ = 'messageDB'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = True, nullable = False)
    token = db.Column(db.String, unique = True, nullable = False)
    
