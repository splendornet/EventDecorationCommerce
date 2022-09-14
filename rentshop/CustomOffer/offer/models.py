# Django Imports
from django.db import models

# module imports
from oscar.apps.offer.abstract_models import AbstractBenefit, AbstractConditionalOffer,AbstractRange
from oscar.core.loading import get_class, get_classes, get_model
from django.utils.translation import ugettext_lazy as _

Category = get_model('catalogue', 'Category')
Voucher = get_model('voucher', 'Voucher')

DISCOUNT_TYPE = (
    ("Percentage", "Discount is a percentage off of the product's value"),
    ("Absolute", "Discount is a fixed amount off of the product's value"),
)

PRICE_RANGE_TUPLE = (
    # ('1-2000', 'Below 2,000'),
    # ('2000-5000', '2,000 - 5,000'),
    # ('5000-7000', '5,000 - 7,000'),
    # ('7000-10000', '7,000 - 10,000'),
    # ('10000-25000', '10,000 - 25,000'),

    ('1-1999', 'Below 1,999'),
    ('2000-4999', '2,000 - 4,999'),
    ('5000-6999', '5,000 - 6,999'),
    ('7000-9999', '7,000 - 9,999'),
    ('10000-24999', '10,000 - 24,999'),
    ('25000-1000000', 'Above 25,000'),
    ('15000-49999', '15,000 - 49,999'),
    ('20000-49999', '20,000 - 49,999'),
    ('30000-69999', '30,000 - 69,999'),
    ('50000-74999', '50,000 - 74,999'),
    ('50000-79999', '50,000 - 79,999'),
    ('70000-99999', '70,000 - 99,999'),
    ('75000-99999', '75,000 - 99,999'),
    ('80000-99999', '80,000 - 99,999'),
    ('100000-149999', '1,00,000 - 1,49,999'),
    ('150000-199999', '1,50,000 - 1,99,999'),
    ('200000-1000000', '2,00,000 Onwards')

)


class Benefit(AbstractBenefit):


    PERCENTAGE, FIXED, MULTIBUY, FIXED_PRICE, CUSTOMIZE_BENEFIT = (
        "Percentage", "Absolute", "Multibuy", "Fixed price", "Customizeprice")
    SHIPPING_PERCENTAGE, SHIPPING_ABSOLUTE, SHIPPING_FIXED_PRICE = (
        'Shipping percentage', 'Shipping absolute', 'Shipping fixed price')
    TYPE_CHOICES = (
        (PERCENTAGE, _("Discount is a percentage off of the product's value")),
        (FIXED, _("Discount is a fixed amount off of the product's value")),
        (MULTIBUY, _("Discount is to give the cheapest product for free")),
        (FIXED_PRICE,
         _("Get the products that meet the condition for a fixed price")),
        (SHIPPING_ABSOLUTE,
         _("Discount is a fixed amount of the shipping cost")),
        (SHIPPING_FIXED_PRICE, _("Get shipping for a fixed price")),
        (SHIPPING_PERCENTAGE, _("Discount is a percentage off of the shipping"
                                " cost")),
        (CUSTOMIZE_BENEFIT, _("Discount is a customize off of the product's value")),
    )
    type = models.CharField(
        _("Type"), max_length=128, choices=TYPE_CHOICES, blank=True)

    @property
    def proxy_map(self):
        return {
            self.PERCENTAGE: get_class(
                'offer.benefits', 'CustomPercentageDiscountBenefit'),
            self.FIXED: get_class(
                'offer.benefits', 'AbsoluteDiscountBenefit'),
            self.MULTIBUY: get_class(
                'offer.benefits', 'MultibuyDiscountBenefit'),
            self.FIXED_PRICE: get_class(
                'offer.benefits', 'FixedPriceBenefit'),
            self.SHIPPING_ABSOLUTE: get_class(
                'offer.benefits', 'ShippingAbsoluteDiscountBenefit'),
            self.SHIPPING_FIXED_PRICE: get_class(
                'offer.benefits', 'ShippingFixedPriceBenefit'),
            self.SHIPPING_PERCENTAGE: get_class(
                'offer.benefits', 'ShippingPercentageDiscountBenefit'),
            self.CUSTOMIZE_BENEFIT: get_class(
                'offer.benefits', 'CustomizeCouponDiscountBenefit')
        }

    def clean(self):

        if not self.type:
            return
        method_name = 'clean_%s' % self.type.lower().replace(' ', '_')
        if hasattr(self, method_name):
            getattr(self, method_name)()


class CouponDistributor(models.Model):
    """
    Model to store coupon distributor information
    """
    # Personal Details
    full_name = models.CharField(max_length=50, blank=True, null=True)
    cdn = models.CharField(max_length=20, unique=True)
    uin = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    email_id = models.EmailField()
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)

    # Bank and Other Details
    aadhar_number = models.CharField(max_length=16, blank=True, null=True)
    pan_number = models.CharField(max_length=15, blank=True, null=True)
    account_holder_name = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    bank_address = models.TextField(blank=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    account_type = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)


class PriceRangeModel(models.Model):
    """
    Model to store Price Range for discount
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price_rng = models.CharField(choices=PRICE_RANGE_TUPLE, max_length=25)
    discount_type = models.CharField(choices=DISCOUNT_TYPE, default="Percentage", max_length=128)
    discount = models.DecimalField(decimal_places=2, max_digits=10)

    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)


class Range(AbstractRange):
    min_billing_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    coupon_distibutor = models.ForeignKey(CouponDistributor, on_delete=models.CASCADE, blank= True, null=True)

    @property
    def get_total_coupon_count(self):
        count = 0
        c_obj = CustomizeCouponModel.objects.filter(range=self)
        print(c_obj)
        if c_obj:
            for obj in c_obj:
                if obj.coupon_count:
                    print('type',type(obj.coupon_count))
                    count = count + obj.coupon_count
        return count

    @property
    def get_cat(self):
        ret = ' '
        if self.included_categories.all().count() > 0:
            for cat in self.included_categories.all():
                ret = ret + cat.name + ','
            return ret[:-1]
        return ret


class CustomizeCouponModel(models.Model):

    start_datetime = models.DateTimeField('Start datetime', blank=True, null=True)
    end_datetime = models.DateTimeField('End datetime', blank= True, null= True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    voucher = models.ForeignKey(Voucher,on_delete=models.CASCADE, blank=True, null=True)
    range = models.ForeignKey(Range,on_delete=models.CASCADE, blank= True, null=True )
    coupon_count = models.PositiveIntegerField(blank=True, null=True)
    used_coupon_count = models.PositiveIntegerField(blank=True, null=True , default=0)




from oscar.apps.offer.models import *
# # noqa isort:skip

