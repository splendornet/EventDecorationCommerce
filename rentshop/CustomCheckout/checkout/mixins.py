# python import
import random
from decimal import Decimal

# django imports
from django.conf import settings
from django.shortcuts import HttpResponse, render
from django.contrib.sites.models import Site

# 3rd party imports
from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model


# internal imports
from .utils import *


User = get_user_model()
OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
OrderCreator = get_class('order.utils', 'OrderCreator')
send_email = get_class('RentCore.email', 'send_email')
Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
CCavenuePaymentDetails = get_model('order', 'CCavenuePaymentDetails')
trigger_email = get_class('RentCore.tasks', 'trigger_email')


class CustomOrderPlacementMixin(OrderPlacementMixin):

    def generate_order_number(self, basket):

        """
        Return a new order number
        :param basket: basket id
        :return: order number
        """

        return OrderNumberGenerator().order_number(basket)

    def handle_order_placement(self, order_number, user, basket, shipping_address, shipping_method, shipping_charge, billing_address, order_total, **kwargs):

        """
        Method to place order
        :param order_number: generated order number
        :param user: order placed user
        :param basket: order basket instance
        :param shipping_address: order shipping address
        :param shipping_method: order shipping method
        :param shipping_charge: order shipping charges
        :param billing_address: order billing address
        :param order_total: order total
        :param kwargs:
        :return: order is initiated.
        """

        order = self.place_order(
            order_number=order_number, user=user, basket=basket,
            shipping_address=shipping_address, shipping_method=shipping_method,
            shipping_charge=shipping_charge, order_total=order_total,
            billing_address=billing_address, **kwargs
        )
        basket.submit()
        print("I came to basket submit")
        return self.handle_successful_order(order)

    def place_order(self, order_number, user, basket, shipping_address, shipping_method, shipping_charge, order_total, billing_address=None, **kwargs):

        """
        Method to store order data.
        :param order_number: generated order number
        :param user: order user
        :param basket: order basket instance
        :param shipping_address: order shipping address
        :param shipping_method: order shipping method
        :param shipping_charge: order shipping charges
        :param order_total: order total
        :param billing_address: order billing address
        :param kwargs:
        :return: save data into order table.
        """

        shipping_address = self.create_shipping_address(user, shipping_address)

        billing_address = self.create_billing_address(
            user, billing_address, shipping_address, **kwargs)

        if 'status' not in kwargs:
            status = self.get_initial_order_status(basket)
        else:
            status = kwargs.pop('status')

        if 'request' not in kwargs:
            request = getattr(self, 'request', None)
        else:
            request = kwargs.pop('request')

        order = OrderCreator().place_order(
            user=user, order_number=order_number, basket=basket,
            shipping_address=shipping_address, shipping_method=shipping_method, shipping_charge=shipping_charge,
            total=order_total, billing_address=billing_address, status=status,
            request=request, order_payment_status='initiated', **kwargs
        )
        self.save_payment_details(order)
        self.payment_record(order_number, order_total)
        return order

    def payment_record(self, order_number, order_total):

        """
        Method to capture order payment before payment gateway.
        :param order_number: generated order number
        :param order_total: order total
        :return: save order payment.
        """

        try:

            hash = random.getrandbits(32)
            transaction_id = str(hash)

            order = Order.objects.get(number=order_number)
            order_pay_data = {
                'order': order, 'order_number': order_number,
                'transaction_id': transaction_id, 'amount': Decimal(order_total.incl_tax),
            }

            CCavenuePaymentDetails.objects.create(
                **order_pay_data
            )

        except:

            hash = random.getrandbits(32)
            transaction_id = str(hash)

            order_pay_data = {
                'order_number': order_number,
                'transaction_id': transaction_id, 'amount': Decimal(order_total.incl_tax),
            }

            CCavenuePaymentDetails.objects.create(
                **order_pay_data
            )

        return True

    def send_confirmation_message(self, order, code, **kwargs):
        ctx = self.get_message_context(order)


    def handle_successful_order(self, order):
        print("hey i m in handle_successful_order")
        print(order)
        print("hey i m in handle_successful_order")
        self.send_confirmation_message(order, self.communication_type_code)

        self.checkout_session.flush()

        self.request.session['checkout_order_id'] = order.id
        return self.generate_payment_data(order)

    def generate_payment_data(self, order):

        # inner global
        event_obj, result, price, product_info = None, [], 0, ''

        # user
        cart_user = User.objects.get(id=self.request.user.id)
        order_lines = OrderLine.objects.filter(order=order)
        order_address = order.shipping_address

        # get current site
        current_site = Site.objects.get_current()

        # get order price
        for cart_line in order_lines:

            product_info += str(cart_line.product) + (',')

        price = order.paid_amount
        # cc-av required parameter

        # order payment table
        cc_ave_obj = CCavenuePaymentDetails.objects.filter(order=order).last()

        p_merchant_id = settings.CC_MERCHANT_ID

        p_order_id = str(self.generate_order_number(self.request.basket))
        p_currency = settings.CC_CURRENCY
        p_amount = str(price)

        p_redirect_url = str(current_site) + '/payment_success/'
        p_cancel_url = str(current_site) + '/payment_cancel/'

        p_language = settings.CC_LANG

        p_billing_name = order_address.first_name + ' ' + order_address.last_name
        p_billing_address = str(order_address)
        p_billing_city = order_address.city
        p_billing_state = order_address.state
        p_billing_zip = str(order_address.postcode)
        p_billing_country = settings.CC_BILL_CONTRY
        p_billing_tel = str(order_address.phone_number)
        p_billing_email = cart_user.email

        p_delivery_name = ''
        p_delivery_address = ''
        p_delivery_city = ''
        p_delivery_state = ''
        p_delivery_zip = ''
        p_delivery_country = 'India'
        p_delivery_tel = ''

        p_merchant_param1 = str(cart_user.id)
        p_merchant_param2 = str(cc_ave_obj.transaction_id)
        p_merchant_param3 = ''
        p_merchant_param4 = ''
        p_merchant_param5 = ''
        p_promo_code = ''

        p_customer_identifier = ''
        merchant_data = 'merchant_id=' + p_merchant_id + '&' + 'order_id=' + p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount + '&' + 'redirect_url=' + p_redirect_url + '&' + 'cancel_url=' + p_cancel_url + '&' + 'language=' + p_language + '&' + 'billing_name=' + p_billing_name + '&' + 'billing_address=' + p_billing_address + '&' + 'billing_city=' + p_billing_city + '&' + 'billing_state=' + p_billing_state + '&' + 'billing_zip=' + p_billing_zip + '&' + 'billing_country=' + p_billing_country + '&' + 'billing_tel=' + p_billing_tel + '&' + 'billing_email=' + p_billing_email + '&' + 'delivery_name=' + p_delivery_name + '&' + 'delivery_address=' + p_delivery_address + '&' + 'delivery_city=' + p_delivery_city + '&' + 'delivery_state=' + p_delivery_state + '&' + 'delivery_zip=' + p_delivery_zip + '&' + 'delivery_country=' + p_delivery_country + '&' + 'delivery_tel=' + p_delivery_tel + '&' + 'merchant_param1=' + p_merchant_param1 + '&' + 'merchant_param2=' + p_merchant_param2 + '&' + 'merchant_param3=' + p_merchant_param3 + '&' + 'merchant_param4=' + p_merchant_param4 + '&' + 'merchant_param5=' + p_merchant_param5 + '&' + 'promo_code=' + p_promo_code + '&' + 'customer_identifier=' + p_customer_identifier + '&'
        encryption = encrypt(merchant_data, settings.CC_WORKING_KEY)

        data_dict = {
            'p_redirect_url': p_redirect_url,
            'encryption': encryption, 'access_code': settings.CC_ACCESS_CODE,
            'cc_url': settings.CC_URL
        }
        print("Hey i m in mixin")
        print(data_dict)
        print("Hey i m in mixin")
        # before payment email

        try:

            order_user = User.objects.get(id=cart_user.id)

            # send cancel email
            user_email_data = {
                'mail_subject': 'TakeRentPe : Order initiated',
                'mail_template': 'customer/email/order_payment_booked_email.html',
                'mail_to': [order_user.email],
                'mail_context': {
                    'user': order_user
                }
            }
            trigger_email.delay(**user_email_data)
            # send_email(**user_email_data)

        except Exception as e:
            print(e.args)
            pass

        # before payment email

        return render(self.request, 'checkout/cc_avenue_payment_page.html', context=data_dict)
