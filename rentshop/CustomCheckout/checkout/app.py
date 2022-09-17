from django.conf import settings
from django.conf.urls import url
from django.urls import path

from django.contrib.auth.decorators import login_required
from oscar.core.application import Application
from oscar.core.loading import get_class
from oscar.apps.checkout.app import CheckoutApplication as CoreCheckoutApplication


class CheckoutApplication(CoreCheckoutApplication):
    shipping_address_view = get_class('checkout.views', 'CustomShippingAddressView')
    payment_details_view = get_class('checkout.views', 'CustomPaymentDetailsView')
    payment_method_view = get_class('checkout.views', 'PaymentMethodView')
    billing_address = get_class('checkout.views', 'CreateCustomBillingAddress')
    index_view = get_class('checkout.views', 'CustomIndexView')



    def get_urls(self):
        urlpatterns = super(CheckoutApplication, self).get_urls()
        urlpatterns += [
            url(r'^billing_address/(?P<fill_form>\d+)', self.billing_address.as_view(), name='billing_address'),
            url(r'^shipping_address/', self.shipping_address_view.as_view(), name='shipping_address'),
            path('', self.index_view.as_view(), name='index'),

        ]
        return self.post_process_urls(urlpatterns)


application = CheckoutApplication()
