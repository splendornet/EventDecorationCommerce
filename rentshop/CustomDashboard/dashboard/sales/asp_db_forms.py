# python imports
import datetime

# django imports
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2Widget, Select2MultipleWidget

# package import
from oscar.core.loading import get_class, get_model
from oscar.forms.widgets import DatePickerInput
from django.db.models import Count

# internal imports
from .constants import type_of_db
Partner = get_model('partner', 'Partner')
IndividualDB = get_model('partner', 'IndividualDB')
StockRecord = get_model('partner', 'StockRecord')

MultiDB = get_model('partner', 'MultiDB')

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductCategory = get_model('catalogue', 'ProductCategory')

class SalesASPDBForm(forms.Form):

    """
    Form to search asp
    """


    category = forms.ModelChoiceField(queryset=Category.objects.all(),required=False)
    type = forms.ChoiceField(label=_("Select ASP"),choices = type_of_db,required=False, widget=forms.Select(attrs={'onchange': 'get_type();'}))

class DBSearchForm(forms.Form):

    """
    Form to search db
    """
    cat_db = MultiDB.objects.all().values_list('category')
    type = forms.ChoiceField(label=_("Select ASP"),choices = type_of_db,required=False, widget= Select2Widget(attrs= {'onchange': 'get_type();'}))
    category = forms.ModelChoiceField(queryset=Category.objects.exclude(id__in = cat_db),required=False, widget= Select2Widget)


class SalesASPDBSearchForm(forms.Form):

    """
    Form to search saleaspdb
    """
    category = forms.ModelChoiceField(queryset=Category.objects.all(),required=False)
    type = forms.ChoiceField(label=_("Select ASP"),choices = type_of_db,required=False)

class IndividualDBModelForm(forms.ModelForm):
    cats = Category.objects.all()
    li = []
    cats = Category.objects.filter(id__in=li)
    cat_db = MultiDB.objects.all().values_list('category')
    category = forms.ModelChoiceField(queryset=Category.objects.exclude(id__in=cat_db),widget=Select2Widget(attrs={'onchange': 'get_vendors();'}))

    class Meta:
        model = IndividualDB
        fields = ('category', 'individual_asp')

        widgets = {
            'individual_asp' : Select2MultipleWidget,
        }

    def __init__(self, *args, **kwargs):

        super(IndividualDBModelForm, self).__init__(*args, **kwargs)
        vendors = Partner.objects.filter(users__is_active=True)
        self.fields['individual_asp'].queryset = vendors

        if self.instance.pk:
            # cat = Category.objects.get(id=self.instance.category.id)
            # prods = cat.product_set.all().values_list('stockrecords__partner')
            # vendors = Partner.objects.filter(id__in=prods, users__is_active = True)
            self.fields['category'].disabled = True
            self.fields['category'].required = False

    def clean_category(self):
        category = self.cleaned_data['category']
        if self.instance.pk:
            return self.instance.category

        return self.cleaned_data['category']

    def clean_individual_asp(self):
        individual_asp = self.cleaned_data.get('individual_asp', None)
        if not individual_asp or len(individual_asp) > 1:
            raise forms.ValidationError('You can add only one individual_asp')
        return self.cleaned_data.get('individual_asp', None)



class MultiDBModelForm(forms.ModelForm):
    cat_db = IndividualDB.objects.all().values_list('category')
    category = forms.ModelChoiceField(queryset=Category.objects.exclude(id__in = cat_db))


    class Meta:
        model = MultiDB
        fields = ('category', 'frontliener','backup1','backup2')

        widgets = {
            'frontliener' :Select2MultipleWidget,
            'backup1': Select2MultipleWidget,
            'backup2':Select2MultipleWidget,
        }

    def __init__(self, *args, **kwargs):

        super(MultiDBModelForm, self).__init__(*args, **kwargs)
        vendors = Partner.objects.filter(users__is_active=True)
        self.fields['frontliener'].queryset = vendors
        self.fields['backup1'].queryset = vendors
        self.fields['backup2'].queryset = vendors

        if self.instance.pk:
            cat = Category.objects.get(id=self.instance.category.id)
            prods = cat.product_set.all().values_list('stockrecords__partner')
            vendors = Partner.objects.filter(id__in=prods, users__is_active = True)
            self.fields['category'].disabled = True
            self.fields['category'].required = False


    def clean_category(self):
        category = self.cleaned_data['category']
        if self.instance.pk:
            return self.instance.category
        return self.cleaned_data['category']

    def clean_frontliener(self):
        frontliener = self.cleaned_data.get('frontliener',None)
        if not frontliener or len(frontliener) > 10:
            raise forms.ValidationError('You can add maximum 10 asp in frontliner list')
        return frontliener

    def clean_backup1(self):
        backup1 = self.cleaned_data.get('backup1',None)
        if not backup1 or len(backup1) > 10:
            raise forms.ValidationError('You can add maximum 10 asp in Back up 1 list')
        return backup1

    def clean_backup2(self):
        backup2 = self.cleaned_data.get('backup2',None)
        if not backup2 or len(backup2) > 10:
            raise forms.ValidationError('You can add maximum 10 asp in Back up 2 list')
        return backup2

    def clean(self):

        frontliener = self.cleaned_data.get('frontliener',None)
        backup1 = self.cleaned_data.get('backup1',None)
        backup2 = self.cleaned_data.get('backup2',None)

        if not frontliener or not backup1 or not backup2 or (len(set(frontliener).intersection(set(backup1))) !=0) or (len(set(frontliener).intersection(set(backup2))) !=0) or (len(set(backup2).intersection(set(backup1))) !=0):
            raise forms.ValidationError('Please select different asp in frontliner, backup1 and in backup2')




