from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from oscar.core.loading import get_class, get_model
from django_select2.forms import Select2Widget


CancellationCharges = get_model('order','CancellationCharges')

CHARGES_APPLY_CHOICES = (
        ('1', 'Before 1 Month'),
        ('2', 'Before 15 Days'),
        ('3', 'Before 5 Days'),
        ('4', 'On the Event Date'),
    )

class CancellationChargeSearchForm(forms.Form):
    charges_percentage = forms.CharField(required=False, max_length=100)
    apply_to = forms.ChoiceField(required=False, choices=CHARGES_APPLY_CHOICES)

class CancellationChargesModelForm(forms.ModelForm):
    apply_to = forms.ChoiceField(choices = CHARGES_APPLY_CHOICES, widget= Select2Widget)
    charges_percentage = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CancellationCharges
        fields = ['apply_to','charges_percentage']


    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['charges_percentage'].required=True

    def clean_percentage_charges(self):
        perc = self.cleaned_data['charges_percentage']

        if perc>100:
            return forms.ValidationEroor("please provide percentage less than 100")
        return perc

