# -*- coding: utf-8 -*-
"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p1p2e^77+6ex*1@-s6hzcx7l3bx#g2q0w1za1c-x-1p@n6z^x*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost ', '67.209.178.147', '192.168.1.102', ]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'django.contrib.sites',
    'blog',
    'swint',
    'freezingsimulation',
    'vmaig_auth',
    'vmaig_comments',
    'vmaig_system',
    'gunicorn',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'vmaig_blog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates/")],
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

WSGI_APPLICATION = 'vmaig_blog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

# LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 设置user model
AUTH_USER_MODEL = "vmaig_auth.VmaigUser"


# log配置
LOG_FILE = "./all.log"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(module)s : %(message)s'
        },
        'verbose': {
            'format':
            '[%(asctime)s] [%(levelname)s] %(module)s : %(message)s'
        }
    },

        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'django.utils.log.AdminEmailHandler',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'formatter': 'verbose',
                'filename': LOG_FILE,
                'mode': 'a',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'filters': ['require_debug_false']
            }
        },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# cache配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'options': {
            'MAX_ENTRIES': 1024,
        }
    },
    'memcache': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # 'LOCATION': 'unix:/home/billvsme/memcached.sock',
        'LOCATION': '127.0.0.1:11211',
        'options': {
            'MAX_ENTRIES': 1024,
        }
    },
}


# 分页配置
PAGE_NUM = 2

# email配置
# 如果想要支持ssl (比如qq邮箱) 见 https://github.com/bancek/django-smtp-ssl
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = ''                       # SMTP地址 例如: smtp.163.com
# EMAIL_PORT = 25                       # SMTP端口 例如: 25
# EMAIL_HOST_USER = ''                  # 我自己的邮箱 例如: xxxxxx@163.com
# EMAIL_HOST_PASSWORD = ''              # 我的邮箱密码 例如  xxxxxxxxx
# EMAIL_SUBJECT_PREFIX = u'vmaig'       # 为邮件Subject-line前缀,默认是'[django]'
EMAIL_USE_TLS = True                  # 与SMTP服务器通信时，是否启动TLS链接(安全链接)。默认是false

# SMTP地址
EMAIL_HOST = 'smtp-mail.outlook.com'
# SMTP端口
EMAIL_PORT = 587
# 邮箱地址
EMAIL_HOST_USER = 'wguiqiang@hotmail.com'
# 密码
EMAIL_HOST_PASSWORD = 'hitswint'
# ACCOUNT_EMAIL_VERIFICATION = 'none'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# 七牛配置
QINIU_ACCESS_KEY = ''
QINIU_SECRET_KEY = ''
QINIU_BUCKET_NAME = ''
QINIU_URL = ''

# 网站标题等内容配置
WEBSITE_TITLE = u'Swint\'s blog'
WEBSITE_WELCOME = u'欢迎来到Vmaig'
