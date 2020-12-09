# API

## Tests

![Docker Image CI](https://github.com/split2021/API/workflows/Docker%20Image%20CI/badge.svg?branch=release)

## Documentation

The API endpoints documentation can be found [here](https://documenter.getpostman.com/view/6975668/S1EUtFTJ?version=latest)
The developper documentation of django_modelapiview (which is the core of our API) is available on [pypi](https://pypi.org/project/django-modelapiview/) or on its [repository](https://github.com/TiphaineLAURENT/Django_APIView)

HTTP Status Codes matches [these ones](https://www.restapitutorial.com/httpstatuscodes.html)

We are using the [Payal-Python-SDK V1](https://github.com/paypal/PayPal-Python-SDK/tree/0d704e7d3bb0c9c77db1edc34801709e43440710)

## Startup

*The docker-compose.yml file provided is only working for a*
*development environment.*

Use `docker-compose up` to start the container
and `docker-compose down` to stop it

## Application files description

**Note**:
- **Display rules**:

  - Empty / not used files are not listed below


- **Common directories and files**:

  - \_\_pycache__/ directories are python files compiled
  - \_\_init__.py files are python module files
  - admin.py files are application interaction with the backoffice description
  - apps.py files are Django required for applications detection
  - forms files are forms class based description
  - models files describe the database using the Django ORM
  - tests.py files are unitary tests



```
api                                       # Project directory
└───api                                   # API application
│   └───migrations                        # List the migrations needed to update the db
|       |   ...
|   |
│   │   admin.py                          # API interaction on the backoffice
│   │   apps.py
│   │   classviews.py                     # Base classes for API endpoints
│   │   models.py                         # API database classes described
│   │   responses.py                      # Base classes for API responses
│   │   tests.py
│   │   urls.py                           # API endpoints description
│   │   views.py                          # API endpoints logic
|
└───eip                                   # EIP application
│   └───migrations
|       |   ...
|   |
|   |   admin.py                          # EIP interaction on the backoffice
|   |   apps.py
|   |   models.py                         # EIP database classes described
|   |   tests.py
|
└───split                                 # Project application
│   └───templates
|       └───admin                         # Django backoffice override
|           |   base_site.html            # Base template override
|       |
|       └───split                         # Additional templates
|           |   user_update_profile.html  # User update template
|   |   
|   |   admin.py                          # Backoffice configuration
|   |   apps.py
|   |   forms.py
|   |   settings.py
|   |   urls.py
|   |   views.py                          # Additional backoffice views
|   |   wsgi.py
|
└───static                                # Django collected static files for production
│   └───admin
|       └───css
|       └───fonts
|       └───img
|       └───js
|
|   Dockerfile                            # Docker API container configuration
|   manage.py                             # Django commands entry point
|   README.md                             # This description file
|   requirements.txt                      # Project modules required list for pip -r
│
```
