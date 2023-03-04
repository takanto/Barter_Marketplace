import os
import secrets
from datetime import datetime
from PIL import Image as Img
from web import db, client, get_google_provider_cfg, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from flask import render_template, request, redirect, url_for, abort, flash, current_app
from web.forms import UpdateAccountForm, ListingForm
from web.models import User, Listing, ListingStateEnum, ListingTypeEnum, Tag, Image, LocationCitiesEnum
from flask_login import login_user,logout_user, current_user, login_required
import requests
import json
from sqlalchemy import and_

@current_app.before_first_request
def before_first_request():
    """
    Create the database and the database table.
    Starts before the website
    """
    db.drop_all()
    db.create_all()
    db.session.add_all([Tag(name = tag) for tag in ['Electronics', 'Furniture', 'Clothing', 'Books', 'Sports', 'Tools', 'Misc']])
    db.session.commit()


@current_app.route('/')
@current_app.route('/home')
def home():
    """
    Home page

    It directs to the listing board.

    Recives:
    - Search query
    - Page number
    - Number of listings per page
    - Filters (for quarying the database)
    """
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    search_query = request.args.get('search','')
    page = request.args.get('page', 1, type = int)
    per_page = request.args.get('per_page', 20, type = int)
    tags = request.args.get('tags')
    dateOffset = request.args.get('dateOffset')
    filters = [getattr(Listing, attribute) == value for attribute, value in request.args.items() \
        if attribute in ["location", "listingType"]]
    filters.append(Listing.title.contains(search_query))
    if tags: 
        productTags = [tag.strip().lower().capitalize() for tag in tags]
        filters.append(Listing.tags.any(Tag.name.in_(productTags)))
    if dateOffset:
        today = datetime.Today
        refrDate = datetime.Today.addDays(-1*dateOffset)
        filters.append(Listing.datePosted.between(refrDate, today))
    listings = Listing.query.filter(Listing.state == "Available", and_(*filters)).order_by(Listing.datePosted.desc()).paginate(page = page, per_page = per_page)
    return render_template('index.html', listings = listings, location = request.args.get('location', 'All Locations'), search_query = search_query, tags = tags, dateOffset = dateOffset)

@current_app.route("/logout")
def logout():
    """
    Logs out the user
    """
    logout_user()
    return redirect(url_for('login'))

@current_app.route("/login", methods = ['GET', 'POST'])
def login():
    """
    Login page

    Checks if the user is already logged in, if so redirects to the home page.
    If not, it connects to the api, to redirect the user to google login
    """
    nextPage = request.args.get("next")
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        hd = "minerva.edu",
        state = nextPage
    )
    return render_template('login.html', title = 'Login', request_uri = request_uri)

@current_app.route("/login/callback")
def login_callback():
    """
    Callback page

    Handels the callback recived from google to login the user.
    """
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    hd = request.args.get("hd", "minerva.edu")
    nextPage = request.args.get("state")
    if hd != "minerva.edu" and hd != "uni.minerva.edu":
        flash('Invalid Email Domain, only minerva.edu emails are allowed', 'error')
        return redirect(url_for('login'))
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    # Now that you have tokens let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified") and (userinfo_response.json().get("hd") == "minerva.edu" or userinfo_response.json().get("hd") == "uni.minerva.edu"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_firstName = userinfo_response.json()["given_name"]
        users_lastName = userinfo_response.json()["family_name"]
        user = User.query.filter_by(emailAddress = users_email).first()
        if user is None:
            user = User(firstName = users_firstName, lastName = users_lastName, emailAddress = users_email)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("You have successfully signed up!", "success")
            flash("Please update your account information with your telegram ID for a great service.", "info")
            return redirect(url_for("account"))
        else:
            login_user(user)
            flash("You have successfully signed in!", "success")
            return redirect(nextPage) if nextPage else redirect(url_for('home'))
    else:
        flash("User email not supported, please use a verified uni.minerva.edu email", "error")
        return redirect(url_for("login"))
        

@current_app.route('/user/', methods = ['GET', 'POST'])
@login_required
def account():
    """
    Stores the user information.

    Functionality:
    - Update user information thru a form
    - Display user information
    """
    form = UpdateAccountForm()
    listings = Listing.query.filter(Listing.user_id == current_user.id, Listing.state != ListingStateEnum.DELETED).all()
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        current_user.telegramID = form.telegramID.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
        form.location.data = current_user.location
        form.telegramID.data = current_user.telegramID
        
    return render_template('users.html', form=form, listings=listings)

def save_picture(form_picture):
    """
    Changes the format of the uploaded picture to fit the database and display structure.
    Changes the size of the image to 166x166 and saves it to the static folder.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    i = Img.open(form_picture)
    output_size = ((166*i.size[0])//i.size[1], 166)
    i.thumbnail(output_size, Img.ANTIALIAS)
    i.save(picture_path)
    
    return picture_fn

@current_app.route('/listing/<int:listing_id>')
def listing(listing_id):
    """
    Stores the listing information.

    Connects to the database and displays the listing information
    """
    if not current_user.is_authenticated:
        return redirect(url_for('login', next = f"/listing/{listing_id}"))
    presListing = Listing.query.get_or_404(listing_id)
    tags = presListing.tags
    form = ListingForm()
    form.tags.choices = [tag.name for tag in Tag.query.all()]
    form.title.data = presListing.title
    form.description.data = presListing.description
    form.state.data = presListing.state.value
    form.location.data = presListing.location.value
    form.price.data = presListing.price
    form.images.data = presListing.images
    form.tags.data = [tag.name for tag in tags]
    form.listingType.data = presListing.listingType.value
    return render_template('templete_listing.html', item = presListing, tags = tags, form = form)

@current_app.route('/listing/new', methods = ['GET', 'POST'])
@login_required
def new_listing():
    """
    Using the form, creates a new listing and stores it in the database.
    """
    form = ListingForm()
    form.tags.choices = [tag.name for tag in Tag.query.all()]
    if form.validate_on_submit():
        image_files = [Image(image_file = save_picture(img)) for img in form.images.data if img.filename != '']
        image_files = [Image(image_file = 'defaultListing.png')] if not image_files else image_files
        newListing = Listing(title = form.title.data, description  = form.description.data, location = LocationCitiesEnum(form.location.data),
                             price = form.price.data, author = current_user, images = image_files, state = ListingStateEnum(form.state.data),
                             listingType = ListingTypeEnum(form.listingType.data))
        tagList = []
        if form.tags.data:
            for tag in form.tags.data:
                tag = tag.strip().lower().capitalize()
                existing_tag = Tag.query.filter_by(name = tag).first()
                if not existing_tag:
                    new_tag = Tag(name = tag)
                    db.session.add(new_tag)
                    tagList.append(new_tag)
                else:
                    tagList.append(existing_tag)
        newListing.tags = tagList  
        db.session.add(newListing)
        db.session.commit()
        flash('Your Listing has been created', 'success')
        return redirect(url_for('listing', listing_id = newListing.id))
    elif request.method == "GET":
        form.location.data = current_user.location
    return render_template('new_listing.html', form = form)

@current_app.route('/listing/<int:listing_id>/update', methods = ['GET', 'POST'])
@login_required
def update_listing(listing_id):
    """
    Using the form, updates the listing and stores it in the database.
    """
    presListing = Listing.query.get_or_404(listing_id)
    if presListing.author != current_user:
        abort(403)
    form = ListingForm()
    form.tags.choices = [tag.name for tag in Tag.query.all()]
    if form.validate_on_submit():
        image_files = ['defaultListing.png']
        if form.images.data:
            image_files = [Image(image_file = save_picture(img)) for img in form.images.data if img.filename != '']
        updated_images = []
        for image in image_files:
            existing_image = Image.query.filter_by(listing_id = presListing.id, image_file = image).first()
            if not existing_image:
                existing_image = Image(image_file = image)
                db.session.add(existing_image)
            updated_images.append(existing_image)
            
        presListing.title = form.title.data
        presListing.description = form.description.data
        presListing.state = ListingStateEnum(form.state.data)
        presListing.listingType = ListingTypeEnum(form.listingType.data)
        presListing.location = LocationCitiesEnum(form.location.data)
        presListing.price = form.price.data
        presListing.images = updated_images
        if form.tags.data:
            tags = form.tags.data
            for tag in tags:
                tag = tag.strip().lower().capitalize()
                existing_tag = Tag.query.filter_by(name = tag).first()
                tagList = []
                if not existing_tag:
                    new_tag = Tag(name = tag)
                    db.session.add(new_tag)
                    tagList.append(new_tag)
                else:
                    tagList.append(existing_tag)
        presListing.tags = tagList     
        presListing.datePosted = datetime.utcnow()
        db.session.commit()
        flash('Your listing has been updated!', 'success')
    
    return redirect(url_for('listing', listing_id = listing_id))

@current_app.route("/listing/<int:listing_id>/delete", methods=['POST'])
@login_required
def delete_listing(listing_id):
    """
    Deletes the listing from the database.
    """
    listing = Listing.query.get_or_404(listing_id)
    if listing.author != current_user:
        abort(403)
    listing.state = ListingStateEnum.DELETED
    db.session.commit()
    flash('Your Listing has been deleted!', 'success')
    return redirect(url_for('home'))