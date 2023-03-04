import unittest
import requests
import sqlalchemy as sa


import requests
import psycopg2
import os
import requests
import subprocess
import sys
import time
import unittest

# All the docker file folder 22/web


class DockerComposeTestCase(unittest.TestCase):
    compose_file = None
    show_docker_compose_output = False

    def setUp(self):
        compose_file = os.path.join(
            os.path.dirname(__file__), "compose",
            "{}.yml".format(self.compose_file))
        popen_kwargs = {}
        if not self.show_docker_compose_output:
            popen_kwargs = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
            }
        proc = subprocess.Popen(
            ["docker-compose", "-f", compose_file, "up"], **popen_kwargs)

        def cleanup():
            proc.kill()
            subprocess.call(
                ["docker-compose", "-f", compose_file, "kill"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.call(
                ["docker-compose", "-f", compose_file, "rm", "-f"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(cleanup)

    def get_docker_host(self):
        if not hasattr(self, "_docker_host"):
            #if "windows" in sys.platform:
            docker_host = "localhost"
            #else:
            #docker_host = subprocess.check_output(["docker-machine", "ip", "dev"]).strip().decode("unicode_escape")
            self._docker_host = docker_host
        return self._docker_host

    def curl_until_success(self, port, endpoint="/", params={}):
        for i in range(10):
            try:
                response = requests.get("http://{}:{}{}".format(
                    self.get_docker_host(), port, endpoint), params=params)
            except requests.exceptions.ConnectionError:
                pass
            else:
                return response
            time.sleep(1)
        else:
            raise Exception("service didn't start in time")

class AppTestCase(DockerComposeTestCase):
    def setUp(self):
        super(AppTestCase, self).setUp()

        self._tokens = {}
        self.curl_until_success(5000)


    def test_valid_listing(self):
        SERVER = "http://{}:5000".format(self.get_docker_host())
        listing_test_data = {
                    "title": "test listing",
                    "description": "test description",
                    "location": "Buenos Aires",
                    "price": "100",
                    "tags": "test, tags",
                    "state": "Available",
                    "listingType": "Buy",
                }
        r = requests.post(SERVER + '/listing', data= listing_test_data)
        assert r.status_code == 200
        """
        with engine.connect() as con:
                rs = con.execute("SELECT * FROM listing WHERE title = 'test listing'")
                self.assertEqual(rs.rowcount, 1)
        if r.status_code == 200 and awnser == int(r.text.split('.00 =')[0][-1:]):
            return True
        else:
            raise Exception("Test failed")
        """

    def test_db(self):
        listing_test_data = {
                    "title": "test listing",
                    "description": "test description",
                    "location": "Buenos Aires",
                    "price": "100",
                    "tags": "test, tags",
                    "state": "Available",
                    "listingType": "Buy",
                }
        
        """
    version: "3.2"
services:
  web:
    image: cs162-barter-marketplace
    depends_on:
      - db
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "0.2"
          memory: 64M
      restart_policy:
        condition: "on-failure"
    ports:
      - 5001:5000
    networks:
      - webnet
    volumes:
      - .:/app

  db:
    image: postgres:alpine
    ports:
      - 5432:5432
    environment:
      POSTGRES_DB: "cs162"
      POSTGRES_USER: "group1"
      POSTGRES_PASSWORD: "minervaMarketplace"
    networks:
      - webnet
    deploy:
      restart_policy:
        condition: "on-failure"

  adminer:
    image: adminer
    depends_on:
      - db
    deploy:
      restart_policy:
        condition: "on-failure"
    ports:
      - 8080:8080
    networks:
      - webnet
networks:
  webnet:
        """
        conn = psycopg2.connect(
            host=self.get_docker_host(),
            port=5432,
            database="cs162",
            user="group1",
            password="minervaMarketplace",
        )
        with engine.connect() as con:
                rs = con.execute("SELECT * FROM listing WHERE title = 'test listing'")
                self.assertEqual(rs.rowcount, 1)
        '''
        res = "(Decimal('2.0'),)"
        #assert res == str(rows[-1]) 
        if res == str(rows[-1]):
            return True
        else:
            raise Exception("Test failed")
        #raise an exception if the test fails
         
        #print(rows)
        '''
    '''
    def test_invalid_request(self):
        SERVER = "http://{}:5000".format(self.get_docker_host())
        r = requests.post(SERVER + '/listing', data=)
        assert r.status_code == 500
        if r.status_code == 500:
            return True
        else:
            raise Exception("Test failed")
    '''

    def test_lenght_db(self):
        listing_invalid_test_data = {
                    "title": "t",
                    "description": "test description",
                    "location": "Buenos Aires",
                    "price": "100",
                    "tags": "test, tags",
                    "state": "Available",
                    "listingType": "Buy",
                }
        SERVER = "http://{}:5000".format(self.get_docker_host())
        conn = psycopg2.connect(
            host=self.get_docker_host(),
            port=5432,
            database="cs162",
            user="cs162_user",
            password="cs162_password",
        )
        cur = conn.cursor()
        cur.execute("SELECT value FROM expression")
        rows = cur.fetchall()
        in1 = len(rows)
        r = requests.post(SERVER + '/listing', data= listing_invalid_test_data)
        post_listing = requests.post("http://127.0.0.1:5000/listing", data = listing_invalid_test_data)
        self.assertEqual(post_listing.status_code, 400)
    

    """
    Basic testing of the deletiion features before the docker integration

    class AuthManager():
    def __init__(self):
        pass
        
    def __enter__(self):
        r = requests.get("http://127.0.0.1:5000/automate_test_login")
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        r = requests.get("/logout")

class IntegrationTestApp(unittest.TestCase):
    
    def test_update_authorized_listing(self):
        with AuthManager():
            #create the listing
            listing_test_data = {
                "title": "test listing",
                "description": "test description",
                "location": "Buenos Aires",
                "price": "100",
                "tags": "test, tags",
                "state": "Available",
                "listingType": "Buy",
            }
            #post the listing to the database (the listing is a form)
            post_listing = requests.post("http://127.0.0.1:5000/listing", data = listing_test_data)
            #test if the listing is in the database
            with engine.connect() as con:
                rs = con.execute("SELECT * FROM listing WHERE title = 'test listing'")
                self.assertEqual(rs.rowcount, 1)
            #update the listing
            listing_test_data = {
                "title": "test listing",
                "description": "test description",
                "location": "Berlin",
                "price": "100",
                "tags": "test, tags",
                "state": "Available",
                "listingType": "Buy",
            }
            #update the listing in the database (the listing is a form)
            post_listing = requests.post("http://http://127.0.0.1:5000/listing/1", data = listing_test_data)
            #test if the listing is in the database
            with engine.connect() as con:
                rs = con.execute("SELECT * FROM listing WHERE location = 'Berlin'")
                self.assertEqual(rs.rowcount, 1)
            #test the if it's a valid request
            self.assertEqual(post_listing.status_code, 200)
            #delete the listing from the database
            with engine.connect() as con:
                rs = con.execute("DELETE FROM listing WHERE title = 'test listing'")
                self.assertEqual(rs.rowcount, 1)
            
                
    def test_update_unauthorized_listing(self):
        with AuthManager():
            pass
                
    def test_existing_listings_for_filter(self):
        with AuthManager():
            pass
    
    def test_empty_listings_for_filter(self):
        with AuthManager():
            pass

    def test_valid_listing(self):
        with AuthManager():
            listing_test_data = {
                    "title": "test listing",
                    "description": "test description",
                    "location": "Buenos Aires",
                    "price": "100",
                    "tags": "test, tags",
                    "state": "Available",
                    "listingType": "Buy",
                }
            #post the listing to the database (the listing is a form)
            post_listing = requests.post("http://127.0.0.1:5000/listing", data = listing_test_data)
            #test if the listing is in the database
            with engine.connect() as con:
                rs = con.execute("SELECT * FROM listing WHERE title = 'test listing'")
                self.assertEqual(rs.rowcount, 1)
            self.assertEqual(post_listing.status_code, 200)


    def test_invalid_listing(self):
        with AuthManager():
            #Minimun title is 6 characters, making it invalid by having 1 character
            listing_invalid_test_data = {
                    "title": "t",
                    "description": "test description",
                    "location": "Buenos Aires",
                    "price": "100",
                    "tags": "test, tags",
                    "state": "Available",
                    "listingType": "Buy",
                }
            #post the listing to the database (the listing is a form)
            post_listing = requests.post("http://127.0.0.1:5000/listing", data = listing_invalid_test_data)
            self.assertEqual(post_listing.status_code, 400)

    """


#run the test
if __name__ == "__main__":
    unittest.main()