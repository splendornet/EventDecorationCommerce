# django imports
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.flatpages.forms import FlatpageForm
from django.utils.translation import gettext_lazy as _
# from ckeditor.widgets import CKEditorWidget

# package import
from oscar.core.loading import get_class, get_model
from oscar.forms.widgets import DatePickerInput

# internal imports
Category = get_model('catalogue', 'Category')
CustomFlatPages = get_model('RentCore', 'CustomFlatPages')


class AccountSearchForm(forms.Form):

    order_number = forms.CharField(required=False)
    customer_name = forms.CharField(required=False)
    order_date = forms.DateField(required=False, widget=DatePickerInput)
    

class CustomFlatPagesSearchForm(forms.Form):

    title = forms.CharField(required=False)

class CustomFlatPagesForm(forms.Form):

    PAGE_TYPE_CHOICES = (
        ('0', 'Legal Documents'),
        ('1', 'Policies'),
        ('2', 'Terms and Conditions'),

    )

    type = forms.ChoiceField(label=_("Type"),choices = PAGE_TYPE_CHOICES,required=False, widget=forms.RadioSelect)



class CustomFlatPagesCreateForm(FlatpageForm):

    # content = forms.CharField(widget=CKEditorWidget(), required= False)

    class Meta:
        model = CustomFlatPages
        fields = ('url','title','page_type','content')

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        self.request = kwargs.pop('request', None)
        super(CustomFlatPagesCreateForm, self).__init__(*args, **kwargs)


        self.fields['page_type'].widget = forms.HiddenInput()

        self.fields['page_type'].required = False
        self.fields['title'].widget.attrs['readonly'] = 'True'
        self.fields['url'].widget.attrs['readonly'] = True
        self.fields['title'].required = False
        self.fields['url'].required = False




