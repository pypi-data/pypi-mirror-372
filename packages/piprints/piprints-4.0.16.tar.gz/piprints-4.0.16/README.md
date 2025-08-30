# INSTALL

Create your new project:

```bash
poetry new myproject
cd myproject
poetry add piprints
poetry run manage
```

Initialize the database
```bash
poetry run manage migrate
poetry run manage collectstatic --no-input
```
(or test database connection with `poetry run manage dbshell`)

Create the first user
```bash
poetry run manage createsuperuser
```

Collect static files
```bash
poetry run manage collectstatic
```

Run the server
```bash
poetry run manage runserver
```
and then connect to localhost:8000/admin/ for the initial configuration. 
You should create a SiteParameter object. 
The `id` of this object must be given to the server configuration
throught the `SITE_ID` configuration variable.
The default value is `2`, hence if you have a diffent value check the `configuration` section below.

Once an admin has been created, anyone can make a request for an account (from the login page) and the admin can manage account requests.
You can then change a user's password with the command
```bash
    poetry run manage changepassword <username>
```

**Warning:** the default configuration is *not* suitable for production. You should carefully check your configuration (see section below) in particular for production you should have 
`DEBUG=False` a randomly choosen `SECRET_KEY` and possibly 
a solid database (`mysql` or `postgres` instead of `sqlite`). 

# CONFIGURATION

Configuration is loaded from environment variables.
For example, to set the `SITE_ID` you should issue this command
```bash
export SITE_ID=2
```
before running the server. This is not permanent. To make it permanent you can create a `.env` file (in the same directory as the `README.md` file) and insert there all variables definition:
```
echo "SITE_ID=2" >> .env
```
An example file listing all settings is provided in the file `.env.example`

You can check the values of settings with the command
```bash
poetry run manage diffsettings
```

# DEPLOY USING PIP

create a working directory on your server 

```bash
mkdir piprints
cd piprints
```

create a virtualenv and activate it:
```bash
python -m venv venv
. venv/bin/activate
```

install the latest version of piprints:
```
pip install piprints
```

You might need the following additional packages, depending 
on your configuration:
```
pip install mysqlclient # if you use mysql as database
pip install httplib2 # if you want to connect to arxiv
pip install oauth2client google-api-python-client # to use google calendar
```

Configure your `.env` file as described above

The `manage` command should be available in your shell (when the virtual environment is active):

```bash
manage
```

You can use `manage runserver` to run a debug server. Otherwise for production use you should adapt the `piprints/wsgi.py` script

# BUILD `pypi` PACKAGE

Remember to bump version in `pyproject.toml`.

```bash
poetry build
poetry publish
```

# MAKE `requirements.txt`

```bash
poetry self add poetry-plugin-export
poetry export --without-hashes --format requirements.txt --output requirements.txt 
```

# BACKUP

Per fare un dump del database il comando che sembra funzionare e' questo:

da un lato:

    python manage.py dumpdata --exclude=contenttypes --exclude=auth.Permission --exclude=admin -o mydump.json

dall'altro lato:
    
    python manage.py flush   ## cancella il database!!
    python manage.py loaddata mydump.json



