# python imports
import hashlib
import logging, os
from collections import OrderedDict
from decimal import Decimal as D
import datetime

# django imports
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signing import BadSignature, Signer
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy


# 3rd party imports
from oscar.apps.order.abstract_models import AbstractOrder, AbstractLine
from oscar.apps.order.signals import (order_line_status_changed, order_status_changed)
from oscar.core.compat import AUTH_USER_MODEL
from oscar.core.loading import get_model, get_class
from oscar.core.utils import get_default_currency
from oscar.models.fields import AutoSlugField
from oscar.models.fields import UppercaseCharField

from django.contrib.auth.models import User

Partner = get_model('partner', 'Partner')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
generate_order_summary = get_class('order.invoice', 'generate_order_summary')
IndividualDB = get_model('partner', 'IndividualDB')
generate_order_invoice = get_class('order.invoice', 'generate_order_invoice')
generate_order_invoice_product = get_class('order.invoice', 'generate_order_invoice_product')
Voucher = get_model('voucher', 'Voucher')


logger = logging.getLogger('oscar.order')
ORDER_PAYMENT_STATUS = (
    ('initiated', 'Initiated'),
    ('success', 'Success'),
    ('failed', 'Failed'),
    ('pending', 'Pending'),
    ('cancel', 'Cancel'),
    ('invalid', 'Invalid'),
)


class Order(AbstractOrder):

    """
    Model to store orders
    """

    advance_payment_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    minimum_qty = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    shipping_charges = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    order_type = models.CharField(max_length=100, null=True, blank=True)
    booking_start_date = models.DateTimeField(blank=True, null=True)
    booking_end_date = models.DateTimeField(blank=True, null=True)
    total_amount_incl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    paid_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    order_payment_status = models.CharField(max_length=100, blank=True, null=True, choices=ORDER_PAYMENT_STATUS)
    is_refund = models.BooleanField(default=False)
    order_cancelled_date = models.DateTimeField(blank=True, null=True)

    total_deposit_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    advance_payment_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    balance_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    customized_order = models.BooleanField(default=False)

    order_margin_price = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    user_billing_address = models.ForeignKey('order.CustomBillingAddress', blank=True, null=True, on_delete=models.SET_NULL)
    user_billing_id = models.CharField(max_length=100, blank=True, null=True)

    @property
    def allocated_order_lines(self):

        sum = 0

        try:

            for i in self.lines.all():
                if i.allocated_order_line.all():
                    sum = sum + 1
                # if IndividualDB.objects.filter(category=i.product.categories.all().last()):
                #     print("sum@@@", sum)
                #     sum = sum + 1

        except:

            pass

        return sum

    @property
    def get_shipping_charges(self):

        _sum = 0

        try:

            for line in self.lines.all():

                if line.shipping_charges:
                    _sum = _sum + line.shipping_charges

            return _sum

        except:

            return _sum

    @property
    def get_billing_address(self):

        if self.user_billing_address:
            address = self.user_billing_address

            return [
                str(address.first_name).capitalize() + ' ' + str(address.last_name).capitalize(),
                str(address.line1).capitalize(), str(address.line4).capitalize(),
                str(address.state).capitalize(), address.postcode,
                str(address.country).capitalize()
            ]

        return None

    @property
    def tax_sum(self):

        tax_sum = 0
        for line in self.lines.all():

            tax_sum = tax_sum + line.tax_amount

        return tax_sum

    def get_order_summary(self):

        summary_pdf = generate_order_summary(self)
        if summary_pdf:
            return '/' + summary_pdf

        return None

    def generate_order_invoice(self):

        summary_pdf = generate_order_invoice(self)

        if summary_pdf:
            return '/' + summary_pdf

        return None

    def order_summary_pdf_path(self):

        summary_pdf = self.get_order_summary()

        if summary_pdf:
            return settings.BASE_DIR + '/' + summary_pdf

        return None

    def order_invoice_pdf_path(self):

        invoice_pdf = self.generate_order_invoice()

        if invoice_pdf:
            return settings.BASE_DIR + '/' + invoice_pdf

        return None

    def order_total_word(self):

        from num2words import num2words

        try:
            return num2words(self.basket_total_incl_tax).title()
        except:
            return self.basket_total_incl_tax

    @property
    def basket_total_excl_tax(self):
        return self.total_excl_tax - self.shipping_excl_tax

    @property
    def total_discount_excl_tax(self):
        discount = D('0.00')
        print(self.basket_discounts)
        for discount_obj in self.basket_discounts:
            discount += discount_obj.amount
        return discount

    @property
    def order_total_after_discount(self):

        """
        Method to calculate order total after discount.
        :return: value
        """

        order_total_ad = self.total_amount_incl_tax - self.total_discount_excl_tax
        return order_total_ad

    @property
    def due_amount(self):

        """
        Method to calculate order due amount
        :return: value
        """

        paid_amount = self.total_discount_excl_tax + self.paid_amount
        order_total_amt = self.total_amount_incl_tax - paid_amount

        return order_total_amt

    @property
    def date_passed(self):
        return self.date_placed < datetime.datetime.now()

    @property
    def refund_amount(self):
        cancelled_day = 0
        refund_amount = 0.0

        if self.date_placed and self.order_cancelled_date:
            lines = self.lines.all()
            l1 =[]
            for line in lines:
                if line.order_type != 'Sale':
                    print(self.number,line.booking_start_date)

            total_days = self.order_cancelled_date - self.date_placed
            cancelled_day = total_days.days
            qs = CancellationCharges.objects.all()
            if cancelled_day >= 30:
                obj = qs.filter(apply_to ='1')
                if obj:
                    refund_amount = (self.paid_amount * obj.last().charges_percentage) / 100
                else:
                    refund_amount = (self.paid_amount * 80) / 100
            elif cancelled_day >= 15 and cancelled_day <30:
                obj = qs.filter(apply_to='2')
                print(obj)
                if obj:
                    refund_amount = (self.paid_amount * obj.last().charges_percentage) / 100
                else:
                    refund_amount = (self.paid_amount * 70) / 100
            elif cancelled_day >= 5 and cancelled_day < 15 :

                obj = qs.filter(apply_to='3')
                if obj:
                    refund_amount = (self.paid_amount * obj.last().charges_percentage) / 100
                else:
                    refund_amount = (self.paid_amount * 50) / 100
            else:
                obj = qs.filter(apply_to ='4')
                if obj:
                    refund_amount = (self.paid_amount * obj.last().charges_percentage) / 100
                else:
                    refund_amount = (self.paid_amount * 30) / 100
        return refund_amount


class Line(AbstractLine):

    """
    Model to store order line.
    """

    advance_payment_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    minimum_qty = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    shipping_charges = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    order_type = models.CharField(max_length=100, null=True, blank=True)
    booking_start_date = models.DateTimeField(blank=True, null=True)
    booking_end_date = models.DateTimeField(blank=True, null=True)
    total_amount_incl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    allocated_vendor = models.ForeignKey(Partner, on_delete=models.SET_NULL, blank=True, null=True, related_name='order_line_allocated_vendor'),
    allocated_vendor_name = models.CharField(max_length=255, blank=True, null=True)

    deposit_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    final_payment = models.BooleanField(default=False)
    product_attributes = models.TextField(blank=True, null=True)

    product_margin_percentage = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    product_margin_price = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    is_line_package_product = models.BooleanField(default = False)


    @property
    def get_discount_amount(self):
        if self.order.basket_discounts:
            category = self.product.categories.last()
            voucher_code = self.order.basket_discounts.last().voucher_code
            offer_name = self.order.basket_discounts.last().offer_name
            try:
                voucher = Voucher.objects.get(code=voucher_code)
                offer_categories = voucher.offers.filter(name=offer_name).last().benefit.range.included_categories.all()
                if category in offer_categories:
                    benefit = voucher.offers.filter(name=offer_name).last().benefit
                    discount_type = benefit.type
                    discount = benefit.value

                    if discount_type == 'Percentage':
                        discount_amount = discount / D('100.0') * self.line_price_incl_tax * int(self.quantity)
                        return '{:,.2f}'.format(discount_amount)
                    else:
                        discount_amount = discount * int(self.quantity)
                        return '{:,.2f}'.format(discount_amount)
            except Exception as e:
                print(e.args)
                pass

        return ""


    @property
    def product_invoice(self):

        summary_pdf_product = generate_order_invoice_product(self, self.order)

        if summary_pdf_product:
            return '/' + summary_pdf_product

        return None

    @property
    def shipping_tax_raw_price(self):

        try:

            tax_1 = self.shipping_charges * 100
            tax_2 = 100 + 18

            return tax_1 / tax_2

        except:

            return 0

    @property
    def shipping_tax_price(self):

        try:
            from decimal import Decimal
            return self.shipping_tax_raw_price * Decimal(18 / 100)

        except Exception as e:
            print("*****In exception***********")
            print(e.args)
            print("*****In exception***********")
            return 0

    @property
    def tax_gst_type(self):

        try:
            prod_obj = Product.objects.get(id = self.product_id)

            if self.tax_percentage <= 6 and prod_obj.product_tax_type =='composition_tax':

                return 'NON_CTP'

            return 'CTP'

        except Exception as e:
            print(e.args)

        return 'NON_CTP'

    @property
    def tax_invoice_dist(self):

        if self.tax_gst_type == 'CTP':

            tax_value = self.tax_percentage / 2
            tax_amount = self.tax_amount / 2

            return [
                {
                    'tax_name': 'CGST',
                    'tax_rate': str(tax_value)+' %',
                    'tax_amount': tax_amount
                },
                {
                    'tax_name': 'SGST',
                    'tax_rate': str(tax_value)+' %',
                    'tax_amount': tax_amount
                },
            ]

        return None

    @property
    def tax_invoice_shipping_dist(self):
        tax_value = 18 / 2
        tax_amount = self.shipping_tax_price / 2
        return [
            {
                'tax_name': 'CGST',
                'tax_rate': str(tax_value) + ' %',
                'tax_amount': tax_amount
            },
            {
                'tax_name': 'SGST',
                'tax_rate': str(tax_value) + ' %',
                'tax_amount': tax_amount
            },
        ]
        # if self.tax_gst_type == 'CTP':
        #     tax_value = self.tax_percentage / 2
        #     tax_amount = self.shipping_tax_price / 2
        #
        #     return [
        #         {
        #             'tax_name': 'CGST',
        #             'tax_rate': str(tax_value) + ' %',
        #             'tax_amount': tax_amount
        #         },
        #         {
        #             'tax_name': 'SGST',
        #             'tax_rate': str(tax_value) + ' %',
        #             'tax_amount': tax_amount
        #         },
        #     ]
        #
        # return None

    @property
    def tax_amount(self):

        try:

            tax_price = self.line_price_incl_tax * (self.tax_percentage / 100)
            return round(tax_price, 2)

        except:

            return 0

    @property
    def tax_type(self):
        return 'GST'

    @property
    def unit_price_tax(self):
        return self.unit_price_incl_tax - self.unit_price_excl_tax

    @property
    def product_order_tax(self):

        return 0

    @property
    def pre_total(self):
        start_date = self.booking_start_date
        end_date = self.booking_end_date

        total_days = 1

        if self.unit_price_incl_tax is not None:
            if self.order_type == 'Sale':
                return self.quantity * self.unit_price_incl_tax
            elif self.order_type == 'Professional':
                date_1 = start_date
                date_2 = end_date
                total_days_obj = date_2 - date_1
                total_days = total_days_obj.days + 1
                return self.unit_price_incl_tax * self.quantity * total_days
            elif self.order_type == 'Rent':
                if start_date and end_date is not None:
                    date_1 = start_date
                    date_2 = end_date
                    total_days_obj = date_2 - date_1
                    total_days = total_days_obj.days + 1
                return self.quantity * self.unit_price_incl_tax * total_days

    @property
    def get_package_lines(self):

        if self.product.is_package:
            p_obj = Line.objects.filter(order= self.order, product__in = self.product.product_package.all())
            if p_obj:
                return p_obj
        return 0


class OrderAllocatedVendor(models.Model):

    """
    Model to store allocated vendors
    """

    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='allocated_order')
    order_line = models.ForeignKey(Line, on_delete=models.CASCADE, blank=True, null=True, related_name='allocated_order_line')
    order_number = models.CharField(max_length=100, blank=True, null=True)

    vendor = models.ForeignKey(Partner, on_delete=models.SET_NULL, blank=True, null=True, related_name='allocated_order_vendor')
    vendor_name = models.CharField(max_length=255, blank=True, null=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name='allocated_product')
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name='allocated_category')

    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_category_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):

        return self.product_category_name


class CCavenuePaymentDetails(models.Model):

    """
    Model to store cc-avenue payment details
    """

    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='cc_order')
    order_number = models.CharField(max_length=100, blank=True, null=True)

    payment_reference_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    status = models.CharField(max_length=100, default='initiated', choices=ORDER_PAYMENT_STATUS)

    gateway_response = models.TextField(blank=True, null=True)
    gateway_chiper = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'CC Avenue Payment'


class CustomBillingAddress(models.Model):
    """
        Model to store billing address
        """

    first_name = models.CharField(_("First name"), max_length=255, blank=True)
    last_name = models.CharField(_("Last name"), max_length=255, blank=True)

    line1 = models.CharField(_("First line of address"), max_length=255)

    line4 = models.CharField(_("City"), max_length=255, blank=True)
    state = models.CharField(_("State/County"), max_length=255, blank=True)
    postcode = UppercaseCharField(
        _("Post/Zip-code"), max_length=64, blank=True)
    country = models.ForeignKey(
        'address.Country',
        on_delete=models.CASCADE,
        verbose_name=_("Country"))
    email = models.EmailField(blank=True,null =True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_billing',blank=True, null=True,)

class CancellationCharges(models.Model):

    CHARGES_APPLY_CHOICES=(
        ('1', 'Before 1 Month'),
        ('2', 'Before 15 Days'),
        ('3', 'Before 5 Days'),
        ('4', 'On the Event Date'),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    charges_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    apply_to = models.CharField(choices=CHARGES_APPLY_CHOICES, max_length=255, )


from oscar.apps.order.models import *  # noqa isort:skip