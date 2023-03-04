import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import unittest
from web import create_app, db
from web.models import User, Listing, Tag, Image, LocationCitiesEnum, ListingStateEnum, ListingTypeEnum
from web.config.config import TestConfig
from unittest import mock
from flask_login import current_user
from flask import url_for, request
from datetime import datetime
from flask_testing import TestCase
    
        
class UnitTestApp(TestCase):
    def setUp(self):
        self.app = create_app(config_class = TestConfig())
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.user = User(firstName = "CS162", lastName = "Test", emailAddress = "cs162test@uni.minerva.edu", location = LocationCitiesEnum.SanFrancisco)
        db.session.add(self.user)
        listing = Listing(title = "Test Listing", description = "This is a test listing", location = LocationCitiesEnum.SanFrancisco, price = 100, state = ListingStateEnum.Available, listingType = ListingTypeEnum.Sale, author = self.user)
        db.session.add(listing)
        db.session.commit()
        
    def tearDown(self):
        db.session.drop_all()
        self.ctx.pop()
    
    def test_non_authenticated_user(self):
        with self.client as c:
            # Send a request to the home route
            response = c.get('/', follow_redirects=True)
            # Assert that the response is a redirect to the login page
            self.assertEqual(response.status_code, 302)
            self.assertTrue('login' in response.location)
        
    def test_route_with_authenticated_user_no_filters(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the home route with no filters
            response = c.get('/', follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the listings query was not filtered
            self.assertEqual(response.context['filters'], [])

        
        
    def test_route_with_authenticated_user_and_search_query(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the home route with a search query
            response = c.get('/', follow_redirects=True, query_string='search=chair')
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the listings query was filtered by the search query
            self.assertEqual(response.context['filters'][0], Listing.title.contains('chair'))

        
        
    def test_route_with_authenticated_user_and_pagination(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the home route with pagination parameters
            response = c.get('/', follow_redirects=True, query_string='page=2&per_page=30')
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the listings query was paginated correctly
            self.assertEqual(response.context['listings'].page, 2)
            self.assertEqual(response.context['listings'].per_page, 30)

        
    
    def test_route_with_authenticated_user_and_filters(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the home route with various filters
            filters = {'location': 'San Francisco', 'listingType': 'Buy', 'tags': ['Furniture'], 'dateOffset': 7}
            response = c.get('/', follow_redirects=True, query_string=filters)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the listings query was filtered correctly
            self.assertEqual(response.context['filters'][0], Listing.location.value == 'San Francisco')
            self.assertEqual(response.context['filters'][1], Listing.listingType.value == 'Buy')
            self.assertEqual(response.context['filters'][2], Tag.name.in_(['Furniture']))
            self.assertEqual(response.context['filters'][3], Listing.datePosted.between(datetime.Today.addDays(-7), datetime.Today))

        
        
    def test_route_with_authenticated_user_and_date_offset(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the home route with a date offset filter
            response = c.get('/', follow_redirects=True, query_string='dateOffset=7')
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the listings query was filtered by the date offset
            self.assertEqual(response.context['filters'][0], Listing.datePosted.between(datetime.Today.addDays(-7), datetime.Today))

        
        
    def test_route_with_authenticated_user_pagination_and_filters(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the home route with pagination and various filters
            filters = {'location': 'San Francisco', 'listingType': 'Buy', 'tags': ['Furniture'], 'dateOffset': 7, 'page': 3, 'per_page': 25}
            response = c.get('/', follow_redirects=True, query_string=filters)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the listings query was filtered and paginated correctly
            self.assertEqual(response.context['filters'][0], Listing.location.value == 'San Francisco')
            self.assertEqual(response.context['filters'][1], Listing.listingType.value == 'Buy')
            self.assertEqual(response.context['filters'][2], Tag.name.in_(['Furniture']))
            self.assertEqual(response.context['filters'][3], Listing.datePosted.between(datetime.Today.addDays(-7), datetime.Today))
            self.assertEqual(response.context['listings'].page, 3)
            self.assertEqual(response.context['listings'].per_page, 25)

        
    def test_route_with_authenticated_user_search_query_and_filters(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the home route with a search query and various filters
            filters = {'location': 'San Francisco', 'listingType': 'Buy', 'tags': ['Furniture'], 'dateOffset': 7, 'search': 'chair'}
            response = c.get('/', follow_redirects=True, query_string=filters)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the listings query was filtered and searched correctly
            self.assertEqual(response.context['filters'][0], Listing.location.value == 'San Francisco')
            self.assertEqual(response.context['filters'][1], Listing.listingType.value == 'Buy')
            self.assertEqual(response.context['filters'][2], Tag.name.in_(['Furniture']))
            self.assertEqual(response.context['filters'][3], Listing.datePosted.between(datetime.Today.addDays(-7), datetime.Today))
            self.assertEqual(response.context['filters'][4], Listing.title.contains('chair'))

        
        
    def test_account_route_valid_post_request(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a valid POST request to the account route
            response = c.post('/user/', follow_redirects=True, data={'firstName': 'John', 'lastName': 'Doe', 'location': 'San Francisco', 'telegramID': '1234567890'})
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('users.html')
            # Assert that the form object in the response context is valid
            self.assertTrue(response.context['form'].validate_on_submit())
            # Assert that the user's data was updated in the database
            user = User.query.filter_by(id=1).first()
            self.assertEqual(user.firstName, 'John')
            self.assertEqual(user.lastName, 'Doe')
            self.assertEqual(user.location.value, 'San Francisco')
            self.assertEqual(user.telegram, '1234567890')

        
    def test_account_route_invalid_post_request(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send an invalid POST request to the account route
            response = c.post('/user/', follow_redirects=True, data={'location': 'San Francisco'})
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('users.html')
            # Assert that the form object in the response context is invalid
            self.assertFalse(response.context['form'].validate_on_submit())

        
        
    def test_account_route_get_request(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a GET request to the account route
            response = c.get('/user/', follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('users.html')
            # Assert that the form object in the response context is populated with the user's data
            self.assertEqual(response.context['form'].firstName.data, current_user.firstName)
            self.assertEqual(response.context['form'].lastName.data, current_user.lastName)
            self.assertEqual(response.context['form'].location.data, current_user.location.value)
            self.assertEqual(response.context['form'].telegramID.data, current_user.telegramID)
            # Assert that the listings object in the response context is the user's listings
            self.assertEqual(response.context['listings'], current_user.listings)

        
        
    def test_account_route_unauthenticated_request(self):
        with self.client as c:
            # Send a request to the account route without an authenticated user
            response = c.get('/user/', follow_redirects=True)
            # Assert that the response is a redirect
            self.assertEqual(response.status_code, 302)
            # Assert that the user was redirected to the login page
            self.assertEqual(response.location, 'http://localhost/login')

            
    def test_listing_route_valid_id(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the listing route with a valid listing ID
            response = c.get('/listing/1', follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('templete_listing.html')
            presListing = Listing.query.get(1)
            # Assert that the form object in the response context is populated with the listing's data
            self.assertEqual(response.context['form'].title.data, presListing.title)
            self.assertEqual(response.context['form'].description.data, presListing.description)
            self.assertEqual(response.context['form'].state.data, presListing.state.value)
            self.assertEqual(response.context['form'].location.data, presListing.location.value)
            self.assertEqual(response.context['form'].price.data, presListing.price)
            self.assertEqual(response.context['form'].images.data, presListing.images)
            self.assertEqual(response.context['form'].tags.data, [tag.name for tag in presListing.tags])
            self.assertEqual(response.context['form'].listingType.data, presListing.listingType.value)

            
    def test_listing_route_invalid_id(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the listing route with an invalid listing ID
            response = c.get('/listing/100', follow_redirects=True)
            # Assert that the response is a 404 error
            self.assertEqual(response.status_code, 404)

        
    def test_listing_route_unauthenticated_user(self):
        with self.client as c:
            # Send a request to the listing route without an authenticated user
            response = c.get('/listing/1', follow_redirects=True)
            # Assert that the response is a redirect
            self.assertEqual(response.status_code, 302)
            # Assert that the user was redirected to the login page
            self.assertEqual(response.location, 'http://localhost/login')


    def test_listing_route_authenticated_user(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a request to the listing route with an authenticated user
            response = c.get('/listing/1', follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('templete_listing.html')
            presListing = Listing.query.get(1)
            # Assert that the form object in the response context is populated with the listing's data
            self.assertEqual(response.context['form'].title.data, presListing.title)
            self.assertEqual(response.context['form'].description.data, presListing.description)
            self.assertEqual(response.context['form'].state.data, presListing.state.value)
            self.assertEqual(response.context['form'].location.data, presListing.location.value)
            self.assertEqual(response.context['form'].price.data, presListing.price)
            self.assertEqual(response.context['form'].images.data, presListing.images)
            self.assertEqual(response.context['form'].tags.data, [tag.name for tag in presListing.tags])
            self.assertEqual(response.context['form'].listingType.data, presListing.listingType.value)


                
                
    def test_new_listing_route_valid_post_request(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Set up a valid POST request to the new_listing route
            response = c.post('/listing/new', follow_redirects=True, data={'title': 'Test Listing', 'description': 'This is a test listing', 'location': 'San Francisco', 'price': 100, 'state': 'Available', 'listingType': 'Buy', 'tags': ['Electronics', 'Furniture']})
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('listing.html')
            # Assert that the new listing was added to the database
            listing = Listing.query.filter_by(title='Test Listing').first()
            self.assertIsNotNone(listing)
            # Assert that the listing's data is correct
            self.assertEqual(listing.description, 'This is a test listing')
            self.assertEqual(listing.location, LocationCitiesEnum('San Francisco'))
            self.assertEqual(listing.price, 100)
            self.assertEqual(listing.state, ListingStateEnum('Available'))
            self.assertEqual(listing.listingType, ListingTypeEnum('Buy'))
            self.assertEqual([tag.name for tag in listing.tags], ['Electronics', 'Furniture'])

        
    def test_new_listing_route_invalid_post_request(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Set up an invalid POST request to the new_listing route (missing the required 'title' field)
            response = c.post('/listing/new', follow_redirects=True, data={'description': 'This is a test listing', 'location': 'San Francisco', 'price': 100, 'state': 'Available', 'listingType': 'Buy', 'tags': ['Electronics', 'Furniture']})
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('new_listing.html')
            # Assert that the form object in the response context has errors
            self.assertTrue(response.context['form'].errors)
            # Assert that the new listing was not added to the database
            listing = Listing.query.filter_by(title='Test Listing').first()
            self.assertIsNone(listing)

        
        
    def test_new_listing_route_get_request(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a GET request to the new_listing route
            response = c.get('/listing/new', follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('new_listing.html')
            # Assert that the form object in the response context is populated with the user's location
            self.assertEqual(response.context['form'].location.data, current_user.location)

            
    def test_new_listing_route_unauthenticated_user(self):
        with self.client as c:
            # Send a request to the new_listing route without an authenticated user
            response = c.get('/listing/new', follow_redirects=True)
            # Assert that the response is a redirect
            self.assertEqual(response.status_code, 302)
            # Assert that the user was redirected to the login page
            self.assertEqual(response.location, 'http://localhost/login')

            
    def test_update_listing_redirects_if_not_logged_in(self):
        with self.client as c:
            # Send a request to the update_listing route without an authenticated user
            response = c.post('/listing/1/update', follow_redirects=True)
            # Assert that the response is a redirect
            self.assertEqual(response.status_code, 302)
            # Assert that the user was redirected to the login page
            self.assertEqual(response.location, 'http://localhost/login')

            
    def test_update_listing_not_author(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 2
                sess['_fresh'] = True
            # Send a POST request to the update_listing route for a listing that the user is not the author of
            response = c.post('/listing/1/update', follow_redirects=True)
            # Assert that the response is a 403 error
            self.assertEqual(response.status_code, 403)


                

    def test_update_listing_prepopulates_form(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a GET request to the update_listing route
            response = c.get('/listing/1/update', follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('update_listing.html')
            # Assert that the form object in the response context is prepopulated with the listing data
            self.assertEqual(response.context['form'].title.data, 'Test Listing')
            self.assertEqual(response.context['form'].description.data, 'This is a test listing')
            self.assertEqual(response.context['form'].location.data, 'San Francisco')
            self.assertEqual(response.context['form'].price.data, 100)
            self.assertEqual(response.context['form'].state.data, 'Available')
            self.assertEqual(response.context['form'].listingType.data, 'Buy')
            self.assertEqual(response.context['form'].tags.data, ['Electronics', 'Furniture'])

            
    def test_update_listing_form_validates_and_updates(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a POST request to the update_listing route with valid form data
            response = c.post('/listing/1/update', data = {'title': 'Updated Test Listing', 'description': 'This is an updated test listing',
                                                        'location': 'San Francisco', 'price': 150, 'state': 'Available',
                                                        'listingType': 'Buy', 'tags': ['Electronics', 'Furniture']}, follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('templete_listing.html')
            # Assert that the listing was updated in the database
            updated_listing = Listing.query.get(1)
            self.assertEqual(updated_listing.title, 'Updated Test Listing')
            self.assertEqual(updated_listing.description, 'This is an updated test listing')
            self.assertEqual(updated_listing.location, LocationCitiesEnum.SANFRANCISCO)
            self.assertEqual(updated_listing.price, 150)
            self.assertEqual(updated_listing.state, ListingStateEnum.AVAILABLE)
            self.assertEqual(updated_listing.listingType, ListingTypeEnum.Buy)
            self.assertEqual([tag.name for tag in updated_listing.tags], ['Electronics', 'Furniture'])

        
    
    def test_update_listing_form_displays_error_messages(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a POST request to the update_listing route with invalid form data
            response = c.post('/listing/1/update', data = {'title': '', 'description': '', 'location': '', 'price': None, 'state': '', 'listingType': '', 'tags': []}, follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('templete_listing.html')
            # Assert that the form contains error messages for each required field
            self.assertContains(response, 'This field is required')

        
    def test_update_listing_uses_default_image(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a POST request to the update_listing route without any images
            response = c.post('/listing/1/update', data = {'title': 'Updated Test Listing', 'description': 'This is an updated test listing',
                                                        'location': 'San Francisco', 'price': 150, 'state': 'Available',
                                                        'listingType': 'Buy', 'tags': ['Electronics', 'Furniture']}, follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('templete_listing.html')
            # Assert that the listing uses the default image
            updated_listing = Listing.query.get(1)
            self.assertEqual(updated_listing.images[0].image_file, 'defaultListing.png')

        
    def test_update_listing_limits_state_choices(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a POST request to the update_listing route with a state not in the allowed choices
            response = c.post('/listing/1/update', data = {'title': 'Updated Test Listing', 'description': 'This is an updated test listing',
                                                        'location': 'San Francisco', 'price': 150, 'state': 'Invalid',
                                                        'listingType': 'Buy', 'tags': ['Electronics', 'Furniture']}, follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('templete_listing.html')
            # Assert that the form contains an error message for the invalid state
            self.assertContains(response, 'Not a valid choice')

            
    def test_delete_listing_redirects_if_not_logged_in(self):
        with self.client as c:
            # Send a POST request to the delete_listing route without being logged in
            response = c.post('/listing/1/delete', follow_redirects=True)
            # Assert that the response is a redirect
            self.assertEqual(response.status_code, 302)
            # Assert that the response redirects to the login page
            self.assertRedirects(response, '/login')
            
    def test_delete_listing_not_author(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a POST request to the delete_listing route with a listing id for a listing not created by the authenticated user
            response = c.post('/listing/2/delete', follow_redirects=True)
            # Assert that the response is a 403 error
            self.assertEqual(response.status_code, 403)

                
    def test_delete_listing_invalid_id(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a POST request to the delete_listing route with an invalid listing id
            response = c.post('/listing/999/delete', follow_redirects=True)
            # Assert that the response is a 404 error
            self.assertEqual(response.status_code, 404)
        
    def test_delete_listing(self):
        with self.client as c:
            # Set up an authenticated user
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['_fresh'] = True
            # Send a POST request to the delete_listing route with a valid listing id for a listing created by the authenticated user
            response = c.post('/listing/1/delete', follow_redirects=True)
            # Assert that the response is a success
            self.assertEqual(response.status_code, 200)
            # Assert that the correct template was rendered
            self.assertTemplateUsed('index.html')
            # Assert that the flash message for a successful delete is displayed
            self.assertContains(response, 'Your Listing has been deleted!')
        
    def test_login_route_redirects_authenticated_user(self):
        # start a new client session
        with self.client as c:
            # start a new session transaction
            with c.session_transaction() as sess:
                # set the user_id in the session to 1
                sess["user_id"] = 1
                # set the session as "fresh"
                sess["_fresh"] = True
            # send a GET request to the login route, following redirects
            response = c.get("/login", follow_redirects=True)
            # assert that the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)
            # assert that the response location is the root route
            self.assertEqual(response.location, 'http://localhost/')

            
    def test_login_route_retrieves_google_provider_config(self):
        # start a new client session
        with self.client as c:
            # start a mock patch for the get_google_provider_cfg function
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                # define a mock configuration object
                mock_cfg = {"authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth"}
                # set the mock configuration as the return value of the mock function
                mock_get_cfg.return_value = mock_cfg
                # send a GET request to the login route
                c.get("/login")
                # assert that the mock function was called once
                mock_get_cfg.assert_called_once()

            # start a mock patch for the web.client object
            with mock.patch("web.client") as mock_client:
                # assert that the prepare_request_uri method of the mock client object was called with the correct arguments
                mock_client.prepare_request_uri.assert_called_with(
                    "https://accounts.google.com/o/oauth2/v2/auth",
                    redirect_uri=mock.ANY,
                    scope=["openid", "email", "profile"],
                    hd = "minerva.edu",
                    state = mock.ANY
                )

                
    def test_login_route_renders_login_page(self):
        # start a new client session
        with self.client as c:
            # start a mock patch for the get_google_provider_cfg function
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                # define a mock configuration object
                mock_cfg = {"authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth"}
                # set the mock configuration as the return value of the mock function
                mock_get_cfg.return_value = mock_cfg
                # start a mock patch for the web.client object
                with mock.patch("web.client") as mock_client:
                    # set the return value of the prepare_request_uri method to a mock URI
                    mock_client.prepare_request_uri.return_value = "https://accounts.google.com/o/oauth2/v2/auth?test=test"
                    # send a GET request to the login route
                    response = c.get("/login")
                    # assert that the response status code is 200 (OK)
                    self.assertEqual(response.status_code, 200)
                    # assert that the response data contains the string "Login using google"
                    self.assertIn("Login using google", response.data)
                    # assert that the response data contains the mock URI
                    self.assertIn("https://accounts.google.com/o/oauth2/v2/auth?test=test", response.data)

                    
    
    def test_login_route_processes_google_login_callback(self):
        # start a new client session
        with self.client as c:
            # start a mock patch for the get_google_provider_cfg function
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                # define a mock configuration object
                mock_cfg = {"authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth"}
                # set the mock configuration as the return value of the mock function
                mock_get_cfg.return_value = mock_cfg
                # start a mock patch for the web.client object
                with mock.patch("web.client") as mock_client:
                    # set the return value of the prepare_request_uri method to a mock URI
                    mock_client.prepare_request_uri.return_value = "https://accounts.google.com/o/oauth2/v2/auth?test=test"
                    # start a mock patch for the handle_callback function
                    with mock.patch("web.handle_callback") as mock_callback:
                        # set the return value of the mock callback function to a tuple of test values
                        mock_callback.return_value = ("test@example.com", "test_user")
                        # send a GET request to the login route, with a "next" query parameter
                        response = c.get("/login?next=http://test.com")
                        # assert that the response status code is 302 (Found)
                        self.assertEqual(response.status_code, 302)
                        # assert that the "next" query parameter is included in the response location
                        self.assertIn("http://test.com", response.location)

                        
    def test_login_callback_route_redirects_authenticated_user(self):
        # start a new client session
        with self.client as c:
            # start a new session transaction
            with c.session_transaction() as sess:
                # set the user_id in the session to 1
                sess["user_id"] = 1
                # set the session as "fresh"
                sess["_fresh"] = True
            # send a GET request to the login/callback route, following redirects
            response = c.get("/login/callback", follow_redirects=True)
            # assert that the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)
            # assert that the request path is the home route
            self.assertEqual(request.path, url_for('home'))

            
    def test_login_callback_route_retrieves_auth_code_and_email_domain(self):
        with self.client as c:
            response = c.get("/login/callback?code=test_code&hd=test_domain")
            self.assertEqual(response.status_code, 302)
            self.assertIn("test_code", response.location)
            self.assertIn("test_domain", response.location)
            
    def test_login_callback_route_retrieves_google_provider_config(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token"}
                mock_get_cfg.return_value = mock_cfg
                c.get("/login/callback?code=test_code&hd=test_domain")
                mock_get_cfg.assert_called_once()

            with mock.patch("web.client") as mock_client:
                mock_client.prepare_token_request.assert_called_with(
                    "https://oauth2.googleapis.com/token",
                    authorization_response="http://localhost/login/callback?code=test_code&hd=test_domain",
                    redirect_url="http://localhost/login/callback",
                    code="test_code"
                )
                
    def test_login_callback_route_processes_token_response(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "test_domain", "given_name": "test_first", "family_name": "test_last"}
                            c.get("/login/callback?code=test_code&hd=test_domain")
                            mock_client.parse_request_body_response.assert_called_with('{"access_token": "test_token"}')
                            mock_get.assert_called_with("https://oauth2.googleapis.com/userinfo", headers={}, data="")
                            
                            
    def test_login_callback_route_handles_invalid_email(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": False, "hd": "test_domain", "given_name": "test_first", "family_name": "test_last"}
                            response = c.get("/login/callback?code=test_code&hd=test_domain")
                            self.assertEqual(response.status_code, 302)
                            self.assertIn(url_for("login"), response.location)
                            self.assertIn("Invalid Email Domain, only minerva.edu emails are allowed", response.data)
                            
    def test_login_callback_route_creates_new_user(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            with mock.patch("web.db") as mock_db:
                                with mock.patch("web.models.User") as mock_user:
                                    mock_user.query.filter_by.return_value.first.return_value = None
                                    response = c.get("/login/callback?code=test_code&hd=minerva.edu")
                                    mock_db.session.add.assert_called_with(mock_user())
                                    mock_db.session.commit.assert_called_once()
                                    self.assertEqual(response.status_code, 302)
                                    self.assertIn(url_for("home"), response.location)
                                    self.assertIn("You have successfully signed up!", response.data)
                                    
    def test_login_callback_route_logs_in_existing_user(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            with mock.patch("web.db") as mock_db:
                                with mock.patch("web.models.User") as mock_user:
                                    mock_user.query.filter_by.return_value.first.return_value = mock_user
                                    response = c.get("/login/callback?code=test_code&hd=minerva.edu")
                                    self.assertEqual(response.status_code, 302)
                                    self.assertIn(url_for("home"), response.location)
                                    self.assertIn("You have successfully signed in!", response.data)
                                    
    def test_login_callback_route_redirects_to_next_page(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            with mock.patch("web.db") as mock_db:
                                with mock.patch("web.models.User") as mock_user:
                                    mock_user.query.filter_by.return_value.first.return_value = mock_user
                                    response = c.get("/login/callback?code=test_code&hd=minerva.edu&state=%2Ftest_next")
                                    self.assertEqual(response.status_code, 302)
                                    self.assertIn("/test_next", response.location)
                                    
    
    def test_login_callback_route_handles_missing_hd_param(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "given_name": "test_first", "family_name": "test_last"}
                            response = c.get("/login/callback?code=test_code")
                            self.assertEqual(response.status_code, 302)
                            self.assertIn(url_for("login"), response.location)
                            self.assertIn("Invalid Email Domain, only minerva.edu emails are allowed", response.data)
                            
    def test_login_callback_route_handles_invalid_email_domain(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "invalid.edu", "given_name": "test_first", "family_name": "test_last"}
                            response = c.get("/login/callback?code=test_code&hd=invalid.edu")
                            self.assertEqual(response.status_code, 302)
                            self.assertIn(url_for("login"), response.location)
                            self.assertIn("Invalid Email Domain, only minerva.edu emails are allowed", response.data)
                            
    def test_login_callback_route_handles_unverified_email(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": False, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            response = c.get("/login/callback?code=test_code&hd=minerva.edu")
                            self.assertEqual(response.status_code, 302)
                            self.assertIn(url_for("login"), response.location)
                            self.assertIn("User email not supported, please use a verified uni.minerva.edu email", response.data)
                            
                            
    def test_login_callback_route_creates_new_user_if_does_not_exist(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            with mock.patch("web.db") as mock_db:
                                with mock.patch("web.models.User") as mock_user:
                                    mock_user.query.filter_by.return_value.first.return_value = None
                                    response = c.get("/login/callback?code=test_code&hd=minerva.edu")
                                    self.assertEqual(response.status_code, 302)
                                    self.assertIn(url_for("home"), response.location)
                                    self.assertIn("You have successfully signed up!", response.data)
                                
    def test_login_callback_route_handles_error_getting_tokens(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.side_effect = Exception("Error getting tokens")
                        response = c.get("/login/callback?code=test_code&hd=minerva.edu")
                        self.assertEqual(response.status_code, 302)
                        self.assertIn(url_for("login"), response.location)
                        self.assertIn("Error getting tokens", response.data)
                        
                        
    def test_login_callback_route_logs_in_existing_user(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            with mock.patch("web.db") as mock_db:
                                with mock.patch("web.models.User") as mock_user:
                                    mock_user.query.filter_by.return_value.first.return_value = mock_user
                                    response = c.get("/login/callback?code=test_code&hd=minerva.edu")
                                    self.assertEqual(response.status_code, 302)
                                    self.assertIn(url_for("home"), response.location)
                                    self.assertIn("You have successfully signed in!", response.data)
                                    
    def test_login_callback_route_handles_missing_or_invalid_next_param(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            with mock.patch("web.db") as mock_db:
                                with mock.patch("web.models.User") as mock_user:
                                    mock_user.query.filter_by.return_value.first.return_value = mock_user
                                    response = c.get("/login/callback?code=test_code&hd=minerva.edu")
                                    self.assertEqual(response.status_code, 302)
                                    self.assertIn(url_for("home"), response.location)

                                    response = c.get("/login/callback?code=test_code&hd=minerva.edu&state=invalid_url")
                                    self.assertEqual(response.status_code, 302)
                                    self.assertIn(url_for("home"), response.location)
                                    
    def test_login_callback_route_only_accessible_via_get(self):
        with self.client as c:
            with mock.patch("web.get_google_provider_cfg") as mock_get_cfg:
                mock_cfg = {"token_endpoint": "https://oauth2.googleapis.com/token", "userinfo_endpoint": "https://oauth2.googleapis.com/userinfo"}
                mock_get_cfg.return_value = mock_cfg
                with mock.patch("web.client") as mock_client:
                    mock_client.prepare_token_request.return_value = ("https://oauth2.googleapis.com/token", {}, "")
                    mock_client.add_token.return_value = ("https://oauth2.googleapis.com/userinfo", {}, "")
                    with mock.patch("requests.post") as mock_post:
                        mock_post.return_value.json.return_value = {"access_token": "test_token"}
                        with mock.patch("requests.get") as mock_get:
                            mock_get.return_value.json.return_value = {"sub": "test_id", "email": "test@example.com", "email_verified": True, "hd": "minerva.edu", "given_name": "test_first", "family_name": "test_last"}
                            with mock.patch("web.db") as mock_db:
                                with mock.patch("web.models.User") as mock_user:
                                    mock_user.query.filter_by.return_value.first.return_value = mock_user
                                    response = c.post("/login/callback?code=test_code&hd=minerva.edu")
                                    self.assertEqual(response.status_code, 405)
                                    
    def test_login_callback_route_handles_missing_code(self):
        with self.client as c:
            response = c.get("/login/callback")
            self.assertEqual(response.status_code, 302)
            self.assertIn(url_for("login"), response.location)
            self.assertIn("Invalid request, no code parameter provided", response.data)

    def test_login_callback_route_handles_missing_hd(self):
        with self.client as c:
            response = c.get("/login/callback?code=test_code")
            self.assertEqual(response.status_code, 302)
            self.assertIn(url_for("login"), response.location)
            self.assertIn("Invalid Email Domain, only minerva.edu emails are allowed", response.data)

if __name__ == "__main__":
    unittest.main()
            