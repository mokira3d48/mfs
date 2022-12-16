# Django Midnight File System
DjangoMidnight File System (MFS) is a Django application programmed to manage easily the server files
created and uploaded with the permissions and download authorizations.


## Installation et configuration

### Install python3 

```sh
sudo apt install python3;\
sudo apt install python3-pip
```

You have to make sure of the version of python that is installed. The version of python
used is `python 3.8.10`.


### Install venv
```sh
sudo apt install python3-venv
```

OR

```sh
sudo pip3 install virtualenv
```

### Create virtual environment

```sh
python3 -m venv env
```

OR

```sh
virtualenv env -p python3
```

### Lauch environment
```sh
source env/bin/activate
```

## Python version

```sh
python --version
```

Show :

```
Python 3.8.10
```

### Dependences installation
You must install the following dependences :

```sh
pip install django==3.2.6;\
pip install django-filter==21.1;\
pip install djangorestframework==3.13.1;\
pip install Markdown==3.3.6
```

## Integration
1. Copy `mfs` folder and past it into your root project.
2. Write the following code source in `settings.py` of your Django project.

```python
# MFS settings :
FSDIR = os.path.join(BASE_DIR, "fsdir");    # Definition of root directory of server files.
FSURL = "/file/";                           # Definition of global URL for file management.

```

3. In `urls.py` file, write the following code:

```python
# ...

from django.conf import settings
from django.conf.urls.static import static

# ...
# After urlpatterns definition ...

urlpatterns += static(settings.FSURL, document_root=settings.FSDIR);

```
