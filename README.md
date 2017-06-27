# django-themagicapi
Django application. To launch an api server without endpoint.
Create the database on demand.

We can create multiple databases for different applications.
Just focusing on the client.

According to how we do the JSON query the server.
It will create, alter the table, insert,
list or delete data from an entire database automatically.

Requirements
------------
* Django 1.5+
* django-tokenapi
* valleorm
* django-cors-middleware

Installation
------------

First obtain `themagicapi` package and place it somewhere on your PYTHONPATH, for example
in your project directory (where settings.py is).

Alternatively, if you are
using some sort of virtual environment, like [virtualenv][], you can perform a
regular installation or use [pip][]:

    python setup.py install

    # or ...

    pip install django-themagicapi

[virtualenv]: http://pypi.python.org/pypi/virtualenv
[pip]: http://pip.openplans.org/

Add 'themagicapi', 'tokenapi' and 'corsheaders' to your `INSTALLED_APPS`.

###These are the modifications of settings.py file:
```python
#Add these lines
PATH_DBS = os.path.join(BASE_DIR, "dbs/")

MEDIA_ROOT = os.path.join(BASE_DIR, 'docfiles')
MEDIA_URL = '/docfiles/'

INSTALLED_APPS = [
    'themagicapi.apps.ThemagicapiConfig',
    'corsheaders',
    #......
]
MIDDLEWARE = [
 'corsheaders.middleware.CorsMiddleware'
 #......
]

AUTHENTICATION_BACKENDS = [
     'django.contrib.auth.backends.ModelBackend',
     'tokenapi.backends.TokenBackend'
     #.....
]

CORS_ORIGIN_ALLOW_ALL = True
```

Include `themagicapi.urls` and `tokenapi.urls` in your `urls.py`.
It will look something like this:

    urlpatterns = [
        url(r'^token/', include('tokenapi.urls')),
        url('', include('themagicapi.urls')),

    ]

Configuration and usage of token
--------------------------------

You can change the number of days that a token is valid for by setting
`TOKEN_TIMEOUT_DAYS` in `settings.py`. The default is `7`.
more information see [django-tokenapi]: https://github.com/jpulgarin/django-tokenapi.git

Usage
-----
### Create new table user if not exists and add new user.
          paramsRow = {
              'add':{
                  "db":"valleorm.db",
                  'user':{
                      "nombre": "Pepito",
                      "apellido": "Lopez",
                      }
                  }
          }

### Modify a user with know ID. Alter table automatically.

        paramsRow = {
            'add':{
                "db":"valleorm.db",
                'user':{
                    'ID': 1,
                    'apodo': 'donpepito',
                    'telf': '666666'
                    }
                }
          }

### Get all user

        paramsRow = {
            'get':{
                "db":"valleorm.db",
                'user':{
                    }
                }
          }

### Get by ID

        paramsRow = {
            'get':{
                "db":"valleorm.db",
                'user':{
                    'ID': 1,
                    }
                }
          }

### Remove row by ID
        paramsRow = {
            'rm':{
                "db":"valleorm.db",
                'user':{
                    'ID': 1,
                  }
                }
          }


for more requires see [themagic-apiserver]: https://github.com/vallemrv/themagic-apiserver.git
