# Django Midnight File System
Django Midnight File System (MFS) is a Django application programmed to manage easily the server files
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

4. Execute the following django commands to make migration of the database File model :

```sh
./manage.py makemigrations;\
./manage.py migrate
```

All is done !

## Usage
We will see some examples of use cases in a Django project. Given an application named `galery`.

1. Example 1:
You can create model of image file in `galery` like following code :

```python
from django.utils.translation import gettext_lazy as _
from django.db  import models
from mfs.models import File


class Image(File):
    """
    Image file database model definition 
    """
    DEFAULT_DIR_NAME = "Pictures";      # define the root folder name of our images
    DEFAULT_FILE_EXT = "png";           # define the global extension
    
    class Meta:
        verbose_name = _("CSR file");

    def __str__(self):
        """
        Function to return a representation of this model in string.
        """
        return self.name;   # this attribut is already defined on File superclass


```

