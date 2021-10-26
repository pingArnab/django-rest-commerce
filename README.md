<section align="center">
    <div align="center">
        <h1>django rest commerce</h1>
        <div align="center">
            <img src="https://img.shields.io/badge/Version-0.9.0-fe7d37?style=for-the-badge&logo=Git&logoColor=ffffff" alt="Version - 0.9.0"> 
        </div>
    </div>
</section>

<br>

<div align="center">
    django-rest-commerce is a framework for building scalable API based e-commerce web application backend that offers all the features an e-commerce application might need with an easy to understand codebase to extend upon
</div>

<br>
<br>

### Installation

1. Clone the project into a suitable directory and create a virtual environment at the project root

2. Install required dependencies in the environment by running `pip install -r requirements.txt`

3. Change the config variables according to your need in the file `config.yaml`

4. Put the necessary environment variables in place. For more information, check env-reference below

5. Create the database by consecutively running `python manage.py makemigrations` and `python manage.py migrate`

6. Create a superuser accordingly by running `python manage.py createsuperuser`

<br>
<br>

### Usage

1. Spin up the Python development server by running `python manage.py runserver`

2. You are good to go for testing the built-in APIs. For more information, visit the API detailed <a href="http://bit.ly/drc-api">documentation</a>

<br>
<br>

### Environment Reference

Make sure that the environment you are running the application in contains the environment variables as listed below.

```text
DOMAIN_NAME=test.com

SERVER_ENV_TYPE=TEST
DJANGO_DEBUG_MODE=TRUE

DB_USERNAME=postgres
DB_PASSWORD=4520
MAIL_USERNAME=no-reply@test.com
MAIL_PASSWORD="'{L%;XSd7sqq,M9g"
```

<br>

<section align="center">
    <h3><a href="http://bit.ly/drc-api">API Documentation</a></h3>
</section>

<br>
<br>

<div align="center">
    Copyright (c) 2021 Poltergeist
</div>

<br>
<br>