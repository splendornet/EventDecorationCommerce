from django.db import models
from django.contrib.auth.models import User


class PaymentDetails(models.Model):

    txid = models.CharField(max_length=512, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


from oscar.apps.checkout.models import *  # noqa isort:skip
