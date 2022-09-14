# Django Imports
from django import forms
from django.core.validators import RegexValidator
from django.forms import formset_factory, inlineformset_factory

# Oscar Imports
from oscar.core.loading import get_class, get_model

CouponDistributor = get_model('offer', 'CouponDistributor')
PriceRangeModel = get_model('offer', 'PriceRangeModel')
Category = get_model('catalogue', 'Category')


class CouponDistributorForms(forms.ModelForm):
    full_name = forms.CharField(required=True, label='Full Name',
                                validators=[RegexValidator('^([A-Za-z_ ])+$', message='Enter a valid name.')],
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    cdn = forms.CharField(required=True, label='CDN',
                          validators=[RegexValidator('^([A-Za-z_ 0-9])+$', message='Enter a valid CDN')],
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    uin = forms.CharField(required=True, label='UIN',
                          validators=[RegexValidator('^([A-Za-z_ 0-9])+$', message='Enter a valid UIN')],
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.Textarea()
    email_id = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobile_number = forms.CharField(required=True, min_length=10, max_length=10,
                                    validators=[RegexValidator('^([0-9])+$', message='Enter a valid mobile number.')],
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    whatsapp_number = forms.CharField(required=True, min_length=10, max_length=10,
                                      validators=[RegexValidator('^([0-9])+$', message='Enter a valid whatsapp number.')],
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))
    aadhar_number = forms.CharField(required=True, min_length=12, max_length=12,
                                    validators=[RegexValidator('^([0-9])+$', message='Enter a valid aadhar number.')],
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    pan_number = forms.CharField(required=True, max_length=16,
                                 validators=[RegexValidator('^([A-Z0-9])+$', message='Enter a PAN number')],
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    account_holder_name = forms.CharField(required=True,
                                          validators=[RegexValidator('^([A-Za-z_ ])+$', message='Enter a valid account holder name.')],
                                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    bank_name = forms.CharField(required=True,
                                validators=[RegexValidator('^([A-Za-z_ ])+$', message='Enter a valid bank name.')],
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    bank_address = forms.Textarea()
    account_number = forms.CharField(required=True, max_length=30,
                                     validators=[RegexValidator('^([0-9])+$', message='Enter a valid account number.')],
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    account_type = forms.CharField(required=True, max_length=30,
                                   validators=[RegexValidator('^([A-Za-z_ ])+$', message='Enter a valid account type.')],
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    ifsc_code = forms.CharField(required=True, max_length=30,
                                validators=[RegexValidator('^([A-Z0-9])+$', message='Enter a IFSC Code')],
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CouponDistributor
        exclude = ['date_created', 'date_updated', 'is_deleted']


class DistributorSearchForm(forms.Form):
    name = forms.CharField(required=False)
    cdn = forms.CharField(required=False, label='CDN')
    whatsapp_number = forms.CharField(required=False)
    email_id = forms.CharField(required=False)


class PriceRangeForm(forms.ModelForm):

    class Meta:
        model = PriceRangeModel
        exclude = ['date_created', 'date_updated']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['price_rng'].widget.attrs['class'] = 'form-control'
        self.fields['discount_type'].widget.attrs['class'] = 'form-control'
        self.fields['discount'].widget.attrs['class'] = 'form-control'

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        discount_type = self.cleaned_data.get('discount_type')
        if discount < 0:
            raise forms.ValidationError('Discount cannot be negative')
        if discount_type and discount_type == 'Percentage':
            if discount > 100:
                raise forms.ValidationError('Discount percentage cannot be greater than 100')
        return discount

class PriceRangeSearchForm(forms.ModelForm):
    class Meta:
        model = PriceRangeModel
        fields = ('category', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False


PriceRangeFormsetExtra = inlineformset_factory(
   Category, model=PriceRangeModel, form=PriceRangeForm, extra=10, max_num=10
)