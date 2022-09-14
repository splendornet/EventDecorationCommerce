# django imports
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

# package import
from oscar.core.loading import get_class, get_model

# internal imports
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
AdvancedPayPercentage = get_model('catalogue', 'AdvancedPayPercentage')


PERCENTAGE_APPLY_CHOICES = (
        ('1', 'For all rental products'),
        ('2', 'For all selling products'),
        ('3', 'For all rent and sale products'),
        ('4', 'For all professional products'),

    )


class PercentageSearchForm(forms.Form):

    advance_payment_percentage = forms.CharField(required=False, max_length=100)
    apply_to = forms.ChoiceField(required=False,choices = PERCENTAGE_APPLY_CHOICES)

class PercentageModelForm(forms.ModelForm):

    apply_to = forms.ChoiceField(choices=PERCENTAGE_APPLY_CHOICES, widget=forms.Select(attrs={'onchange': 'for_products_change();'}))
    advance_payment_percentage = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sale_advance_payment_percentage = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = AdvancedPayPercentage
        fields = ('advance_payment_percentage', 'apply_to','sale_advance_payment_percentage',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['advance_payment_percentage'].required = True
        self.fields['apply_to'].widget.attrs['disabled'] = True
        self.fields['apply_to'].required = False
        self.fields['apply_to'].widget.attrs['class'] = 'form-control'


    def clean_advance_payment_percentage(self):
        perc = self.cleaned_data['advance_payment_percentage']

        if perc<0 or perc>100:
            raise forms.ValidationError('Please provide advance payment percentage in range 0 to 100')
        return perc
