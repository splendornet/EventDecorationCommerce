# django imports
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

# package import
from oscar.core.loading import get_class, get_model
from oscar.forms.widgets import DatePickerInput

# internal imports
Category = get_model('catalogue', 'Category')


class AccountSearchForm(forms.Form):

    order_number = forms.CharField(required=False)
    customer_name = forms.CharField(required=False)
    order_date = forms.DateField(required=False, widget=DatePickerInput)
    

class ProductMarginSearchForm(forms.Form):

    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)
    vendor_name = forms.CharField(required=False)
    product_name = forms.CharField(required=False)
    upc = forms.CharField(required=False)


class SetProductMarginForm(forms.Form):

    """

    """

    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)
    product_name = forms.CharField(required=False)
    upc = forms.CharField(required=False)