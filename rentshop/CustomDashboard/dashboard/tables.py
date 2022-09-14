from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ungettext_lazy
from django_tables2 import A, Column, LinkColumn, TemplateColumn
from oscar.apps.dashboard.users.tables import UserTable
from django.utils.safestring import mark_safe


from oscar.core.loading import get_class, get_model

DashboardTable = get_class('dashboard.tables', 'DashboardTable')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
AttributeOptionGroup = get_model('catalogue', 'AttributeOptionGroup')


class CustomCheckboxHeader(TemplateColumn):

    """
    Table two extended method to override header column.
    """

    @property
    def header(self):
        return mark_safe('<input type="checkbox" id="master_checkbox"/>')


class CustomUserCheckboxHeader(TemplateColumn):

    """
    Table two extended method to override header column.
    """

    @property
    def header(self):
        return mark_safe('<input type="checkbox" id="master_user_checkbox"/>')


class CustomCategotyCheckboxHeader(TemplateColumn):

    """
    Table two extended method to override header column.
    """

    @property
    def header(self):
        return mark_safe('<input type="checkbox" id="master_category_checkbox"/>')


class CustomCategoryTable(DashboardTable):
    """
    Oscar method to display category table.
    """

    check = CustomCategotyCheckboxHeader(
        template_name='dashboard/catalogue/tables/category_row_checkbox.html',
        verbose_name=' ', orderable=False
    )
    name = LinkColumn('dashboard:catalogue-category-update', args=[A('pk')])

    show_on_frontside = TemplateColumn(
        verbose_name=_('Show on frontside'),
        template_name='dashboard/catalogue/product_show_on_frontside.html',
        orderable=False,
    )

    # description = TemplateColumn(
    #     verbose_name=_('Descriptionss'),
    #     template_name='dashboard/catalogue/product_category.html',
    #     orderable=False,
    # )

    # description = TemplateColumn(
    #     template_code='{{ record.description|default:""|striptags'
    #                   '|cut:"&nbsp;"|truncatewords:6 }}'
    # )
    num_children = LinkColumn(
        'dashboard:catalogue-category-detail-list', args=[A('pk')],
        verbose_name=mark_safe(_('Number of child categories')),
        accessor='get_num_children',
        orderable=False
    )
    actions = TemplateColumn(
        template_name='dashboard/catalogue/category_row_actions.html',
        orderable=False
    )

    icon = "sitemap"
    caption = ungettext_lazy("%s Category", "%s Categories")

    class Meta(DashboardTable.Meta):
        model = Category
        fields = ('name', 'show_on_frontside')
        sequence = ('check',)


class CustomProductTable(DashboardTable):

    """
    Oscar extended product table.
    """

    title = TemplateColumn(
        verbose_name=_('Title'),
        template_name='dashboard/catalogue/product_row_title.html',
        order_by='title', accessor=A('title')
    )

    image = TemplateColumn(
        verbose_name=_('Image'),
        template_name='dashboard/catalogue/product_row_image.html',
        orderable=False
    )

    product_class = Column(
        verbose_name=_('Product type'),
        accessor=A('product_class'),
        order_by='product_class__name'
    )

    # product_cost_type = Column(
    #     verbose_name=_('Product Cost type'),
    #     accessor=A('product_cost_type'),
    #     # order_by='product_class__name'
    # )

    variants = CustomCheckboxHeader(
        template_name='dashboard/catalogue/product_check_box.html',
        orderable=False
    )

    stock_records = TemplateColumn(
        verbose_name=_('Stock records'),
        template_name='dashboard/catalogue/product_row_stockrecords.html',
        orderable=False
    )

    vendor = TemplateColumn(
        verbose_name=_('ASP'),
        template_name='dashboard/catalogue/tables/product_row_vendor.html',
        orderable=False
    )

    category = TemplateColumn(
        verbose_name=_('Category'),
        template_name='dashboard/catalogue/tables/product_row_category.html',
        orderable=False
    )

    actions = TemplateColumn(
        verbose_name=_('Actions'),
        template_name='dashboard/catalogue/product_row_actions.html',
        orderable=False
    )

    Approved = TemplateColumn(
        verbose_name=_('Is Approved'),
        template_name='dashboard/catalogue/product_status.html',
        orderable=False,
    )

    is_combo_product = TemplateColumn(
        verbose_name=_('Is Combo'),
        template_name='dashboard/catalogue/is_combo_product.html',
        orderable=False,
    )

    icon = "sitemap"

    class Meta(DashboardTable.Meta):

        model = Product
        fields = ('upc', 'date_updated')
        sequence = (
            'variants', 'title', 'upc', 'image', 'product_class',
            'stock_records', 'vendor', 'category', '...', 'date_updated', 'actions'
        )
        order_by = '-date_updated'


class CategoryTable(DashboardTable):

    """
    Oscar extended category table.
    """

    name = LinkColumn('dashboard:catalogue-category-update', args=[A('pk')])

    description = TemplateColumn(
        template_code='{{ record.description|default:""|striptags|cut:"&nbsp;"|truncatewords:6 }}'
    )

    num_children = LinkColumn(
        'dashboard:catalogue-category-detail-list', args=[A('pk')],
        verbose_name=mark_safe(_('Number of child categories')),
        accessor='get_num_children', orderable=False
    )

    actions = TemplateColumn(template_name='dashboard/catalogue/category_row_actions.html', orderable=False)

    icon = "sitemap"
    caption = ungettext_lazy("%s Category", "%s Categories")

    class Meta(DashboardTable.Meta):

        model = Category
        fields = ('name', 'description')


class AttributeOptionGroupTable(DashboardTable):

    name = TemplateColumn(
        verbose_name=_('Name'),
        template_name='dashboard/catalogue/attribute_option_group_row_name.html',
        order_by='name'
    )

    option_summary = TemplateColumn(
        verbose_name=_('Option summary'),
        template_name='dashboard/catalogue/attribute_option_group_row_option_summary.html',
        orderable=False
    )

    actions = TemplateColumn(
        verbose_name=_('Actions'),
        template_name='dashboard/catalogue/attribute_option_group_row_actions.html',
        orderable=False
    )

    icon = "sitemap"
    caption = ungettext_lazy("%s Attribute Option Group", "%s Attribute Option Groups")

    class Meta(DashboardTable.Meta):

        model = AttributeOptionGroup
        fields = ('name',)
        sequence = ('name', 'option_summary', 'actions')
        per_page = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE


class CustomUserTable(UserTable):

    """
    User customer table.
    """

    check = CustomUserCheckboxHeader(
        template_name='dashboard/users/user_row_checkbox.html',
        verbose_name=' ', orderable=False
    )

    email = LinkColumn('dashboard:user-detail', args=[A('id')], accessor='email')

    name = Column(accessor='get_full_name', order_by=('last_name', 'first_name'))

    mobile_number = TemplateColumn(template_name='dashboard/users/user_row_mobile_number.html',orderable=False, )

    active = TemplateColumn(template_name='dashboard/users/user_row_is_active.html',verbose_name= 'Status',orderable=False, )
    staff = Column(accessor='is_staff', visible=False)
    date_registered = Column(accessor='date_joined')
    num_orders = Column(accessor='orders.count', orderable=False, verbose_name=_('Number of Orders'))
    actions = TemplateColumn(template_name='dashboard/users/user_row_actions.html', verbose_name=' ')

    icon = "group"

    class Meta(DashboardTable.Meta):

        fields = ('mobile_number',)
        sequence = ('check','name', 'email', 'mobile_number', 'active','date_registered', 'num_orders',)
        template = 'dashboard/users/table.html'

