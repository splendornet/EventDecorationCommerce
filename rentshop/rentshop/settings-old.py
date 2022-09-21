"""
Django settings for rentshop project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from oscar.defaults import *
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '--d$*ve_79=k^2g3oz1_n)na@*9@p0v9skvxj$s5^@*nk0p3$e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition
from oscar import get_core_apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'widget_tweaks',
    'country',
    'FrontendSite',
    'serviceOrders',
    'django_select2',
    'mathfilters',
    'HeaderMenu',
    'captcha',
    'payu',
    'master_access',
]+ get_core_apps(
    [
        'CustomCatalogue.catalogue',
        'CustomCustomer.customer',
        'CustomDashboard.dashboard',
        'CustomPartner.partner',
        'CustomPromotion.promotions',
        'CustomBasket.basket',
        'CustomSearch.search',
        'CustomCheckout.checkout',
        'CustomOrder.order',
        'CustomOffer.offer',
        'CustomPayment.payment',
    ]
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'rentshop.urls'

from oscar import OSCAR_MAIN_TEMPLATE_DIR
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), OSCAR_MAIN_TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'rentshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


# DATABASES = {
#     'default':{
#         'ENGINE':'django.db.backends.postgresql_psycopg2',
#         'NAME':'takerentpay_db',
#         'USER':'takerentpay_root',
#         'PASSWORD':'redhat',
#         'HOST':'localhost',
#         'POST':'5432',
#         'ATOMATIC_REQUESTS':True,
#     }
# }


DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME':'takerentpe_dev_test',
        'USER':'postgres',
        'PASSWORD':'',
        'HOST':'localhost',
        'POST':'5432',
        'ATOMATIC_REQUESTS':True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'
TIME_ZONE =  'Asia/Kolkata'


USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = BASE_DIR + '/static/'
#STATICFILES_DIRS = ['static']
#STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
SITE_ID = 2

#Search backend
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# Oscar uses Haystack to abstract away from different search backends.
# Unfortunately, writing backend-agnostic code is nonetheless hard and Apache Solr is currently the only supported production-grade backend.
# Your Haystack config could look something like this:

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#         'URL': 'http://127.0.0.1:8983/solr',
#         'INCLUDE_SPELLING': True,
#     },
# }

OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled','Completed'),
    'Being processed': ('Processed', 'Cancelled','Completed'),
    'Cancelled': (),
    'Completed': (),
}


from oscar.defaults import *

# OSCAR_DASHBOARD_NAVIGATION += [
#     {
#         'label': ('Add/Update Sliders'),
#         'url_name': 'slider',
#         'icon': 'icon-pencil',
#         'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff,
#     },
# ]


OSCAR_DASHBOARD_NAVIGATION = [

    {
        'label': ('Dashboard'),
        'icon': 'icon-th-list',
        'url_name': 'dashboard:index',
    },
    {
        'label': ('Catalogue'),
        'icon': 'icon-sitemap',
        'children': [
            {
                'label': ('Products'),
                'url_name': 'dashboard:catalogue-product-list',
            },
            # {
            #     'label': ('Product Types'),
            #     'url_name': 'dashboard:catalogue-class-list',
            # },
            {
                'label': ('Categories'),
                'url_name': 'dashboard:catalogue-category-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            # {
            #     'label': ('Ranges'),
            #     'url_name': 'dashboard:range-list',
            # },
            {
                'label': ('Low stock alerts'),
                'url_name': 'dashboard:stock-alert-list',
            },
        ]
    },
    # {
    #     'label': ('Orders'),
    #     'url_name': 'dashboard:order-list',
    #     'icon': 'icon-ok',
    # },
    {
        'label': ('Orders'),
        'icon': 'icon-group',
        'children': [
            {
                'label': ('Orders'),
                'url_name': 'dashboard:order-list',
                #'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Service Order Enquiry'),
                'url_name': 'service-order-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
        ]
    },
    {
        'label': ('Vendors'),
        'url_name': 'dashboard:partner-list',
        'icon': 'icon-group',
        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
    },
    {
        'label': ('Customers'),
        'icon': 'icon-group',
        'children': [
            {
                'label': ('Customers'),
                'url_name': 'dashboard:users-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            # {
            #     'label': ('Stock alert requests'),
            #     'url_name': 'dashboard:user-alert-list',
            # },
        ]
    },
    {
        'label': ('Offers'),
        'icon': 'icon-bullhorn',
        'children': [
            # {
            #     'label': ('Offers'),
            #     'url_name': 'dashboard:offer-list',
            # },
            {
                'label': ('Coupon Seasons'),
                'url_name': 'dashboard:range-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

            },
            {
                'label': ('Coupons'),
                'url_name': 'dashboard:voucher-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },

            # {
            #     'label': ('Voucher Sets'),
            #     'url_name': 'dashboard:voucher-set-list',
            # },

        ],
    },
    # {
    #     'label': ('Content'),
    #     'icon': 'icon-folder-close',
    #     'children': [
    #         {
    #             'label': ('Content blocks'),
    #             'url_name': 'dashboard:promotion-list',
    #         },
    #         {
    #             'label': ('Content blocks by page'),
    #             'url_name': 'dashboard:promotion-list-by-page',
    #         },
    #         {
    #             'label': ('Pages'),
    #             'url_name': 'dashboard:page-list',
    #         },
    #         {
    #             'label': ('Email templates'),
    #             'url_name': 'dashboard:comms-list',
    #         },
    #         {
    #             'label': ('Reviews'),
    #             'url_name': 'dashboard:reviews-list',
    #         },
    #     ]
    # },
    {
        'label': ('Reports'),
        'icon': 'icon-bar-chart',
        'url_name': 'dashboard:reports-index',
    },
    {
         'label': ('Add/Update Sliders'),
         'url_name': 'slider',
         'icon': 'icon-pencil',
         'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
    },
    {
         'label': ('Change Password'),
         'url_name': 'Dashboard-PasswordChange',
         #'icon': 'icon-pencil',
    },


]


OSCAR_DEFAULT_CURRENCY = 'INR'

SLIDER_IMAGE_FOLDER = 'slider'
#SLIDER_DEFAULT_IMAGE = '/media/slider/slider_default.jpg'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.splendornet@gmail.com'
EMAIL_HOST_PASSWORD = 'splendornet123'
EMAIL_PORT = 587
FROM_EMAIL_ADDRESS = "test.splendornet@gmail.com"
SENT_FROM_EMAIL = "test.splendornet@gmail.com"


OSCAR_PRODUCTS_PER_PAGE = 4

LOGIN_REDIRECT_URL = '/'

STATICFILES_DIRS = ('static_custom', )



#PAYU_MERCHANT_KEY = "Sy9QK8HF",
#gtKFFx
#eCwWELxi
#PAYU_MERCHANT_SALT = "a2660SKcFu",


PAYU_MERCHANT_KEY = 'gtKFFx',
PAYU_MERCHANT_SALT = 'eCwWELxi'
PAYU_MODE = "TEST"
