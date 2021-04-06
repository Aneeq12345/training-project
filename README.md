# training-project

# Installation
Install python and postgresql.


Install these  packages.

```bash
pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install psycopg2
```
# Databse
In setting.py configure Database

```python
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

```