# django imports
from django import forms
from django.forms import formset_factory
from django.forms.models import modelform_factory, inlineformset_factory
from django_select2.forms import Select2Widget

# package import
from oscar.core.loading import get_class, get_model

# internal imports
Product = get_model('catalogue', 'Product')

Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
Manage_Menu = get_model('HeaderMenu', 'Manage_Menu')
ManageMenuMasterProducts = get_model('HeaderMenu', 'ManageMenuMasterProducts')
Admin_Header = get_model('HeaderMenu', 'Admin_Header')
ExhibitionOffers = get_model('HeaderMenu', 'ExhibitionOffers')
ExhibitionOffersCategory = get_model('HeaderMenu', 'ExhibitionOffersCategory')
Category = get_model('catalogue', 'Category')


class ManageMenuSearchForm(forms.Form):

    """
    Form to search manage menu
    """

    header_menu = forms.ModelChoiceField(queryset = Admin_Header.objects.filter(title__in = ["Corporate Offers"]),required=False, widget=Select2Widget)
    offer_title = forms.CharField(required=False, max_length=100)



class ManageMenuMasterProductsModelForm(forms.ModelForm):

    """
    Product model form
    """

    class Meta:
        model = ManageMenuMasterProducts
        fields = ('manage_menu', 'manage_product',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(ManageMenuMasterProductsModelForm, self).__init__(*args, **kwargs)
        self.fields['manage_product'].widget.attrs['class'] = 'manage_product'
        self.fields['manage_product'].queryset = Product.objects.filter(is_deleted=False)




ProductFormsetExtra = inlineformset_factory(
    Manage_Menu,
    ManageMenuMasterProducts, ManageMenuMasterProductsModelForm,
    extra=10,
)


class ManagerMenuMasterModelForm(forms.ModelForm):
    header_menu = forms.ModelChoiceField(Admin_Header.objects.filter(title__in = ["Corporate Offers"]))
    offer_title = forms.CharField(max_length=200, required=True)


    class Meta:
        model = Manage_Menu
        fields = (
            'header_menu', 'offer_title',

        )

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(ManagerMenuMasterModelForm, self).__init__(*args, **kwargs)
        self.fields['offer_title'].widget.attrs['class'] = 'form-control'




class ManageMenuModelForm(forms.ModelForm):

    header_menu = forms.ModelChoiceField(Admin_Header.objects.filter(title = "Corporate Offers"))
    offer_title = forms.CharField(max_length=200, required=True)

    class Meta:
        model = Manage_Menu
        fields = ('header_menu', 'offer_title', 'product',)

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(ManageMenuModelForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_deleted=False)
        self.fields['offer_title'].widget.attrs['class'] = 'form-control'


class ExhibitionOffersModelForm(forms.ModelForm):
    header_menu = forms.ModelChoiceField(Admin_Header.objects.filter(title__in = ["Exhibitions Offers"]), widget=Select2Widget)


    class Meta:
        model = ExhibitionOffers
        fields = (
            'header_menu',

        )

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """

        super(ExhibitionOffersModelForm, self).__init__(*args, **kwargs)

class ExhibitionOffersCategoryModelForm(forms.ModelForm):


    """
    Product model form
    """

    class Meta:
        model = ExhibitionOffersCategory
        fields = ('manage_menu', 'manage_category',)
        widget = {
            'manage_category': Select2Widget,
        }

    def __init__(self, *args, **kwargs):

        """
        Form default init method.
        :param args: default
        :param kwargs: default
        """



        super(ExhibitionOffersCategoryModelForm, self).__init__(*args, **kwargs)
        self.fields['manage_category'].widget.attrs['class'] = 'manage_category'
        self.fields['manage_category'].queryset = Category.objects.filter(depth=1)


CategoryFormsetExtra = inlineformset_factory(
    ExhibitionOffers,
    ExhibitionOffersCategory, ExhibitionOffersCategoryModelForm,
    extra=10,
)