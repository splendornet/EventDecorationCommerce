# python imports

# django imports
from django.conf import settings
from django import forms
from django.core.validators import RegexValidator

# 3rd party imports
from oscar.core.loading import get_model

# internal imports
ContactUs = get_model('customer', 'ContactUs')


class ContactUsForm(forms.ModelForm):

    """
    Contact us form.
    """

    name = forms.CharField(max_length=30, required=True, label='Name', validators=[RegexValidator('^([A-Za-z ])+$', message='Enter a valid name.')])
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Phone', max_length=10, required=True, validators=[RegexValidator('^[6-9]\d{9}$', message='Please enter valid mobile number.')])
    message = forms.CharField(required=True, label='Message', max_length=200, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ContactUsForm, self).__init__(*args, **kwargs)

        #self.fields['name'].widget.attrs['placeholder'] = 'Name'
        #self.fields['email'].widget.attrs['placeholder'] = 'Email ID'
        #self.fields['phone'].widget.attrs['placeholder'] = 'Mobile Number'

    class Meta:

        model = ContactUs
        fields = ('name', 'email', 'phone', 'message',)