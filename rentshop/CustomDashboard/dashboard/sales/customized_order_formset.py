# python imports
import datetime

# django imports
from django.forms import forms
from django.forms.models import inlineformset_factory

# packages imports
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model

# internal import
from .customized_order_forms import *

Basket = get_model('basket', 'Basket')
BasketLine = get_model('basket', 'Line')

Order = get_model('order', 'Order')
Product = get_model('catalogue', 'Product')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
User = get_user_model()


BaseBasketSet = inlineformset_factory(Basket, BasketLine, form=BasketModelForm, extra=1)


class BasketSet(BaseBasketSet):

    def __init__(self, *args, **kwargs):
        super(BasketSet, self).__init__(*args, **kwargs)
