# Copyright (C) 2017 Linaro Limited
#
# Author: Milosz Wasilewski <milosz.wasilewski@linaro.org>
#
# This file is part of KernelCI-monitor.
#
# KernelCI-monitor is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# KernelCI-monitor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with KernelCI-monitor. If not, see <http://www.gnu.org/licenses/>.

"""
Django settings for kernelcimonitor project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1&_znemf9(5(jyef!7=e(h=m4v^h5o2y6&3xjmcyhumo1hh1)_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'monitor.apps.MonitorConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kernelcimonitor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kernelcimonitor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'db.sqlite3')),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Celery settings
BROKER_URL = 'amqp://kernelci:kernelci@localhost:5672//kernelci'

CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTENT = False
CELERY_ACCEPT_CONTENT = ['json', 'pickle']
CELERYBEAT_SCHEDULE_FILENAME = "/tmp/kernelcimonitor-celery-beat"
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
CELERYD_TASK_LOG_FORMAT = '[%(asctime)s] %(levelname)s %(task_name)s: %(message)s'
CELERY_TIMEZONE = 'UTC'
CELERY_IMPORTS = ("monitor.tasks", )

KERNELCI_TOKEN="super-secret-token"
KERNELCI_URL="https://kernelci.org/"
KERNELCI_API_URL="https://api.kernelci.org/%s/"
KERNELCI_STORAGE_URL="https://storage.kernelci.org/"
KERNELCI_DATE_RANGE=1

LAVA_XMLRPC_URL="https://staging.validation.linaro.org/RPC2/"
LAVA_USERNAME="lava-user"
LAVA_PASSWORD="lava-password"

SQUADLISTENER_TOKEN="super-secret-token"
SQUADLISTENER_API_URL="http://localhost:8001"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
