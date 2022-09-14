# python imports
import datetime

# django imports
from django.forms import forms

# packages imports
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model

# internal import
from .asp_db_forms import *


Basket = get_model('basket', 'Basket')
BasketLine = get_model('basket', 'Line')

Order = get_model('order', 'Order')
Product = get_model('catalogue', 'Product')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
User = get_user_model()


class UserModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):

        if obj.get_full_name():
            return obj.get_full_name()
        return obj.email


class CustomOrderSearchForm(forms.Form):

    order_number = forms.CharField(required=False, max_length=20)
    product = forms.ModelChoiceField(required=False, queryset=Product.objects.all())

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        self.request = kwargs.pop('request', None)
        super(CustomOrderSearchForm, self).__init__(*args, **kwargs)


class CustomOrderSelectCustomerForm(forms.Form):

    customer = UserModelChoiceField(queryset=User.objects.filter(is_active=True, is_staff=False))


class BasketModelForm(forms.ModelForm):

    class Meta:

        model = BasketLine
        fields = ('basket', 'product', 'quantity', 'order_type', 'booking_start_date', 'booking_end_date', 'product_attributes',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(BasketModelForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['class'] = 'form-control'

        self.fields['product'].widget.attrs['class'] = 'custom-order-product'
        self.fields['product'].queryset = Product.objects.filter(id__in=['8973', '8969'],is_deleted=False)

        self.fields['product_attributes'].widget = forms.HiddenInput()
