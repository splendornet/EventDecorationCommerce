# django imports
from django.contrib import admin

# 3rdp party imports
from treebeard.admin import TreeAdmin
from .mp_admin import CustomTreeAdmin
from treebeard.forms import movenodeform_factory
from oscar.core.loading import get_model

# internal imports
AttributeOption = get_model('catalogue', 'AttributeOption')
AttributeOptionGroup = get_model('catalogue', 'AttributeOptionGroup')
Category = get_model('catalogue', 'Category')
Option = get_model('catalogue', 'Option')
Product = get_model('catalogue', 'Product')
ComboProducts = get_model('catalogue', 'ComboProducts')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductClass = get_model('catalogue', 'ProductClass')
ProductImage = get_model('catalogue', 'ProductImage')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')
PremiumProducts = get_model('catalogue', 'PremiumProducts')
ComboProductsMaster = get_model('catalogue', 'ComboProductsMaster')
ComboProductsMasterProducts = get_model('catalogue', 'ComboProductsMasterProducts')
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')

StockRecord = get_model('partner', 'StockRecord')
Attribute = get_model('catalogue', 'Attribute')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')
AdvancedPayPercentage = get_model('catalogue', 'AdvancedPayPercentage')
Taxation = get_model('catalogue', 'Taxation')
FilterValues = get_model('catalogue', 'FilterValues')
CategoriesWiseFilterValue = get_model('catalogue', 'CategoriesWiseFilterValue')
CategoriesWisePriceFilter = get_model('catalogue', 'CategoriesWisePriceFilter')

from .forms import *

class ComboProductsAdmin(admin.ModelAdmin):

    list_display = ('combo_product', 'product',)


class AttributeInline(admin.TabularInline):

    """
    Admin in-line product attribute class.
    """

    model = ProductAttributeValue


class ProductRecommendationInline(admin.TabularInline):

    """
    Admin in-line product recommendation class.
    """

    model = ProductRecommendation
    fk_name = 'primary'
    raw_id_fields = ['primary', 'recommendation']


class CategoryInline(admin.TabularInline):

    """
    Admin class to display product categories.
    """

    model = ProductCategory
    extra = 1


class ProductAttributeInline(admin.TabularInline):

    """
    Admin class to display product attribute.
    """

    model = ProductAttribute
    extra = 2


class ProductClassAdmin(admin.ModelAdmin):

    """
    Admin class to product classes.
    """

    list_display = ('name', 'requires_shipping', 'track_stock')
    inlines = [ProductAttributeInline]


class ProductAdmin(admin.ModelAdmin):

    """
    Admin class to display products list.
    """

    date_hierarchy = 'date_created'
    list_display = ('get_title', 'category_list', 'product_price', 'date_created')
    list_filter = ['product_class', 'is_approved']
    raw_id_fields = ['parent']
    inlines = [AttributeInline, CategoryInline, ProductRecommendationInline]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ['upc', 'title', 'is_approved']

    def category_list(self, obj):
        
        return "\n".join([p.name for p in obj.categories.all()])

    def product_price(self, obj):

        price = None
        stock = StockRecord.objects.filter(product=obj)
        if stock:
            stock_price = stock.last()
            price = str(stock_price.price_excl_tax)

        return price

    def get_queryset(self, request):
        qs = super(ProductAdmin, self).get_queryset(request)
        return (
            qs.select_related('product_class', 'parent')
            .prefetch_related(
                'attribute_values',
                'attribute_values__attribute'
            )
        )


class ProductAttributeAdmin(admin.ModelAdmin):

    """
    Admin class to display product attributes.
    """

    list_display = ('name', 'code', 'product_class', 'type')
    prepopulated_fields = {"code": ("name", )}


class OptionAdmin(admin.ModelAdmin):

    """
    Product options admin.
    """

    pass


class ProductAttributeValueAdmin(admin.ModelAdmin):

    """
    Admin class to display product attributes.
    """

    list_display = ('product', 'attribute', 'value')


class AttributeOptionInline(admin.TabularInline):

    """
    Admin in-line class to display attributes options.
    """

    model = AttributeOption


class AttributeOptionGroupAdmin(admin.ModelAdmin):

    """
    Admin class of attributes options group
    """

    list_display = ('name', 'option_summary')
    inlines = [AttributeOptionInline, ]


class CategoryAdmin(CustomTreeAdmin):

    """
    Tree bird admin category class.
    """

    search_fields = ('name', 'slug',)
    list_filter = ('name', 'slug',)
    form = movenodeform_factory(Category)
    list_display = ('name', 'slug', 'path', 'id', 'master_sequence')


class ProductImageAdmin(admin.ModelAdmin):

    """
    Product image admin model.
    """

    list_display = ('product','img_sequence', 'original', 'is_dp_image')
    ordering = ['img_sequence']


class PremiumProductsAdmin(admin.ModelAdmin):

    list_display = ('category',)
    change_form_template = 'admin/premiumproduct_form.html'
    filter_horizontal = ('product',)

    form = AdminPremiumProductsForm

class AttributeMappingAdmin(admin.ModelAdmin):

    list_display = ('product', 'attribute','value')

class AdvancedPayPercentageAdmin(admin.ModelAdmin):

    list_display = ('apply_to','advance_payment_percentage', )

class TaxPercentageAdmin(admin.ModelAdmin):

    list_display = ('apply_to','tax_percentage','sale_tax_percent' )

class FilterValueAdmin(admin.ModelAdmin):

    list_display = ('filter_name', )

class CategoriesWiseFilterValueAdmin(admin.ModelAdmin):

    list_display = ('category', )

class CategoriesWisePriceFilterAdmin(admin.ModelAdmin):

    list_display = ('category', 'from_value', 'to_value', 'range')


admin.site.register(ProductClass, ProductClassAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(AttributeOptionGroup, AttributeOptionGroupAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductCategory)
admin.site.register(ComboProducts, ComboProductsAdmin)
admin.site.register(PremiumProducts,PremiumProductsAdmin)
admin.site.register(ComboProductsMaster)
admin.site.register(ComboProductsMasterProducts)
admin.site.register(ProductCostEntries)
admin.site.register(Attribute)
admin.site.register(Attribute_Mapping,AttributeMappingAdmin)
admin.site.register(AdvancedPayPercentage,AdvancedPayPercentageAdmin)
admin.site.register(Taxation,TaxPercentageAdmin)
admin.site.register(FilterValues,FilterValueAdmin)
admin.site.register(CategoriesWiseFilterValue,CategoriesWiseFilterValueAdmin)
admin.site.register(CategoriesWisePriceFilter,CategoriesWisePriceFilterAdmin)

