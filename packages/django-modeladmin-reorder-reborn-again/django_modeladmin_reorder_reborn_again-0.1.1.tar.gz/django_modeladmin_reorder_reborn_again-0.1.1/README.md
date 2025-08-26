# django-modeladmin-reorder-reborn-again

Reviving the old Django `django-modeladmin-reorder` package.

Detaches model groups from the apps, granting the flexibility to organize models
into various groups, change models and groups order.
Custom names can be assigned to groups.

## Implemented origin features

* Reorder apps in admin index - this will allow you to position most used apps in top of the page, instead of listing apps alphabetically. e.g. sites app before the auth app
* Rename app labels easily for third party apps without having to modify the source code. e.g. rename auth app to Authorisation for the django admin app.
* Split large apps into smaller groups of models.
* Reorder models within an group. e.g. auth.User model before the auth.Group model.
* Exclude any of the models from the app list. e.g. Exclude auth.Group from the app list. Please note this only excludes the model from the app list and it doesn't protect it from access via url.
* Cross link models from multiple apps. e.g. Add sites.Site model to the auth app.
* Rename individual models in the app list. e.g. rename auth.User from User to Staff

## New features

* Gathering models of the app that haven't been included in other groups.
* Create virtual app groups with models from multiple apps.

## Requirements

1. Python >= 3.5
2. Django >= 4.1

## Install

Install django-modeladmin-reorder-reborn-again:

`pip install django-modeladmin-reorder-reborn-again`

## Configuration

1. Create `admin_apps.py` file in your project folder:

```python
from django.contrib.admin.apps import AdminConfig

class MyAdminConfig(AdminConfig):
    default_site = "admin_reorder.ReorderingAdminSite"
```

2. Replace `django.contrib.admin` to `project.admin_apps.MyAdminConfig`
in your settings.py:

```python
INSTALLED_APPS = (
    ...
    '̶d̶j̶a̶n̶g̶o̶.̶c̶o̶n̶t̶r̶i̶b̶.̶a̶d̶m̶i̶n',
    'your_project_name.admin_apps.MyAdminConfig',
    ...
)
```

Add the setting ADMIN_REORDER to your settings.py:

```python
ADMIN_REORDER = [
    # Keep original label and models, but change group order
    {'app': 'sites'},

    # Rename app
    {'app': 'auth', 'label': 'Authorisation'},

    # Reorder app models
    {'app': 'auth', 'models': ('User', 'Group')},

    # Exclude models
    {'app': 'auth', 'models': ('User', )},

    # Cross-linked models from multiple apps
    {'app': 'auth', 'models': ('auth.User', 'sites.Site')},

    # Models with custom names
    {'app': 'auth', 'models': (
        'Group',
        {'model': 'auth.User', 'label': 'Staff'},
    )},

    # Create virtual app groups with models from multiple apps
    {'app': 'user_management', 'label': 'User Management', 'models': (
        'auth.User',
        'auth.Group',
        'sites.Site',
    )},

    # Gather not included in any group models
    {'app': 'auth', 'models': '__rest__'},
]
```
