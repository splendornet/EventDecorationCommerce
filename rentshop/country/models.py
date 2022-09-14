# python imports
from __future__ import unicode_literals

# django imports
from django.db import models


class Country(models.Model):

    """
    Model to store country master.
    """

    country_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.country_name


class State(models.Model):

    """
    Model to store state master.
    """

    state_name = models.CharField(max_length=200, unique=True)
    state_id = models.IntegerField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='country')

    def __str__(self):
        return self.state_name


class City(models.Model):

    """
    Model to store city master.
    """

    SHIPMENT_STATUS = (
        (1,'active'),
        (2,'inactive')
    )
    city_name = models.CharField(max_length=200, unique=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='state')
    shipment = models.IntegerField(choices=SHIPMENT_STATUS, default=1, verbose_name='shipment')

    def __str__(self):
        return self.city_name
