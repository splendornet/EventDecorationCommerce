# python imports
import datetime

# django imports
from django import forms
from django.utils.translation import gettext_lazy as _

# package import
from oscar.core.loading import get_class, get_model
from oscar.forms.widgets import DatePickerInput
from django.db.models import Count

# internal imports
Partner = get_model('partner', 'Partner')
IndividualDB = get_model('partner', 'IndividualDB')
StockRecord = get_model('partner', 'StockRecord')

MultiDB = get_model('partner', 'MultiDB')

CategoriesWiseFilterValue = get_model('catalogue', 'CategoriesWiseFilterValue')
CategoriesWisePriceFilter = get_model('catalogue', 'CategoriesWisePriceFilter')
Category = get_model('catalogue', 'Category')
Attribute = get_model('catalogue', 'Attribute')
from django.forms import formset_factory, inlineformset_factory


class CategoryFilterSearchForm(forms.Form):

    """
    Form to search category
    """
    category = forms.ModelChoiceField(queryset=Category.objects.all(),required=False)

class CategoryFilterModelForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())


    filter_names = forms.MultipleChoiceField()

    class Meta:

        model = CategoriesWiseFilterValue
        fields = ('category', 'filter_names')

    def __init__(self, *args,**kwargs):
        super(CategoryFilterModelForm, self).__init__(*args, **kwargs)
        VALUE_CHOICES = []
        distinct_attribute = Attribute.objects.distinct('attribute')
        for att in distinct_attribute:
            VALUE_CHOICES.append((att.attribute, att.attribute))
        self.fields['category'].widget.attrs['disabled'] = True
        self.fields['filter_names'].choices = VALUE_CHOICES
        self.fields['category'].required = False
        self.fields['filter_names'].required = False
        self.fields['filter_names'].widget.attrs['class'] = 'form-control'

class PriceFilterForm(forms.ModelForm):

    class Meta:
        model = CategoriesWisePriceFilter
        exclude = ['range']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['from_value'].widget.attrs['class'] = 'form-control'
        self.fields['to_value'].widget.attrs['class'] = 'form-control'

    def clean(self):

        from_value = self.cleaned_data.get('from_value', False)
        to_value = self.cleaned_data.get('to_value', False)

        print('from',from_value,to_value)
        if from_value and to_value:

            if from_value and to_value and from_value > to_value:
                raise forms.ValidationError('Please give to figure greater than from')


class PriceFilterSearchForm(forms.ModelForm):
    class Meta:
        model = CategoriesWisePriceFilter
        fields = ('category', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False


PriceFilterFormsetExtra = inlineformset_factory(
   Category, model=CategoriesWisePriceFilter, form=PriceFilterForm, extra=10, max_num=10
)

