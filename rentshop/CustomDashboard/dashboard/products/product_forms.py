# python imports

# django imports
from django import forms

# packages imports
from oscar.core.loading import get_class, get_model

# internal imports
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')


class RateCardProductSearchForm(forms.Form):

    """
    Form to search product cards
    """

    TR_CHOICE = (
        ('', '--------'),
        ('1', 'Yes'),
        ('2', 'No'),
    )

    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)

    product = forms.ModelChoiceField(queryset=Product.objects.filter(product_cost_type='Multiple',is_deleted=False), required=False)
    product_upc = forms.CharField(max_length=100, required=False)
    transport_available = forms.ChoiceField(choices=TR_CHOICE, required=False)


class ProductCostEntriesModelForm(forms.ModelForm):

    class Meta:
        model = ProductCostEntries
        fields = (
            'product', 'product_upc', 'product_type',
            'quantity_from', 'quantity_to', 'requirement_day',
            'cost_incl_tax', 'transport_cost',
            'rent_quantity_from', 'rent_quantity_to', 'rent_requirement_day',
            'rent_cost_incl_tax', 'rent_transport_cost', 'remarks', 'rent_remarks'
        )

    def __init__(self, *args, **kwargs):

        """
        Form default init method
        :param args: default
        :param kwargs: default
        """

        base_product = kwargs.pop('base_product')

        super().__init__(*args, **kwargs)

        self.fields['product'].widget.attrs['class'] = 'form-control'

        self.fields['product'].queryset = Product.objects.filter(id=base_product,is_deleted=False)
        self.fields['product'].initial = Product.objects.filter(id=base_product,is_deleted=False).last()

        self.fields['product_upc'].widget.attrs['class'] = 'form-control'
        self.fields['product_type'].widget.attrs['class'] = 'form-control'
        self.fields['quantity_from'].widget.attrs['class'] = 'form-control form-control-valid-sale'
        self.fields['quantity_to'].widget.attrs['class'] = 'form-control form-control-valid-sale'
        self.fields['requirement_day'].widget.attrs['class'] = 'form-control'
        self.fields['cost_incl_tax'].widget.attrs['class'] = 'form-control'
        self.fields['transport_cost'].widget.attrs['class'] = 'form-control'

        self.fields['rent_quantity_from'].widget.attrs['class'] = 'form-control form-control-valid-rent'
        self.fields['rent_quantity_to'].widget.attrs['class'] = 'form-control form-control-valid-rent'
        self.fields['rent_requirement_day'].widget.attrs['class'] = 'form-control'
        self.fields['rent_cost_incl_tax'].widget.attrs['class'] = 'form-control'
        self.fields['rent_transport_cost'].widget.attrs['class'] = 'form-control'
        self.fields['remarks'].widget.attrs['class'] = 'form-control'
        self.fields['rent_remarks'].widget.attrs['class'] = 'form-control'

    def clean(self):

        quantity_from = self.cleaned_data.get('quantity_from')
        quantity_to = self.cleaned_data.get('quantity_to')

        rent_quantity_from = self.cleaned_data.get('rent_quantity_from')
        rent_quantity_to = self.cleaned_data.get('rent_quantity_to')

        if quantity_from and quantity_to and quantity_from > quantity_to:
            raise forms.ValidationError('Please add valid quantity')

        if rent_quantity_from and rent_quantity_to and rent_quantity_from > rent_quantity_to:
            raise forms.ValidationError('Please add valid quantity')

        transport_cost = self.cleaned_data.get('transport_cost')
        rent_transport_cost = self.cleaned_data.get('rent_transport_cost')
        product = self.cleaned_data.get('product')
        upc = self.cleaned_data.get('product_upc')
        obj = Product.objects.filter(upc__exact = upc)
        if obj:

            if rent_quantity_from != None and  obj.last().is_transporation_available and obj.last().product_class.name in ['Rent', 'Professional'] and not rent_transport_cost:
                raise forms.ValidationError('Please add rent transportation cost')

            if quantity_from != None and obj.last().is_transporation_available and obj.last().product_class.name == 'Sale' and not transport_cost:
                raise forms.ValidationError('Please add sale transportation cost')

            if rent_quantity_from != None and quantity_from != None and obj.last().is_transporation_available and obj.last().product_class.name == 'Rent Or Sale':
                if not rent_transport_cost and not transport_cost:
                    raise forms.ValidationError('Please add sale and rent transportation cost')

                elif not rent_transport_cost and transport_cost:
                    raise forms.ValidationError('Please add rent transportation cost')

                elif rent_transport_cost and not transport_cost:
                    raise forms.ValidationError('Please add sale transportation cost')

            if rent_quantity_from != None  and obj.last().is_transporation_available and obj.last().product_class.name == 'Rent Or Sale':
                if not rent_transport_cost:
                    raise forms.ValidationError('Please add rent transportation cost')


            if quantity_from != None and obj.last().is_transporation_available and obj.last().product_class.name == 'Rent Or Sale':
                if not transport_cost:
                    raise forms.ValidationError('Please add sale transportation cost')


        return self.cleaned_data

class FeaturedProductSearchForm(forms.Form):

    """
    Form to search featured product
    """

    category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=1), required=False)
    sub_category = forms.ModelChoiceField(queryset=Category.objects.filter(depth=2), required=False)

    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_deleted=False), required=False)
    product_upc = forms.CharField(max_length=100, required=False)
