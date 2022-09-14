# python imports

# django imports
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# 3rd party imports
from oscar.apps.dashboard.partners import forms as base_forms
from oscar.apps.catalogue.categories import *

# internal imports
from country.models import *

Partner = get_model('partner', 'Partner')
Country = get_model('country', 'Country')
State = get_model('country', 'State')
City = get_model('country', 'City')
categories_choices = []
state_default = (('','Select State'),)
city_default = (('','Select City'),)


def validate_image_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Please upload only .jpg or .png image.')


class PartnerUpdateForm(base_forms.PartnerCreateForm):

    """
    Oscar extended form to update vendor.
    """

    name = forms.CharField(min_length=2,max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder':'Owner Name'}), validators = [RegexValidator('^([A-Za-z_ ])+$', message='Enter a valid Name.')])

    telephone_number = forms.CharField(max_length=10, min_length=10, required=True, validators=[RegexValidator('^([0-9]{10})+$' ,message='Enter a valid number.')])
    alternate_mobile_number = forms.CharField(max_length=10, min_length=10, required=True, validators=[RegexValidator('^([0-9]{10})+$' ,message='Enter a valid alternate number.')])

    address_line_1 = forms.CharField(max_length=100,required=True, widget=forms.TextInput(attrs={'placeholder': 'Address Line 1'}))
    address_line_2 = forms.CharField(max_length=100 ,required=True,widget=forms.TextInput(attrs={'placeholder': 'Address Line 2'}))

    country = forms.ModelChoiceField(queryset=Country.objects.all(), initial=0)
    state = forms.ModelChoiceField(queryset=State.objects.all().order_by('state_name'))
    city = forms.ModelChoiceField(queryset=City.objects.all().order_by('city_name'))
    pincode = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Pincode'}), validators=[RegexValidator('^([0-9]{6})+$' ,message='Enter a valid Pin Code.')])

    business_name = forms.CharField(min_length=2, max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder':'Business Name'}))
    user_active = forms.BooleanField(required=False)

    digital_signature = forms.ImageField(required=False, validators=[validate_image_extension])

    pan_number = forms.CharField(required=False, max_length=20, validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', message='Enter a pan number.')])
    gst_number = forms.CharField(required=False, max_length=20, validators=[RegexValidator(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', message='Enter a gst number.')])

    class Meta(base_forms.PartnerCreateForm.Meta):

        fields = (
            'business_name', 'name', 'email_id', 'telephone_number',
            'alternate_mobile_number', 'address_line_1',
            'address_line_2', 'country', 'state', 'city', 'pincode',
            'user_active', 'digital_signature', 'pan_number', 'gst_number',
        )

        exclude = ('code', 'country_id', 'categories',)

    def __init__(self, *args, **kwargs):

        super(PartnerUpdateForm, self).__init__(*args,**kwargs)

        self.fields['pan_number'].widget.attrs['class'] = 'form-control'
        self.fields['gst_number'].widget.attrs['class'] = 'form-control'

    def clean(self):

        cleaned_data = super(PartnerUpdateForm, self).clean()
        email_id = cleaned_data['email_id'].lower()
        partner_id = Partner.objects.get(id=self.instance.pk)
        user_ids = partner_id.users.all()
        if User.objects.exclude(id__in=user_ids).filter(username=email_id).exists():
            raise ValidationError({'email_id': ["ASP with that Email Id is already exists."]})
        return cleaned_data

    def clean_telephone_number(self):

        number = self.cleaned_data['telephone_number']
        if Partner.objects.filter(telephone_number__iexact=number).exclude(id=self.instance.pk).exists():
            raise forms.ValidationError(
                _("A user with that mobile number address already exists."))

        return number

    def clean_alternate_mobile_number(self):
        number = self.cleaned_data['alternate_mobile_number']
        if Partner.objects.filter(alternate_mobile_number__iexact=number).exclude(id=self.instance.pk).exists():
            raise forms.ValidationError(
                _("A user with that mobile number address already exists."))

        return number
