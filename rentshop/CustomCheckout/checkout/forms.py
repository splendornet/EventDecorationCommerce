from django import forms
from oscar.apps.checkout.forms import ShippingAddressForm
from oscar.core.loading import get_class, get_model
from django.core.validators import RegexValidator, MaxLengthValidator

Country = get_model('address', 'Country')
Country_Country = get_model('country', 'Country')
CustomBillingAddress = get_model('order', 'CustomBillingAddress')


class CustomShippingAddressForm(ShippingAddressForm):

    first_name = forms.CharField(min_length=2, max_length=20, validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid first name.')])
    last_name = forms.CharField(min_length=2, max_length=20, validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid last name.')])
    line4 = forms.CharField(min_length=2, max_length=100, label=('City'), validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid city name.')])
    state = forms.CharField(min_length=2, max_length=100, label=('State'), validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid state name.')],required=False)
    notes = forms.CharField(max_length=225, required=False, widget=forms.Textarea)
    country = forms.ModelChoiceField(queryset=Country_Country.objects.filter(country_name='India'), initial='India')
    phone_number = forms.CharField(max_length=15,min_length=10)
    line1 = forms.CharField(max_length=100, min_length=2, validators=[RegexValidator('^[ A-Za-z0-9_,/.@-]*$',
                                                                                     message='Enter a valid address line 1. Only allowed (Alphabets, numbers and @-,/_.)')],required=True)
    postcode = forms.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['title'].widget = forms.HiddenInput()
        self.fields['line3'].widget = forms.HiddenInput()
        self.adjust_country_field()
        self.fields['notes'].label = "Customer's Note"
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['state'].widget.attrs['placeholder'] = 'State'
        self.fields['country'].widget.attrs['placeholder'] = 'Country'
        self.fields['line1'].widget.attrs['placeholder'] = 'Address'
        self.fields['postcode'].widget.attrs['placeholder'] = 'Pincode'
        self.fields['line4'].widget.attrs['placeholder'] = 'City'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Number'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['line4'].widget.attrs['class'] = 'form-control'
        self.fields['line1'].widget.attrs['class'] = 'form-control'
        self.fields['postcode'].widget.attrs['class'] = 'form-control'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control'


    def adjust_country_field(self):

        countries = Country._default_manager.filter(name='Republic of India', is_shipping_country=True)
        self.fields['country'].queryset = countries

    def clean_postcode(self):
        postcode = self.cleaned_data['postcode']

        postcode = postcode.replace(' ', '')
        if len(postcode)!= 6:
            raise forms.ValidationError('Enter valid postal code')
        else:
            return postcode



class CustomBillingAddressForm(forms.ModelForm):


    first_name = forms.CharField(min_length=2, max_length=20, validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid first name.')])
    last_name = forms.CharField(min_length=2, max_length=20, validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid last name.')])
    line4 = forms.CharField(min_length=2, max_length=100, label=('City'), validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid city name.')])
    state = forms.CharField(min_length=2, max_length=100, label=('State'), validators=[RegexValidator('^([A-Za-z])+$', message='Enter a valid state name.')])
    country = forms.ModelChoiceField(queryset=Country_Country.objects.filter(country_name='India'), initial='India')
    line1 = forms.CharField(max_length=100, min_length=2, validators=[RegexValidator('^[ A-Za-z0-9_,/.@-]*$',
             message='Enter a valid address line 1. Only allowed (Alphabets, numbers and @-,/_.)')])
    postcode = forms.CharField(max_length=10)
    class Meta:
        model = CustomBillingAddress
        fields = (
            'first_name', 'last_name', 'line4','line1',
            'state','country','postcode',
            'email', 'user'
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['user'].widget = forms.HiddenInput()
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['state'].widget.attrs['placeholder'] = 'State'
        self.fields['country'].widget.attrs['placeholder'] = 'Country'
        self.fields['line1'].widget.attrs['placeholder'] = 'Address'
        self.fields['postcode'].widget.attrs['placeholder'] = 'Pincode'
        self.fields['line4'].widget.attrs['placeholder'] = 'City'
        self.fields['email'].label = 'Email Address'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['line4'].widget.attrs['class'] = 'form-control'
        self.fields['line1'].widget.attrs['class'] = 'form-control'
        self.fields['postcode'].widget.attrs['class'] = 'form-control'
        self.adjust_country_field()

    def adjust_country_field(self):

        countries = Country._default_manager.filter(name='Republic of India', is_shipping_country=True)
        self.fields['country'].queryset = countries

    def clean_postcode(self):
        postcode = self.cleaned_data['postcode']

        postcode = postcode.replace(' ', '')
        if len(postcode)!= 6:
            raise forms.ValidationError('Enter valid postal code')
        else:
            return postcode
        #
        # if len(postcode) == 6:
        #     if postcode[::2].isalpha() and postcode[1::2].isdigit():  # slicing with step
        #         return postcode
        #     else:
        #         raise forms.ValidationError('Enter valid postal code')


