## exi

**exi** a [Flask](http://flask.pocoo.org/) project ....

*exi is extendable backbone for new Flask projects
and a set of useful helpers.

### The main idea of exi

...


## Installation

Create a virtualenv like:
```virtualenv <virtualenvs_dir>\exi''

Activate this virtualenv. For windows run activate.cmd

```git clone git://github.com/larryeitel/exi.git```
```cd exi```
```pip install -r requirements.pip```


## Run

There is some demo data for you. Create it.  
```./manage.py init_data```

Run development server, and go to http://127.0.0.1:5000  
```./manage.py runserver```

VERY early dev stage. Not much to see.

## Configuration

...

### testing.py

Simple basic TestCase for your tests. Note, that `nose` test runner is used (it's really good).

```
(exi)exi$ nosetests
```

### settings.py



The notation is `package.module.object` or `package.object` if object is in the `__init__.py`.
Look into the file for examples.


### wingide

If you use WingWare IDE (Highly recommended), here are some useful settings for debugging:

Project/Project Settings

    Environment
        Python Path (Added):
            <virtualenvs_dir>\exi\Lib\site-packages
            c:\Users\Larry\__prjs\exi
        Environment (Add to inherited environment)
        	PROJECT_SETTINGS=<projects_dir>\exi\exi\tests\local_settings.py
    Debug
        Main Debug File:
            <projects_dir>\exi\exi\app.py
        Initial Directory:
            <projects_dir>\exi\exi

