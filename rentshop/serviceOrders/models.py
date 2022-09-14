from django.conf import settings
from django.db import models, router
from django.utils.translation import ugettext_lazy as _


class ServiceOrders(models.Model):

    product = models.ForeignKey('catalogue.Product', on_delete=models.CASCADE, verbose_name=_("Product"))
    name = models.CharField(max_length=200, verbose_name='Name')
    email = models.EmailField(blank=True, verbose_name='Email')
    mobile = models.CharField(max_length=10, blank=True, verbose_name='Mobile Number')
    added_date = models.DateTimeField(auto_now_add=True)

    booking_date = models.DateTimeField(blank=True, null=True)
    booking_start_date = models.DateTimeField(blank=True, null=True)
    booking_end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service Orders'
        verbose_name_plural = 'All Service Orders'
