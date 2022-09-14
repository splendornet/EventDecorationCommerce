# python imports

# django imports
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _

# 3rd party imports
from oscar.core.loading import get_classes, get_model

# internal imports
from .forms import *


Product = get_model('catalogue', 'Product')
ComboProducts = get_model('catalogue', 'ComboProducts')
StockRecord = get_model('partner', 'StockRecord')
Category = get_model('catalogue', 'Category')
ProductCategory = get_model('catalogue', 'ProductCategory')
CustomProductCategoryForm = get_class('dashboard.forms','CustomProductCategoryForm')
ComboProductSetForm = get_class('dashboard.forms', 'ComboProductSetForm')
CustomProduComboProductSetFormctImageForm = get_class('dashboard.forms','CustomProductImageForm')
CustomAttributeForm = get_class('dashboard.forms','CustomAttributeForm')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')


(StockRecordForm) = get_classes('dashboard.catalogue.forms', ('StockRecordForm',))

BaseStockRecordFormSet = inlineformset_factory(Product, StockRecord, form=CustomStockRecordForm)
BaseProductCategoryFormSet = inlineformset_factory(Product, ProductCategory, form=CustomProductCategoryForm, extra=1, max_num=1, min_num=1)
BaseComboProductCategoryFormSet = inlineformset_factory(Product, ProductCategory, form=ComboProductCategoryForm, extra=1, max_num=1, min_num=1)
BaseProductImageFormSet = inlineformset_factory(Product, ProductImage, form=CustomProductImageForm, extra=100, can_delete=False)
BaseComboProductSet = inlineformset_factory(
    Product, ComboProducts, form=ComboProductSetForm,
    fk_name='combo_product', fields='__all__', extra=8, can_delete=False
)
BaseAttributeSet = inlineformset_factory(
    Product, Attribute_Mapping, form=CustomAttributeForm,
    fk_name='product', extra=20, can_delete=False
)


class ComboProductFormSet(BaseComboProductSet):

    """

    """

    def __init__(self, product_class, user, *args, **kwargs):

        self.user = user
        self.product_class = product_class

        super().__init__(*args, **kwargs)

        if user.is_superuser:
            for form in self.forms:
                form.fields['product'].queryset = Product.objects.filter(is_combo_product=True,is_deleted=False)

        if user.is_staff and not user.is_superuser:
            for form in self.forms:
                vendor_user = Partner.objects.filter(users=self.user).last()
                vendor_stock = StockRecord.objects.filter(partner=vendor_user).values_list('product__id', flat=True)
                form.fields['product'].queryset = Product.objects.filter(is_combo_product=True, id__in=vendor_stock,is_deleted=False)


class ComboStockRecordFormSet(BaseStockRecordFormSet):

    """
    Oscar stock record extended method to store stock-record.
    """

    def __init__(self, product_class, user, *args, **kwargs):

        self.user = user
        self.require_user_stockrecord = not user.is_staff
        self.product_class = product_class

        is_vendor = self.user.groups.filter(name='Vendor').exists()

        BaseStockRecordFormSet.extra = 1
        BaseStockRecordFormSet.max_num = 1
        BaseStockRecordFormSet.min_num = 1

        if is_vendor:
            BaseStockRecordFormSet.extra = 1
            BaseStockRecordFormSet.max_num = 1
            BaseStockRecordFormSet.min_num = 1

        if not user.is_staff and \
                'instance' in kwargs and \
                'queryset' not in kwargs:
            kwargs.update({
                'queryset': StockRecord.objects.filter(product=kwargs['instance'],
                                                       partner__in=user.partners.all())
            })

        super().__init__(*args, **kwargs)

        for form in self.forms:
            if product_class == 'Service':
                self.forms[0].empty_permitted = True
            else:
                self.forms[0].empty_permitted = False

        self.set_initial_data()

    def set_initial_data(self):

        if self.require_user_stockrecord:
            try:
                user_partner = self.user.partners.get()
            except (exceptions.ObjectDoesNotExist,
                    exceptions.MultipleObjectsReturned):
                pass
            else:
                partner_field = self.forms[0].fields.get('partner', None)
                if partner_field and partner_field.initial is None:
                    partner_field.initial = user_partner

    def _construct_form(self, i, **kwargs):

        kwargs['product_class'] = self.product_class
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)

    def clean(self):

        if any(self.errors):
            print(any(self.erroos))
            return

        if self.require_user_stockrecord:
            stockrecord_partners = set([form.cleaned_data.get('partner', None)
                                        for form in self.forms])
            user_partners = set(self.user.partners.all())
            if not user_partners & stockrecord_partners:
                raise exceptions.ValidationError(_("At least one stock record must be set to a partner thatyou're " \
                                                   " associated with."))


class CustomStockRecordFormSet(BaseStockRecordFormSet):

    """
    Oscar stock record extended method to store stock-record.
    """

    def __init__(self, product_class, user, *args, **kwargs):

        self.user = user
        self.require_user_stockrecord = not user.is_staff
        self.product_class = product_class

        is_vendor = self.user.groups.filter(name='Vendor').exists()

        BaseStockRecordFormSet.extra = 1
        BaseStockRecordFormSet.max_num = 1
        BaseStockRecordFormSet.min_num = 1

        if is_vendor:
            BaseStockRecordFormSet.extra = 1
            BaseStockRecordFormSet.max_num = 1
            BaseStockRecordFormSet.min_num = 1

        if not user.is_staff and \
                'instance' in kwargs and \
                'queryset' not in kwargs:
            kwargs.update({
                'queryset': StockRecord.objects.filter(product=kwargs['instance'],
                                                       partner__in=user.partners.all())
            })

        super().__init__(*args, **kwargs)

        for form in self.forms:
            if product_class == 'Service':
                self.forms[0].empty_permitted = True
            else:
                self.forms[0].empty_permitted = False

        self.set_initial_data()

    def set_initial_data(self):
        if self.require_user_stockrecord:
            try:
                user_partner = self.user.partners.get()
            except (exceptions.ObjectDoesNotExist,
                    exceptions.MultipleObjectsReturned):
                pass
            else:
                partner_field = self.forms[0].fields.get('partner', None)
                if partner_field and partner_field.initial is None:
                    partner_field.initial = user_partner

    def _construct_form(self, i, **kwargs):

        kwargs['product_class'] = self.product_class
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)

    def clean(self):

        if any(self.errors):
            print("errors###",any(self.errors), self.errors)
            return

        if self.require_user_stockrecord:
            print("comboo", self.require_user_stockrecord)
            stockrecord_partners = set([form.cleaned_data.get('partner', None)
                                        for form in self.forms])
            user_partners = set(self.user.partners.all())
            if not user_partners & stockrecord_partners:
                raise exceptions.ValidationError(_("At least one stock record must be set to a partner thatyou're "\
                                                   " associated with."))


class ProductCategoryFormSet(BaseProductCategoryFormSet):

    """
    Oscar category extended formset to store product category.
    """

    def __init__(self, product_class, user, *args, **kwargs):
        # This function just exists to drop the extra arguments
        self.can_delete = False
        super().__init__(*args, **kwargs)

    def clean(self):

        if not self.instance.is_child and self.get_num_categories() == 0:
            raise forms.ValidationError(
                _("Stand-alone and parent products "
                  "must have at least one category"))
        if self.instance.is_child and self.get_num_categories() > 0:
            raise forms.ValidationError(
                _("A child product should not have categories"))

    def get_num_categories(self):
        num_categories = 0
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if (hasattr(form, 'cleaned_data')
                    and form.cleaned_data.get('category', None)
                    and not form.cleaned_data.get('DELETE', False)):
                num_categories += 1
            return num_categories


class ComboProductCategoryFormSet(BaseComboProductCategoryFormSet):

    """
    Oscar category extended formset to store product category.
    """

    def __init__(self, product_class, user, *args, **kwargs):
        # This function just exists to drop the extra arguments
        self.can_delete = False
        super().__init__(*args, **kwargs)

    def clean(self):

        if not self.instance.is_child and self.get_num_categories() == 0:
            raise forms.ValidationError(
                _("Stand-alone and parent products "
                  "must have at least one category"))
        if self.instance.is_child and self.get_num_categories() > 0:
            raise forms.ValidationError(
                _("A child product should not have categories"))

    def get_num_categories(self):
        num_categories = 0
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if (hasattr(form, 'cleaned_data')
                    and form.cleaned_data.get('category', None)
                    and not form.cleaned_data.get('DELETE', False)):
                num_categories += 1
            return num_categories


class CustomProductImageFormSet(BaseProductImageFormSet):

    """
    Oscar image extended formset.
    """

    def __init__(self, product_class, user, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AttributeFormSet(BaseAttributeSet):
    def __init__(self, product_class, user, *args, **kwargs):
        super().__init__(*args, **kwargs)