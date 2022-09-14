# python imports
import datetime

# django imports
from django import forms
from django.utils.translation import gettext_lazy as _

# package import
from oscar.core.loading import get_class, get_model
from oscar.forms.widgets import DatePickerInput

# internal imports
VendorCalender = get_model('partner', 'VendorCalender')
Partner = get_model('partner', 'Partner')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')


class VendorSaleCalendarAddEvent(forms.ModelForm):

    """
    Form to store vendor calendar.
    """
    from_date = forms.DateField(label=_("Date from"), required=True, widget=DatePickerInput)
    to_date = forms.DateField(label=_("Date from"), required=True, widget=DatePickerInput)

    class Meta:
        model = VendorCalender
        fields = ('product', 'from_date', 'to_date', 'vendor',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(VendorSaleCalendarAddEvent, self).__init__(*args, **kwargs)
        self.fields['product'].widget.attrs['class'] = 'form-control'
        self.fields['to_date'].widget.attrs['class'] = 'form-control'
        self.fields['from_date'].widget.attrs['class'] = 'form-control'

    def clean(self):

        """
        Form clean method.
        :return: validation
        """

        from_date = self.cleaned_data.get('from_date', None)
        to_date = self.cleaned_data.get('to_date', None)
        product = self.cleaned_data.get('product', None)

        if from_date:
            if from_date < datetime.datetime.now().date():
                raise forms.ValidationError('Please select current date.')

        if (all([from_date, to_date]) and self.cleaned_data['from_date'] > self.cleaned_data['to_date']):
            raise forms.ValidationError(_("Your start date must be before your end date"))

        if product and from_date and to_date:

            q1 = VendorCalender.objects.filter(
                product=product, to_date__gte=from_date
            ).exclude(id=self.instance.id)

            q2 = VendorCalender.objects.filter(
                product=product, from_date__range=[from_date, to_date]
            ).exclude(id=self.instance.id)

            q3 = VendorCalender.objects.filter(
                product=product, to_date__range=[from_date, to_date]
            ).exclude(id=self.instance.id)

            if q1 or q2 or q3:
                raise forms.ValidationError(
                    'Product already booked on that date range.'
                )

        return self.cleaned_data


class SalesPrimeBucketSearchForm(forms.Form):

    """
    Form to search prime bucket
    """

    order_number = forms.CharField(max_length=100, required=False)


class SalesSearchForm(forms.Form):

    """
    Form to search vendor calendar.
    """

    product = forms.ModelChoiceField(required=False, queryset=Product.objects.filter(is_deleted = False))
    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)
    upc = forms.CharField(required=False, label=_("UPC"))
    vendor = forms.ModelChoiceField(required=False, queryset=Partner.objects.all(),label='ASP')
    from_date = forms.DateField(required=False, widget=DatePickerInput)
    to_date = forms.DateField(required=False, widget=DatePickerInput)

    def clean(self):

        date_from = self.cleaned_data.get('from_date', None)
        date_to = self.cleaned_data.get('to_date', None)
        if (all([date_from, date_to]) and self.cleaned_data['from_date'] > self.cleaned_data['to_date']):
            raise forms.ValidationError(_("Your start date must be before your end date"))
        return self.cleaned_data



