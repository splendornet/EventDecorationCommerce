from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views import generic
from oscar.core.application import Application
from oscar.core.loading import get_class
from oscar.apps.customer.app import CustomerApplication as CoreCustomerApplication


class CustomerApplication(CoreCustomerApplication):

    name = 'customer'

    login_view = get_class('customer.views', 'CustomAccountLoginView')
    register_view = get_class('customer.views', 'CustomAccountRegistrationView')
    faq = get_class('customer.views', 'FAQView')
    order_single = get_class('customer.views', 'OrderSingleProductView')
    coupon_view = get_class('customer.views', 'UserCouponView')
    profile_update_view = get_class('customer.views', 'CustomProfileUpdateView')
    custom_order = get_class('customer.views', 'CustomOrderListView')
    custom_order_place = get_class('customer.views', 'PlaceCustomOrder')

    wishlists_list_view = get_class('customer.views', 'CustomWishListListView')
    order_detail_view = get_class('customer.views', 'CustomOrderDetailView')
    profile_view = get_class('customer.views', 'CustomProfileView')

    change_password_view = get_class('customer.views', 'CustomChangePasswordView')

    def get_urls(self):

        urls = [
            url(r'faq', self.faq.as_view(), name='user-faq'),
            url(r'order/(?P<order_id>\d+)/detail/(?P<product_id>\d+)/(?P<line_id>\d+)', self.order_single.as_view(), name='user-only-order'),
            url(r'coupon/', self.coupon_view.as_view(), name='user-my-coupon'),
            url(r'custom_order/', self.custom_order.as_view(), name='user-custom-order'),
            url(r'custom_order_place/', self.custom_order_place.as_view(), name='user-custom-order-place'),
        ]

        urls = urls + super(CustomerApplication, self).get_urls()
        return urls


application = CustomerApplication()


