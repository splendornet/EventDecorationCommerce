# django imports
from django.db import models
from django.contrib.flatpages.models import FlatPage

# packages import
from oscar.core.compat import AUTH_USER_MODEL


class SiteMessage(models.Model):

    """
    Model to store messages
    """

    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    user_welcome_message = models.CharField(max_length=255, blank=True, null=True)
    vendor_welcome_message = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Site messages'


class CustomFlatPages(FlatPage):

    PAGE_TYPE_CHOICES = (
        ('0', 'Legal Documents'),
        ('1', 'Policies'),
        ('2', 'Terms and Conditions'),
        ('3', 'FAQ'),
        ('4', 'About Us'),
        ('5', 'How It Works'),

    )
    page_type = models.CharField(max_length=200, blank=True, null=True, choices=PAGE_TYPE_CHOICES )

    def __str__(self):
        return self.content


class AbandonedCartLogs(models.Model):

    """
    Model to store cart logs
    """

    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ab_cart_users', blank=True, null=True)

    cart = models.ForeignKey('basket.Basket', on_delete=models.CASCADE, related_name='ab_cart', blank=True, null=True)
    wishlist = models.ForeignKey('wishlists.WishList', on_delete=models.CASCADE, related_name='ab_wish_list', blank=True, null=True)
