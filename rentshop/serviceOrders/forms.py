from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import pgettext_lazy

from .models import ServiceOrders


class ServiceEnquiryForm(forms.ModelForm):
    name = forms.CharField(max_length=100, min_length=3, required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter Name'}))
    mobile_number = forms.CharField(max_length=10, required=True, validators=[RegexValidator(regex='^[6-9]\d{9}$',message='Invalid Mobile No.',code='invalid_mobile_no'),
    ], widget=forms.TextInput(attrs={'class': 'form-control onlyNumber', 'placeholder': 'Enter Mobile No.'}))
    email = forms.EmailField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}))
    booking_date = forms.DateField(required=True)
    class Meta:
        model = ServiceOrders
        fields = ('name', 'mobile_number', 'email', 'booking_date')

class ServiceOrderSearchForm(forms.Form):
    name = forms.CharField(
        required=False, label=pgettext_lazy(u"Name's name", u"Name"))
