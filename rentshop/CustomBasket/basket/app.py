# 3rd party import
from oscar.apps.basket.app import BasketApplication as CoreBasketApplication
from oscar.core.loading import get_class


class BasketApplication(CoreBasketApplication):

    """
    Basket app extended.
    """

    add_view = get_class('basket.views', 'CustomBasketAddView')
    summary_view = get_class('basket.views', 'CustomBasketView')
    add_voucher_view = get_class('basket.views', 'CustomVoucherAddView')


application = BasketApplication()
