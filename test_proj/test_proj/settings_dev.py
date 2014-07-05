from .settings import *

BASE_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'parallel_tests',
)

CUSTOM_APPS = (
    'app1',
    'app2',
)

INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

TEST_APPS = ["app1", "app2"]
PROJECT_NAME = "test_proj_dev"
REQUIREMENTS = "requirements.txt"
