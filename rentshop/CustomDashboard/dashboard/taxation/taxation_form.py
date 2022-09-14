# django imports
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

# package import
from oscar.core.loading import get_class, get_model

# internal imports
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
Taxation = get_model('catalogue', 'Taxation')


TAX_APPLY_CHOICES = (
        ('1', 'For all rental products'),
        ('2', 'For all selling products'),
        ('3', 'For all rent and sale products'),
        ('4', 'For all professional products'),

)


class TaxationSearchForm(forms.Form):

    tax_percentage = forms.CharField(required=False, max_length=100)
    apply_to = forms.ChoiceField(required=False,choices = TAX_APPLY_CHOICES)


# Developer: Smita Patil
# Date: 15-01-2021
# Changes as per composition and regular tax type
class TaxationModelForm(forms.ModelForm):

    apply_to = forms.ChoiceField(choices=TAX_APPLY_CHOICES, widget=forms.Select(attrs={'onchange': 'for_products_change();'}))
    tax_percentage = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sale_tax_percent = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Taxation
        fields = ('tax_percentage', 'apply_to', 'sale_tax_percent')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tax_percentage'].required = True
        self.fields['apply_to'].widget.attrs['disabled'] = True
        self.fields['apply_to'].required = False
        self.fields['apply_to'].widget.attrs['class'] = 'form-control'

    # def clean_tax_percentage(self):
    #     perc = self.cleaned_data['tax_percentage']
    #
    #     if perc>18:
    #         raise forms.ValidationError('Please provide tax percentage less than 18')
    #     return perc
    #
