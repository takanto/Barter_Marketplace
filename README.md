# Welcome to CS162 Final Project

![template ci](https://github.com/minerva-schools/template-cs162/actions/workflows/ci.yaml/badge.svg)

## Run Virtual Environment

Virtual environment is a key component in ensuring that the application is configured in the right environment

##### Requirements
* Python 3
* Pip 3

```bash
$ brew install python3
```

Pip3 is installed with Python3

##### Installation
To install virtualenv via pip run:
```bash
$ pip3 install virtualenv
```

##### Usage
Creation of virtualenv:

    $ virtualenv -p python3 venv

If the above code does not work, you could also do

    $ python3 -m venv venv

To activate the virtualenv:

    $ source venv/bin/activate

Or, if you are **using Windows** - [reference source:](https://stackoverflow.com/questions/8921188/issue-with-virtualenv-cannot-activate)

    $ venv\Scripts\activate

To deactivate the virtualenv (after you finished working):

    $ deactivate

Install dependencies in virtual environment:

    $ pip3 install -r requirements.txt

## Environment Variables

All environment variables are stored within the `.env` file and loaded with dotenv package.

**Never** commit your local settings to the Github repository!

## Run Application

Start the server by running:

    $ export OAUTHLIB_INSECURE_TRANSPORT=1  
    $ python3 app.py

## Run Application with Dockerfile

    $ docker build -t cs162-barter-marketplace:latest .
    $ docker swarm init
    $ docker stack deploy -c docker-compose.yml cs162-swarm
    
    To check the status of containers,
    
    $ docker ps

    For removing everything,
    
    $ docker stack rm cs162-swarm

## Unit Tests
To run the unit tests use the following commands:

    $ python3 -m venv venv_unit
    $ source venv_unit/bin/activate
    $ pip install -r requirements-unit.txt
    $ python3 unit_test/test_app.py

## Integration Tests
Start by running the web server in a separate terminal.

Now run the integration tests using the following commands:

    $ python3 -m venv venv_integration
    $ source venv_integration/bin/activate
    $ pip3 install -r requirements-integration.txt
    $ python3 unit_test/test_app.py

## Deployment
We will use Heroku as a tool to deploy your project, and it is FREE

We added Procfile to help you deploy your repo easier, 
but you may need to follow these steps to successfully deploy the project

1. You need to have admin permission to be able to add and deploy your repo to Heroku 
(Please ask your professor for permission)
2. You need to create a database for your website. 
We recommend you use [Heroku Postgres](https://dev.to/prisma/how-to-setup-a-free-postgresql-database-on-heroku-1dc1)
3. You may need to add environment variables to deploy successfully - [Resource](https://devcenter.heroku.com/articles/config-vars#using-the-heroku-dashboard)
