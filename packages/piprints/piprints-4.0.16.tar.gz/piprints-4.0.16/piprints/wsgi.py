import os
import sys
from dotenv import load_dotenv

os.environ['DJANGO_SETTINGS_MODULE'] = 'piprints.settings'

# load your configuration
load_dotenv(dotenv_path="path to .env configuration file")

# uncomment the following line if "piprints" is not in the Python path
# sys.path.append("path to piprints source directory")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
