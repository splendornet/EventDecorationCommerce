import os
from oscar.defaults import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '--d$*ve_79=k^2g3oz1_n)na@*9@p0v9skvxj$s5^@*nk0p3$e'

DEBUG = True

ALLOWED_HOSTS = ['*']

from oscar import get_core_apps
from oscar import OSCAR_MAIN_TEMPLATE_DIR

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'widget_tweaks',
    'country',
    'FrontendSite',
    'multiselectfield',
    'serviceOrders',
    'django_select2',
    'mathfilters',
    'HeaderMenu',
    'captcha',
    'payu',
    'RentCore',
    'embed_video',
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
    # 'CustomBasket.basket.middleware.CustomBasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',

]

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'rentshop.urls'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'takerentpe_dev_test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'POST': '5432',
        'ATOMATIC_REQUESTS': True,
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    }
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

# USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = BASE_DIR + '/static/'

SITE_ID = 2

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}


OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Initiated': ('Initiated', 'Cancelled','Completed'),
    'Pending': ('Being processed', 'Cancelled','Completed'),
    'Being processed': ('Processed', 'Cancelled','Completed'),
    'Cancelled': (),
    'Completed': (),
}

from oscar.defaults import *

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
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff,
            },
            {
                'label': ('Product Rate Card'),
                'url_name': 'dashboard:rate-card-products',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Categories'),
                'url_name': 'dashboard:catalogue-category-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Premium Product'),
                'url_name': 'dashboard:premium-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            # {
            #     'label': ('Combo Offer'),
            #     'url_name': 'dashboard:combo-index',
            #     'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff,
            # },

            {
                'label': ('Units'),
                'url_name': 'dashboard:product_unit',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Low stock alerts'),
                'url_name': 'dashboard:stock-alert-list',
            },
            {
                'label': ('Reviews'),
                'url_name': 'dashboard:reviews-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Taxation'),
                'url_name': 'dashboard:taxation-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Advanced Payment Percentage'),
                'url_name': 'dashboard:adv-percentage-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Product Attributes'),
                'url_name': 'dashboard:attribute-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Categories Filter'),
                'url_name': 'dashboard:category-filter-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Price Range Filter'),
                'url_name': 'dashboard:category-filter-price-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },

        ]
    },
    {
        'label': ('Orders'),
        'icon': 'icon-group',
        'children': [
            {
                'label': ('Orders'),
                'url_name': 'dashboard:order-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff,

            },
            {
                'label': ('Service Order Enquiry'),
                'url_name': 'service-order-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
        ]
    },
    {
        'label': ('ASP'),
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
        ]
    },
    {
        'label': ('Coupon'),
        'icon': 'icon-bullhorn',
        'children': [
            {
                'label': ('Primary Coupons'),
                'url_name': 'dashboard:voucher-list1',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Customize Coupon'),
                'url_name': 'dashboard:customize-voucher-list1',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Price Range Database'),
                'url_name': 'dashboard:price-range-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
        ],
    },
    {
        'label': ('Calendar'),
        'icon': 'icon-calendar',
        'children': [
            {
                'label': ('Calendar'),
                'url_name': 'dashboard:vendor-calender',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff,

            },
            {
                'label': ('My events'),
                'url_name': 'dashboard:vendor-calender-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff and not user.is_superuser,

            },
            {
                'label': ('Add event'),
                'url_name': 'dashboard:vendor-calender-add',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff and not user.is_superuser,
            },
            {
                'label': ('Events List'),
                'url_name': 'dashboard:vendor-calender-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

            },
            {
                'label': ('Add event'),
                'url_name': 'dashboard:create-event-admin',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
        ],
    },
    {
        'label': ('Reports'),
        'icon': 'icon-bar-chart',
        'url_name': 'dashboard:reports-index',
        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
    },
    {
         'label': ('Add/Update Sliders'),
         'icon': 'icon-pencil',

         'children': [
            {
                'label': ('Add/Update Sliders'),
                'url_name': 'slider',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

            },
            {
                'label': ('Featured Products'),
                'url_name': 'dashboard:featured-product-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
        ]
    },
    {
         'label': ('Sales'),
        'icon': 'icon-pencil',
        'children': [
                    {
                        'label': ('Daily Updates'),
                        'url_name': 'dashboard:sales-index',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('Prime Bucket'),
                        'url_name': 'dashboard:prime-bucket',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('ASP Database'),
                        'url_name': 'dashboard:asp-db',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('Order Allotement'),
                        'url_name': 'dashboard:best_quote',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('Re-Allocate Order'),
                        'url_name': 'dashboard:re-allocate-order',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('Cancelled Order'),
                        'url_name': 'dashboard:cancel-order-index',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('Cancellation Charges'),
                        'url_name': 'dashboard:cancellation_index',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('Offer Prime Bucket (OPB)'),
                        'url_name': 'dashboard:offers-prime-bucket',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('OPB Allotment and Re-Allotment'),
                        'url_name': 'dashboard:offers-order-reallocate',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                    {
                        'label': ('Coupon Distributors'),
                        'url_name': 'dashboard:coupon-distributors',
                        'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,

                    },
                ],

    },
    {
         'label': ('Accounts'),
        'icon': 'icon-money',
        'children': [
            {
                'label': ('Net Profit'),
                'url_name': 'dashboard:accounts-net-profit',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Product Margin'),
                'url_name': 'dashboard:accounts-product-margin',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Set Product Margin'),
                'url_name': 'dashboard:accounts-set-margin',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Front Pages'),
                'url_name': 'dashboard:accounts-legal-page',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
        ]
    },
    {
         'label': ('Transportation'),
        'icon': 'icon-pencil',
        # 'url_name': 'Dashboard-PasswordChange',
    },
    {
         'label': ('Billing'),
        'icon': 'icon-pencil',
        # 'url_name': 'Dashboard-PasswordChange',
    },
    {
         'label': ('Customer Support'),
        'icon': 'icon-user',
        # 'url_name': 'Dashboard-PasswordChange',
    },
    {
         'label': (' Account'),
        'icon': 'icon-book',
        # 'url_name': 'Dashboard-PasswordChange',
    },
    {
        'label': (' Manage Menu'),
        'icon': 'icon-book',
        'children': [
            {
                'label': ('Corporate Offers'),
                'url_name': 'dashboard:manage-menu-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Exhibition Offers'),
                'url_name': 'dashboard:exhibition-offers-index',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
            {
                'label': ('Add/Upload My Offer Images '),
                'url_name': 'dashboard:upload-my-offer-images',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_superuser,
            },
        ]
    },

    {
         'label': ('Change Password'),
         'url_name': 'Dashboard-PasswordChange',
    },
]


OSCAR_DEFAULT_CURRENCY = 'INR'

SLIDER_IMAGE_FOLDER = 'slider'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtpout.secureserver.net'
# EMAIL_HOST_USER = 'test.splendornet@gmail.com'
# EMAIL_HOST_PASSWORD = 'splendornet123'
EMAIL_HOST_USER = 'info@takerentpe.com'
EMAIL_HOST_PASSWORD = 'Respect13Marshall$'
EMAIL_PORT = 587
FROM_EMAIL_ADDRESS = "info@takerentpe.com"
SENT_FROM_EMAIL = "info@takerentpe.com"

OSCAR_PRODUCTS_PER_PAGE = 30

LOGIN_REDIRECT_URL = '/'

STATICFILES_DIRS = ('static_custom', )

PAYU_MERCHANT_KEY = 'gtKFFx',
PAYU_MERCHANT_SALT = 'eCwWELxi'
PAYU_MODE = "TEST"

ERROR_MESSAGE = 'Something went wrong.'

CONTACT_ADMIN_EMAIL = ['rmtest08@gmail.com', 'p.mohadikar@splendornet.com']

FOOTER_TERM = 'Copyright © 2018-2019 Take Rent Pe, All rights reserved'

SITE_URL = 'http://takerentpe-dev.progfeel.co.in'

# CC AVE
CC_URL = ' https://test.ccavenue.com'
CC_MERCHANT_ID = '198605'
CC_ACCESS_CODE = 'AVYF81FK72BH23FYHB'
CC_WORKING_KEY = 'D354E70142D2966BD4D7D006D13568E3'
CC_CURRENCY = 'INR'
CC_LANG = 'EN'
CC_BILL_CONTRY = 'India'
API_CC_WORKING_KEY = 'BB3C8C631791BA17C67EA0863AB72581'
API_CC_ACCESS_CODE = 'AVYF81FK72BH23FYHB'

SUPPORT_NUMBER = '+91-7378989996'
SUPPORT_NUMBER_TEL = '07378989996'

SUPPORT_EMAIL = 'admin@takerentpe.com'

TRP_FB_LINK = 'https://www.facebook.com/'
TRP_GPLUS_LINK = 'http://gmail.com/'
TRP_LINKIN_LINK = 'https://www.linkedin.com/'
TRP_TWITTER_LINK = 'https://twitter.com/'

TRP_FB_LINK1 = 'https://www.facebook.com/Take-Rent-Pe-101019151839514'
TRP_TWITTER_LINK1 = 'https://twitter.com/take_rent_pe'
TRP_YOUTUBE_LINK1 = 'https://www.youtube.com/channel/UCW7mHue2nbWxqE7xCAKi2VQ'
TRP_INSTA_LINK1 = 'https://www.instagram.com/takerentpe/'


USER_AFTER_REGISTER = 'Thank you for registering with us. Account activation link has been sent to your email.'

LOGO_URL = 'oscar/site_logo/icons/logo500.png'
OSCAR_MODERATE_REVIEWS = True

FILE_UPLOAD_PERMISSIONS = 0o644

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'amqp'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

EMAIL_LOGO_URL = 'http://takerentpe-dev.progfeel.co.in/media/logo500.png'
EMAIL_FOOTER_LOGO_URL = 'http://takerentpe-dev.progfeel.co.in/media/TakeRentPe_Logo_Black_Email.png'

CONGRATULATION_IMG = 'http://takerentpe-dev.progfeel.co.in/media/images/email_images/congratulations.png'
SIGNATURE_IMG = 'http://takerentpe-dev.progfeel.co.in/media/images/email_images/signature.png'




SMS_USER = 'takerentpe'
SMS_PASS = 'takerentpe'

