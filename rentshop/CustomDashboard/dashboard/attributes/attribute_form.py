# django imports
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.forms import formset_factory
from django.forms.models import modelform_factory, inlineformset_factory,modelformset_factory

# package import
from oscar.core.loading import get_class, get_model

# internal imports

Attribute = get_model('catalogue', 'Attribute')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')


class AttributeSearchForm(forms.Form):

    attribute = forms.CharField(required=False, max_length=100)

class AttributeModelForm(forms.ModelForm):

    attribute = forms.CharField(required=False, max_length=100)

    class Meta:
        model = Attribute
        fields = ('attribute','value')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        super(AttributeModelForm, self).__init__(*args, **kwargs)
        self.fields['attribute'].widget.attrs['class'] = 'product_attribute'
        self.fields['value'].widget.attrs['class'] = 'form-control'

        self.fields['attribute'].requried = False



AttributeFormsetExtra = formset_factory(
   AttributeModelForm,extra=10,
)

