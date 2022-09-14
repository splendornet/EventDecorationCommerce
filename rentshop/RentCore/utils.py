# python imports

# django imports
from django.conf import settings

# 3rd party imports
from oscar.core.loading import get_class, get_model

# catalogue
Product = get_model('catalogue', 'Product')

# core
SiteMessage = get_model('RentCore', 'SiteMessage')


class CatalogueQuery:

    """
    Class to return catalogue app models queryset's.
    """

    def product_set(self, *args, **kwargs):

        """
        Method to return product set.
        """

        # return Product.objects.all()
        return Product.objects.filter(is_deleted = False)


class SiteMessages:

    """
    Class to display site messages.
    """

    def default_message(self, message_type):

        """
        Method to return default message from settings.
        """

        if message_type == 'customer_after_register':
            try:
                return settings.USER_AFTER_REGISTER
            except:
                return 'Thank you for registering with us. Account activation link has been sent to your email.'

    def customer_messages(self, *args, **kwargs):

        """
        Method to return customer messages.
        """

        if not SiteMessage.objects.all():
            return self.default_message(message_type='customer_after_register')

        site_obj = SiteMessage.objects.all().last()

        if kwargs.get('message_type') == 'customer_after_register':

            if not site_obj.user_welcome_message:
                return self.default_message(message_type='customer_after_register')
            return site_obj.user_welcome_message
