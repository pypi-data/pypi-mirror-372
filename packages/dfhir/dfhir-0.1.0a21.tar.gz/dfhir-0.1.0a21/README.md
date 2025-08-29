# Dfhir (Django FHIR) API

Dfhir is a Django-based FHIR (Fast Healthcare Interoperability Resources) server designed to provide a robust and scalable solution for managing healthcare data.
It leverages Django's powerful ORM and REST framework to implement FHIR-compliant APIs. It currently implements FHIR v5.
This project is in its early stages and is not yet production-ready.

## Features

- **FHIR Resource Management**: Supports FHIR resources with Django models.
- **Django REST Framework Integration**: Provides RESTful APIs for FHIR resources.
- **PostgreSQL Support**: Uses `psycopg` for PostgreSQL database integration.


## Requirements

- Python 3.11 or higher
- Django 5.0 or higher
- PostgreSQL(support to make this DB agnostic will be added in the future)

## Installation

```bash
pip install dfhir
```


## Usage

Add dfhir to your Django project's `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    'dfhir.base',
    'dfhir.organization',
    ...
]
```

To use the views provided by dfhir, include the URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...,
    path('api', include("dfhir.organizations.urls")),
    path('api', include("dfhir.locations.urls")),
    ...
]
```
