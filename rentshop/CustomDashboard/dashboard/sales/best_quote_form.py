# django imports
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django_select2.forms import Select2Widget, Select2MultipleWidget

# package import
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model

# internal imports
User = get_user_model()
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
Partner = get_model('partner', 'Partner')

class EnquirySearchForm(forms.Form):

    organization_name = forms.CharField(required=False, max_length=100)
    person_name = forms.CharField(required=False, max_length=100)
    email = forms.CharField(required=False, max_length=100)
    city = forms.CharField(required=False, max_length=100)

class OrderAllocateForm(forms.Form):

    vendors = forms.ModelMultipleChoiceField(queryset=Partner.objects.all(), widget= Select2MultipleWidget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = User.objects.filter(is_active=True, is_staff=True).values_list('id')
        self.fields['vendors'].queryset = Partner.objects.filter(users__in=users)

