# django imports
from django.db import models
from oscar.core.loading import get_class, get_model

from multiselectfield import MultiSelectField

from django.contrib.auth.models import User
Partner = get_model('partner', 'Partner')
Product = get_model('catalogue', 'Product')
Basket = get_model('basket', 'Basket')



class CustomProfile(models.Model):

    """
    Model to store user profile
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_user')
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    is_first_login = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.mobile_number


class ContactUs(models.Model):

    """
    Model to store contact us query
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):

        return self.name


class Notes(models.Model):
    """
        Model to store Notes
        """

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='created_user')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='updated_user')

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    note = models.TextField(blank=True, null=True)
    alert = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)


class Enquiry(models.Model):
    """
    Model to store enquiry data
    """

    RENTAL_DURATION_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
    )

    EVENT_CHOICE = (
        ('1', 'Annual'),
        ('2', 'Festival'),
        ('3', 'Concert'),
        ('4', 'Exhibition'),
        ('5', 'Fashion Show'),
        ('6', 'Customized Wedding'),
        ('7', 'Customized Birthday'),
        ('8', 'Other'),
    )

    organization_name = models.CharField(max_length=100, blank=True, null=True)
    person_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone_number = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    enquiry_text = models.TextField(max_length = 250, blank = True,null = True)
    event_date = models.DateTimeField(auto_now_add=True)
    rental_duration = models.PositiveIntegerField(choices=RENTAL_DURATION_CHOICES, default=1)
    
    budget_from = models.PositiveIntegerField()
    budget_to = models.PositiveIntegerField()
    allocated_vendor = models.ManyToManyField(Partner, blank=True, null=True)
    event_type = MultiSelectField(choices = EVENT_CHOICE)

    basket_instance = models.ForeignKey(Basket, on_delete=models.SET_NULL, blank=True, null=True, related_name='enquiry_basket')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='created_enquiry')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='updated_enquiry')
    enquiry_date = models.DateTimeField(blank = True,null = True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def get_allocated_vendor(self):
        ret = ''
        if self.allocated_vendor.all():
            for allocate_vendor in self.allocated_vendor.all():
                ret = ret + allocate_vendor.name + ','
            return ret[:-1]

        return 0

    def get_order_number(self):

        try:

            if self.basket_instance:
                return 100000 + self.basket_instance.id

            return '-'

        except:

            return '-'


class OTPModel(models.Model):

    """
    Model to store otp
    """

    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_update = models.DateTimeField(auto_now=True, null=True, blank=True)

    mobile_number = models.CharField(max_length=100)
    otp = models.CharField(max_length=100)
    sms_response = models.TextField(blank=True, null=True)
    otp_attempt_count = models.IntegerField(null=True, blank=True, default = 0)
    otp_sent_count = models.IntegerField(null=True, blank=True)


    def __str__(self):

        return self.mobile_number


from oscar.apps.customer.models import *  # noqa isort:skip
