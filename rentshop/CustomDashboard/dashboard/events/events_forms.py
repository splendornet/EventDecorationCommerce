# python imports
import datetime

# django imports
from django import forms

# packages imports
from oscar.core.loading import get_class, get_model
from oscar.forms.widgets import DatePickerInput, TimePickerInput

# internal imports
VendorCalender = get_model('partner', 'VendorCalender')
Product = get_model('catalogue', 'Product')


class AdminCalendarAddEvent(forms.ModelForm):

    """
    Form to store vendor calendar.
    """
    from_date = forms.DateField(label="Date from", required=True, widget=DatePickerInput)
    to_date = forms.DateField(label="Date from", required=True, widget=DatePickerInput)

    class Meta:
        model = VendorCalender
        fields = ('product', 'from_date', 'to_date', 'vendor',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        super(AdminCalendarAddEvent, self).__init__(*args, **kwargs)
        products = Product.objects.filter(is_deleted = False, is_approved = 'Approved')

        self.fields['from_date'].widget.attrs['class'] = 'form-control'
        self.fields['to_date'].widget.attrs['class'] = 'form-control'
        self.fields['vendor'].widget.attrs['class'] = 'form-control'
        self.fields['product'].widget.attrs['class'] = 'form-control'
        self.fields['product'].queryset = products
        self.fields['product'].required = True

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
            raise forms.ValidationError("Your start date must be before your end date")

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
