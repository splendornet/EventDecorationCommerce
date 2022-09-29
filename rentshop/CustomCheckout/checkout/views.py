# python imports
import uuid
import logging

# django imports
from django.contrib.sites.models import Site
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from django import http
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import generic
from django.utils import six
from django.shortcuts import HttpResponse, render
from .forms import *
from django.urls import reverse, reverse_lazy

# 3rd party imports
from oscar.apps.checkout.views import ShippingAddressView, PaymentDetailsView, PaymentMethodView,IndexView
from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_classes, get_model
from oscar.apps.checkout import signals

# internal imports
from .utils import *
from CustomCustomer.customer.models import CustomProfile

# model/class imports

RedirectRequired, UnableToTakePayment, PaymentError \
    = get_classes( 'payment.exceptions',
    ['RedirectRequired', 'UnableToTakePayment', 'PaymentError']
)
Custom_ShippingAddressForm = get_class('checkout.forms','CustomShippingAddressForm')
CustomOrderPlacementMixin = get_class('checkout.mixins', 'CustomOrderPlacementMixin')
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')
send_email = get_class('RentCore.email', 'send_email')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')

User = get_user_model()
OrderObj = get_model('order','order')
CCavenuePaymentDetails = get_model('order', 'CCavenuePaymentDetails')
payment_details = get_model('checkout','PaymentDetails')
States = get_model('country','State')

logger = logging.getLogger('oscar.checkout')
trigger_email = get_class('RentCore.tasks', 'trigger_email')
send_sms = get_class('RentCore.email', 'send_sms')
VoucherApplication = get_model('voucher', 'VoucherApplication')

class CustomShippingAddressView(ShippingAddressView):

    """
    Order shipping view
    """

    form_class = Custom_ShippingAddressForm
    template_name = 'checkout/shipping_address1.html'
    RedirectRequired, UnableToTakePayment, PaymentError = get_classes('payment.exceptions', ['RedirectRequired', 'UnableToTakePayment', 'PaymentError'])

    def get_context_data(self, **kwargs):

        ctx = super(CustomShippingAddressView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            try:
                ctx['phone_number']=CustomProfile.objects.get(user=self.request.user.id).mobile_number
            except:
                pass
            ctx['addresses'] = self.get_available_addresses()

        ctx['states'] = States.objects.all().order_by('state_name')

        return ctx


@method_decorator(csrf_exempt, name='dispatch')
class CustomPaymentDetailsView(PaymentDetailsView, CustomOrderPlacementMixin):

    template_name = 'checkout/payment_details.html'
    template_name_preview = 'checkout/preview.html'

    def post(self, request, *args, **kwargs):

        if not self.preview:
            return http.HttpResponseBadRequest()

        if request.POST.get('action', '') == 'place_order':
            return self.handle_place_order_submission(request)
        return self.handle_payment_details_submission(request)

    def submit(self, user, basket, shipping_address, shipping_method, shipping_charge, billing_address, order_total, payment_kwargs=None, order_kwargs=None):
        print("in submit")
        if payment_kwargs is None:
            payment_kwargs = {}
        if order_kwargs is None:
            order_kwargs = {}

        assert basket.is_tax_known, ("Basket tax must be set before a user can place an order")
        assert shipping_charge.is_tax_known, ("Shipping charge tax must be set before a user can place an order")

        order_number = self.generate_order_number(basket)
        self.checkout_session.set_order_number(order_number)
        logger.info("Order #%s: beginning submission process for basket #%d", order_number, basket.id)

        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        error_msg = _(
            "A problem occurred while processing payment for this order - no payment has been taken. "
            "Please contact customer services if this problem persists"
        )

        signals.pre_payment.send_robust(sender=self, view=self)

        try:
            self.handle_payment(order_number, order_total, **payment_kwargs)
        except RedirectRequired as e:
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except UnableToTakePayment as e:
            msg = six.text_type(e)
            logger.warning(
                "Order #%s: unable to take payment (%s) - restoring basket",
                order_number, msg
            )
            self.restore_frozen_basket()
            return self.render_payment_details(self.request, error=msg, **payment_kwargs)

        except PaymentError as e:

            msg = six.text_type(e)
            logger.error("Order #%s: payment error (%s)", order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)
        except Exception as e:
            # Unhandled exception - hopefully, you will only ever see this in
            # development...
            logger.error(
                "Order #%s: unhandled exception while taking payment (%s)",
                order_number, e, exc_info=True
            )
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs
            )

        signals.post_payment.send_robust(sender=self, view=self)

        logger.info("Order #%s: payment successful, placing order", order_number)
        print("before handle order placement")
        try:
            return self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, **order_kwargs
            )
        except UnableToPlaceOrder as e:
            msg = six.text_type(e)
            logger.error("Order #%s: unable to place order - %s",
                         order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)

    def get_template_names(self):
        return [self.template_name_preview] if self.preview else [
            self.template_name]


class CustomPaymentMethodView(PaymentMethodView):

    """
    Method to view payments
    """

    def get(self, request, *args, **kwargs):
        return self.get_success_response()

    def get_success_response(self):
        return redirect('checkout:payment-details')


class PaymentCancelView(generic.View):

    """
    Payment cancel response page.
    """

    template_name = 'checkout/payment_cancel_response.html'

    def get(self, request, *args, **kwargs):

        return render(self.request, self.template_name, {})


@csrf_exempt
def payment_success(request):

    """
    Method to handel cc-ave payment success.
    :param request:
    :return:
    """

    response_data = request.POST

    try:

        response_chiper = response_data.get('encResp')
        payment_list = decrypt(response_chiper, settings.CC_WORKING_KEY)

        order_number = None
        order_transaction_id = None
        payment_status = None
        payment_tracking_id = None
        payment_currency = None
        payment_amount = None
        payment_user_id = None

        for data in payment_list:

            # fetch order id
            if data.get('order_id'):
                order_number = data.get('order_id')

            # fetch order status
            if data.get('order_status'):
                payment_status = data.get('order_status')

            # fetch payment tracking id
            if data.get('tracking_id'):
                payment_tracking_id = data.get('tracking_id')

            if data.get('amount'):
                payment_amount = data.get('amount')

            if data.get('currency'):
                payment_currency = data.get('currency')

            if data.get('merchant_param1'):
                payment_user_id = data.get('merchant_param1')

            if data.get('merchant_param2'):
                order_transaction_id = data.get('merchant_param2')

        pay_status = 'success'
        if payment_status == 'Success':
            pay_status = 'success'
        elif payment_status == 'Failure':
            pay_status = 'failed'
        elif payment_status == 'Aborted':
            pay_status = 'cancel'
        elif payment_status == 'Invalid':
            pay_status = 'invalid'
        else:
            pay_status = 'pending'

        cc_data = {
            'status': pay_status, 'payment_reference_id': payment_tracking_id,
            'gateway_response': payment_list, 'gateway_chiper': request.POST.get('encResp')
        }

        # update cc-ave payment instance.
        CCavenuePaymentDetails.objects.filter(order_number=order_number, transaction_id=order_transaction_id).update(**cc_data)

        # update order status
        if not pay_status=='success':
            coupon_used=VoucherApplication.objects.filter(order__number=order_number)
            coupon_used.delete()

        order_data = {
            'order_payment_status': pay_status,
            
            'status': 'Initiated'
        }

        OrderObj.objects.filter(number=order_number).update(**order_data)

        try:

            order_user = User.objects.get(id=payment_user_id)
            order = OrderObj.objects.get(number=order_number, user=order_user)

            # send cancel email
            user_email_data = {
                'mail_subject': 'TakeRentPe : Order placed',
                'mail_template': 'customer/email/order_booked_email.html',
                'mail_to': [order_user.email],
                'mail_type': 'order_placed',
                'order_id': order.id,
                'order_user_id': order_user.id
            }

            trigger_email.delay(**user_email_data)

            # send sms to client THANK YOU ORDER BOOKING
            message = 'Order booked: Thank you for connecting with us. For your next purchase, we’re going to share you more offers soon. Take Rent Pe.'
            if order_user.is_staff:
                active_user = User.objects.filter(id=payment_user_id).values_list('id')
                active_partner = Partner.objects.filter(users__in=active_user)
                mobile_number = active_partner.last().telephone_number
            else:
                mobile_number = order_user.profile_user.mobile_number
            msg_kwargs = {
                'message': message,
                'mobile_number': mobile_number,
            }
            send_sms(**msg_kwargs)

            order_obj = OrderObj.objects.filter(number = order_number)
            if order_obj.last().order_type == 'partial':

                # send sms to client ADVANCE PAYMENT
                # message = 'Your advance payment is successfully received for Order No. ' + str(order_obj.last().number)
                message = 'Your advance payment is successfully received for Order No. ' + str(order_obj.last().number)+' Take Rent Pe.'
                if order_user.is_staff:
                    active_user = User.objects.filter(id=payment_user_id).values_list('id')
                    active_partner = Partner.objects.filter(users__in=active_user)
                    mobile_number = active_partner.last().telephone_number
                else:
                    mobile_number = order_user.profile_user.mobile_number
                msg_kwargs = {
                    'message': message,
                    'mobile_number': mobile_number,
                }
                send_sms(**msg_kwargs)

                advanced_pay_email_data = {
                    'mail_subject': 'TakeRentPe : Advanced Payment',
                    'mail_template': 'customer/email/order_advanced_payment.html',
                    'mail_to': [order_user.email],
                    'mail_type': 'order_placed_advance_payment',
                    'order_id': order.id,
                    'order_user_id': order_user.id,
                }
                # send_email(**advanced_pay_email_data)
                trigger_email.delay(**advanced_pay_email_data)

            if order_obj.last().order_type == 'full':
                # send sms to client FULL PAYMENT
                # message = 'Your full payment is successfully received for Order No. ' + str(order_obj.last().number)
                message = 'Your full payment is successfully received for Order No. ' + str(order_obj.last().number)+' Take Rent Pe.'
                if order_user.is_staff:
                    active_user = User.objects.filter(id=payment_user_id).values_list('id')
                    active_partner = Partner.objects.filter(users__in=active_user)
                    mobile_number = active_partner.last().telephone_number
                else:
                    mobile_number = order_user.profile_user.mobile_number
                msg_kwargs = {
                    'message': message,
                    'mobile_number': mobile_number,
                }
                send_sms(**msg_kwargs)

                full_pay_email_data = {
                    'mail_subject': 'TakeRentPe : Full Payment',
                    'mail_template': 'customer/email/order_full_payment.html',
                    'mail_to': [order_user.email],
                    'mail_type': 'order_placed_full_payment',
                    'order_id': order.id,
                    'order_user_id': order_user.id,
                }

                trigger_email.delay(**full_pay_email_data)

        except Exception as e:
            import os
            import sys
            print('-----------in exception----------')
            print(e.args)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print('-----------in exception----------')

        allocate_vendor(order_number)
        
        messages.success("Payment recieved successfully")
        return redirect('/')
        # return redirect('/accounts/orders/')

    except Exception as e:

        return redirect('/')


@csrf_exempt
def payment_cancel(request):

    """
    Method to handel cc-ave.
    :param request: data
    :return: status
    """

    response_data = request.POST

    try:

        response_chiper = response_data.get('encResp')
        payment_list = decrypt(response_chiper, settings.CC_WORKING_KEY)

        order_number = None
        order_transaction_id = None
        payment_status = None
        payment_tracking_id = None
        payment_currency = None
        payment_amount = None
        payment_user_id = None

        for data in payment_list:

            if data.get('order_id'):
                order_number = data.get('order_id')

            if data.get('order_status'):
                payment_status = data.get('order_status')

            if data.get('tracking_id'):
                payment_tracking_id = data.get('tracking_id')

            if data.get('amount'):
                payment_amount = data.get('amount')

            if data.get('currency'):
                payment_currency = data.get('currency')

            if data.get('merchant_param1'):
                payment_user_id = data.get('merchant_param1')

            if data.get('merchant_param2'):
                order_transaction_id = data.get('merchant_param2')

        # get cc-ave payment status.
        pay_status = 'cancel'
        if payment_status == 'Aborted':
            pay_status = 'cancel'

        cc_data = {
            'status': pay_status, 'payment_reference_id': payment_tracking_id,
            'gateway_response':payment_list, 'gateway_chiper':request.POST.get('encResp')
        }

        # update cc-ave payment instance.
        CCavenuePaymentDetails.objects.filter(order_number=order_number, transaction_id=order_transaction_id).update(**cc_data)

        # update order status

        order_data = {
            'order_payment_status': pay_status,
            'status': 'Cancel'
        }

        OrderObj.objects.filter(number=order_number).update(**order_data)

        try:

            order_user = User.objects.get(id=payment_user_id)
            order = OrderObj.objects.get(number=order_number, user=order_user)

            # send cancel email
            user_email_data = {
                'mail_subject': 'TakeRentPe : Order cancel',
                'mail_template': 'customer/email/order_payment_cancel_email.html',
                'mail_to': [order_user.email],
                'mail_type': 'order_failed',
                'order_id': order.id,
                'order_user_id': order_user.id
            }

            # send_email(**user_email_data)
            trigger_email.delay(**user_email_data)

        except:
            pass

        return redirect('/order_payment_cancel/')

    except:

        return redirect('/order_payment_cancel/')


class CreateCustomBillingAddress(CheckoutSessionMixin,generic.FormView):

    """

    """

    template_name = 'checkout/billing_address1.html'
    form = CustomBillingAddressForm

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('fill_form')
        form = self.form()
        if pk == '1':
            cust_obj = CustomBillingAddress.objects.filter(user=request.user)
            cust = cust_obj.last()
            form = self.form(instance = cust)
        return render(request, self.template_name, {'form': form, 'states': States.objects.all().order_by('state_name')})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST)
        pk = kwargs.get('fill_form')

        if request.user.is_superuser or pk == '1':

            addr = CustomBillingAddress.objects.filter(id=pk)

            if addr:
                form = self.form_class(request.POST, instance=addr.last())

        if form.is_valid():

            try:
                base_form = form.save(commit=False)
                base_form.user = request.user
                base_form.save()

                return redirect('/checkout/shipping-address/')

            except Exception as e:

                messages.error(request, 'Something went wrong.')
                return redirect('/')

        else:
            pass

        return render(request, self.template_name, {'form': form, 'states': States.objects.all().order_by('state_name')})


class CustomIndexView(IndexView):

    success_url = reverse_lazy('checkout:billing_address',kwargs={'fill_form': 0})

def get_transaction_details(request):

    api_url = "https://api.ccavenue.com/apis/servlet/DoWebTrans"

    # payment = Payment.objects.filter(gateway='ccavenue', charge_status='not-charged')
    order_number_list = [100630,100629,100628]
    orders = Order.objects.filter(number__in=order_number_list)

    for order in orders:
        print("order id",order.id)
        p_order_id = str(order.id)
        # p_merchant_param3 = order.token
        p_merchant_id = str(settings.CC_MERCHANT_ID)
        # merchant_data = 'merchant_id=' + p_merchant_id + '&' + 'order_id=' + p_order_id + 'merchant_param3=' + p_merchant_param3
        merchant_data = 'merchant_id=' + p_merchant_id + '&' + 'order_id=' + p_order_id + '&' + 'merchant_param3=' + ''
        print("merchant data", merchant_data)
        enc_request = encrypt(merchant_data, settings.CC_WORKING_KEY)
        access_code = settings.CC_ACCESS_CODE
        request_type = 'JSON'
        request_data = {
            'enc_request': enc_request,
            'access_code': access_code,
            'request_type': request_type,
            'command': 'orderStatusTracker'
        }
        import requests
        response = requests.post(api_url, data=request_data)
        print(response)
        message = str(response.content)

   #      CCAvenueRawResponse.objects.create(
   #          raw_response=message
   #      )
   #
        try:
            r = {
                "order_no": str(order.id)
            }

            enc_request = encrypt(str(r), settings.API_CC_WORKING_KEY)

            access_code = settings.API_CC_ACCESS_CODE
            request_type = 'JSON'
            request_data = {
                'enc_request': enc_request,
                'access_code': access_code,
                'request_type': request_type,
                'command': 'orderStatusTracker'
            }

            response = requests.post(api_url, data=request_data)
            message1 = str(response.content)

            # CCAvenueRawResponse.objects.create(
            #     raw_response=message, raw_request=str(request_data)
            # )

            # a = b'status=0&enc_response=8928b8aa1a4bdffd1e31d917742410c90837c5a65154da27d928d33aec59cd196acc377b5862104d7585c7029cb6849861605f7e4abc4378af0e0a31d7803596c2f90dd94ee5100635be6faff814a4f4e21269ef396ea1b8d6b326a817e73831993439fc9272411ecba75bb1d571c2cb5e81b4b7d1e81e6134688c80055b5d7821a97c0d3aace624884ef94822c0d61029ff7c6f081008fb34b9e499c58a5d443b76087f421aa2bf6eeace341b253a941f383326c571149114f7c2d20a867207cb6a713a4f53a31304ecfc766c244c4f8e347f868347fa5015484e4f507dd9389621cf50a7fde37d2d2b279fa2605eb588ff3932e6cae1cee9e6c4f691b9ff86e1c6f0d3398e85781235607bd558db6ddc391ea841a5986e757fd792f34f0cb5ace15f825916ce1dafbad3daac6b6d81e35e7c171c5db51d4b4b11e579c37f89256efe61e0e09633cd81c5272614aaae8742acefc12b649742876956ad7f2525708ec8de840c2283d9a40d8d38e237441c513095f1f297ed1f2e4cbf8a9deb6e932d51de16e964fc1182a57ffe62cf381dfaf1bb17e42f995d60f35dbba6d0dd9f10f59c2817cea4738fc9fbc231324b1d363775fc910880ee962d02e1b4f7de6adde7b5d1b84def2e8325a99a094f3c223350c01c64abf1e6180b9ba5d1fd76497e009505e8102b9b5d1f75de416cf5fc5b4f6caa6ded776c22b5236c9dc0a4a0aaa993525602664f994670fa94865ea5fbefd6d3bee10f03980825c17e4f6f8a3a2ea26d14ad331313727bcbde484d98f926204a791463e58e879ff75bb4c13b2c50f8d91ff57f1d519b482cb8848bbf7bb646e9cf9bdfbec398a9fce9632635fc31bdcaa77cc89ebe1064d6f7cce151a39f0e49e205e219c78a1724ac654a6e1842640e465302f1c3e74caae2579f6f8d973c256df7357310467f12da5d6e84caab9a158a7bb399c275f3d0b22d12fa519531b934503b2c3206acd67b2ff7d0474c5a4d0c74d0666189d40743300499d8b9f45d25a786e11ca86885ddc5ce7a7545c84ded873d7a106d27dcfc41a74ccf783260bb08e2d05900ce99eafd11ca316a379425014a27e899c91c06471d3c757f07aaf0684779e16ed0705dbc2ae09210c96b55f3e68a7d22e1ceac70ccff5de343b36b2622d97a595f3758f0be5716a7b11384c88a416de991571eeee7d3d8ed218415c653c7c2ba408070c7c3af56292ec7002d02b0177bfb05861afb5022dba41239eda7568c7819cfbc2caca52ab46c0179954ca8ca7f14b96b45a8330cf8639a849822339c90fee6f8f36f8fa2ed2860574582619eb4dfc9e14dd559c485c1c8e9353309ca7b1672fc702f9166be780c190cfdfe6fb8be360bee41f0038187dc7ad36a03651f4afe383ccd51a82553d2fcb338fc27873ddb97e7d696d84d27bb5c9b7197586ec7734e9aa497b2ff5c73387ab016c32340f8c5ea68ad42269b3eed2abdfa8672706bc5d5fbaca2cb377eb01c1acfdb1769866b64a130558b62635eae93b21aacb57d5407ca492cd82ce9fbcab196964dc787c523b52fa854157e19703552a92878ef43cea212e7f250bde69597ba408f4221d868c2554aeb48f606ecb8d9dbfb40394c2a916b47594b3e2eadc4f4b8927e77357bd03ab6e36c9e1b3e12e3e9a96d72b7a6d7776357b703f4e29f9903377a4082c0d6\r\n'
            enc_response = str(message).split('&')[1]
            enc_resp_str = enc_response.split("=")[1]

   #          response_json = decrypt_cron(enc_resp_str[:-5], settings.API_CC_WORKING_KEY)[0]
   #
   #          if response_json['status'] == 0:
   #              payment_status = response_json['order_status']
   #              if payment_status == 'Successful':
   #                  //write your code
   #              elif payment_status == 'Initiated' or payment_status == 'Awaited':
   #                  continue
   #
   #              elif payment_status == 'Aborted' or payment_status == 'Auto-Cancelled' or payment_status == 'Cancelled':
   # # write your code
   #              elif payment_status == 'Unsuccessful':
   # #write your code
   #              else:
   #                  pass
        except Exception as e:
            print(e.args)
            continue

    return HttpResponse("done"+message+"done"+message1)
