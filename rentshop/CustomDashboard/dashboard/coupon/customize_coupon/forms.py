# Django Imports
from django import forms
from django.core.validators import RegexValidator
from django.forms import formset_factory, inlineformset_factory
from django.core.validators import RegexValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.forms import inlineformset_factory
import datetime
# Oscar Imports
from oscar.core.loading import get_class, get_model
from oscar.apps.dashboard.ranges.forms import RangeForm
from oscar.apps.dashboard.vouchers.forms import VoucherForm, VoucherSetForm, VoucherSearchForm
from oscar.forms.widgets import DateTimePickerInput, ImageInput

CouponDistributor = get_model('offer', 'CouponDistributor')
CustomizeCouponModel = get_model('offer', 'CustomizeCouponModel')
Category = get_model('catalogue', 'Category')
PriceRangeModel = get_model('offer', 'PriceRangeModel')
Range = get_model('offer', 'Range')
Benefit = get_model('offer', 'Benefit')
Voucher = get_model('voucher', 'Voucher')


class CustomizeCouponModelForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        widget=DateTimePickerInput(),
        label=_("Start datetime"))
    end_datetime = forms.DateTimeField(
        widget=DateTimePickerInput(),
        label=_("End datetime"))

    class Meta:
        model = CustomizeCouponModel
        fields = ('category', 'start_datetime', 'end_datetime','coupon_count')

    def __init__(self, *args, **kwargs):
        p_obj = PriceRangeModel.objects.distinct('category').values_list('category__id', flat=True)
        c_obj = Category.objects.filter(id__in=p_obj)
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].queryset = c_obj
        self.fields['coupon_count'].initial = 1
        self.fields['coupon_count'].required = False

    def clean(self):
        cleaned_data = super(CustomizeCouponModelForm, self).clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        if start_datetime and end_datetime and end_datetime < start_datetime:
            raise forms.ValidationError(_("The start date must be before the"
                                          " end date"))
        return cleaned_data




class UINMultipleChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.uin

class CustomizeCouponRangeForm(RangeForm):

    """
    Offer range form oscar extended.
    """

    p_obj = PriceRangeModel.objects.distinct('category').values_list('category__id', flat=True)
    c_obj = Category.objects.filter(id__in = p_obj)
    coupon_distibutor = UINMultipleChoiceField(queryset = CouponDistributor.objects.all())

    class Meta:
        model = Range
        fields = [
            'description', 'coupon_distibutor',
        ]

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(CustomizeCouponRangeForm, self).__init__(*args, **kwargs)
        self.fields['description'].label = "Terms and Condition"


class CustomizeVoucherForm(forms.ModelForm):

    """
    Oscar voucher form extended.
    """
    start_datetime = forms.DateTimeField(initial=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        widget=DateTimePickerInput(),
        label=_("Start datetime"))
    end_datetime = forms.DateTimeField(initial=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        widget=DateTimePickerInput(),
        label=_("End datetime"))

    class Meta:
        model = Voucher
        fields = (
            'usage', 'code','start_datetime','end_datetime',
        )
        exclude = ('name','benefit_type','benefit_value', 'benefit_range')

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """
        super(CustomizeVoucherForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['class'] = 'form-control'
        self.fields['start_datetime'].widget =  forms.HiddenInput()
        self.fields['end_datetime'].widget =  forms.HiddenInput()
        # self.fields['state_datetime'].initial =  datetime.datetime.now()
        # self.fields['end_datetime'].initial =  datetime.datetime.now() + datetime.timedelta(1)
        self.fields['code'].widget =  forms.HiddenInput()
        self.fields['code'].required =  False






CustomizeCouponModelFormsetExtra = inlineformset_factory(Range,model= CustomizeCouponModel, form = CustomizeCouponModelForm,  extra=10, max_num=10,can_delete=False,)


class CustomizeVoucherSearchForm(forms.Form):
    cdn = forms.CharField(required=False, label=_("CDN"))
    uin = forms.CharField(required=False, label=_("UIN"))
    name = forms.CharField(required=False, label=_("Name"))
    code = forms.CharField(required=False, label=_("Code"))

