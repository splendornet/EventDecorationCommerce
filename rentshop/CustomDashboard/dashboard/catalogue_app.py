# python imports

# django imports
from django.conf.urls import url

# 3rd party imports
from oscar.core.application import DashboardApplication
from oscar.apps.dashboard.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from oscar.apps.dashboard.reports.app import ReportsApplication as CoreReportsApplication
from oscar.apps.dashboard.partners.app import PartnersDashboardApplication as CorePartnersDashboardApplication
from oscar.apps.dashboard.users.app import UserManagementApplication as CoreUserManagementApplication
from oscar.apps.dashboard.ranges.app import RangeDashboardApplication as CoreRangeDashboardApplication
from oscar.apps.dashboard.vouchers.app import VoucherDashboardApplication as CoreVoucherDashboardApplication
from oscar.apps.dashboard.orders.app import OrdersDashboardApplication as CoreOrdersDashboardApplication
from oscar.apps.dashboard.reviews.app import ReviewsApplication as CoreReviewsApplication

from oscar.core.loading import get_class
from oscar.apps.dashboard import app

class AccountsApplication(DashboardApplication):

    name = None
    default_permissions = ['is_staff', ]

    net_profile_index_view = get_class('dashboard.accounts.accounts', 'AccountNetProfitView')
    export_net_profile = get_class('dashboard.accounts.accounts', 'ExportNetProfile')
    product_margin_list = get_class('dashboard.accounts.accounts', 'ProductMarginListView')
    get_sub_category = get_class('dashboard.accounts.accounts', 'GetSubCategory')
    set_margin_list = get_class('dashboard.accounts.accounts', 'SetMarginListView')
    apply_margin = get_class('dashboard.accounts.accounts', 'ApplyMarginView')
    custom_flat_pages_list = get_class('dashboard.accounts.customflatpages', 'CustomFlatPagesListView')
    custom_flat_pages_create_update = get_class('dashboard.accounts.customflatpages', 'CustomFlatPagesCreateUpateView')
    custom_flat_pages_create_update_v1 = get_class('dashboard.accounts.customflatpages', 'CustomFlatPagesCreateUpateViewV1')
    upload_my_offer_images = get_class('dashboard.images_upload.my_offer', 'ImagesUploadView')
    upload_img = get_class('dashboard.images_upload.my_offer', 'CustomFlatPagesCreateUpateViewV1')

    def get_urls(self):

        urls = [
            url(r'^net-profit/$', self.net_profile_index_view.as_view(), name='accounts-net-profit'),
            url(r'^export-net-profile/(?P<pk>\d+)/$', self.export_net_profile.as_view(), name='accounts-export-net-profile'),
            url(r'^product-margin/$', self.product_margin_list.as_view(), name='accounts-product-margin'),
            url(r'^get-sub-category/$', self.get_sub_category.as_view(), name='accounts-get-sub-category'),
            url(r'^set-margin/$', self.set_margin_list.as_view(), name='accounts-set-margin'),
            url(r'^apply-margin/$', self.apply_margin.as_view(), name='accounts-apply-margin'),
            url(r'^front-legal-page/$', self.custom_flat_pages_create_update.as_view(), name='accounts-legal-page'),
            url(r'^front-legal-page-v1/$', self.custom_flat_pages_create_update_v1.as_view(), name='accounts-legal-page-v1'),
            # url(r'^-create-front-pages/$', self.custom_flat_pages_create.as_view(), name='accounts-create-flat-pages'),
            url(r'^upload-my-offer-images/$', self.upload_my_offer_images.as_view(), name='upload-my-offer-images'),
            url(r'^uplaod-my-offer-image/$', self.upload_img.as_view(),
                name='uplaod-my-offer-image-v1'),

        ]

        return self.post_process_urls(urls)


class SalesApplication(DashboardApplication):

    name = None
    default_permissions = ['is_staff', ]

    custom_order_list_view = get_class('dashboard.sales.customized_order', 'CustomOrdersListView')
    custom_order_create_view = get_class('dashboard.sales.customized_order', 'CreateCustomOrder')
    custom_order_export = get_class('dashboard.sales.customized_order', 'ExportCustomOrder')
    coupon_distributor_add_view = get_class('dashboard.coupon.offers_views', 'CouponDistributorView')
    coupon_distributor_list_view = get_class('dashboard.coupon.offers_views', 'CouponDistributorList')
    coupon_distributor_delete_view = get_class('dashboard.coupon.offers_views', 'DistributorDeleteView')

    def get_urls(self):

        urls = [
            url(r'^custom-orders/$', self.custom_order_list_view.as_view(), name='sales-custom-orders'),
            url(r'^custom-orders-create/$', self.custom_order_create_view.as_view(), name='sales-custom-orders-create'),
            url(r'^custom-orders-export/$', self.custom_order_export.as_view(), name='sales-custom-orders-export'),
            url(r'^add-coupon-distributor/$', self.coupon_distributor_add_view.as_view(), name='add-coupon-distributor'),
            url(r'^update-coupon-distributor/(?P<pk>\d+)/$', self.coupon_distributor_add_view.as_view(), name='update-coupon-distributor'),
            url(r'^delete-coupon-distributor/(?P<pk>\d+)/$', self.coupon_distributor_delete_view.as_view(), name='delete-coupon-distributor'),
            url(r'^coupon-distributors/$', self.coupon_distributor_list_view.as_view(), name='coupon-distributors'),

        ]

        return self.post_process_urls(urls)


class ReviewsApplication(CoreReviewsApplication):

    list_view = get_class('dashboard.review.review', 'CustomReviewListView')
    update_view = get_class('dashboard.review.review', 'CustomReviewUpdateView')
    update_review_bulk = get_class('dashboard.review.review', 'UpdateReviewStatus')

    def get_urls(self):

        urls = [
            url(r'^update-review-bulk/$', self.update_review_bulk.as_view(), name='update-review-bulk'),
        ]

        urls = urls + super(ReviewsApplication, self).get_urls()
        return urls


class CatalogueApplication(CoreCatalogueApplication):

    """
    Oscar extended method of catalogues
    """

    product_createupdate_view = get_class('dashboard.views', 'CustomProductCreateUpdateView')
    product_list_view = get_class('dashboard.products.product', 'FilteredProductListView')

    category_create_view = get_class('dashboard.views','CustomCategoryCreateView')
    category_update_view = get_class('dashboard.views','CustomCategoryUpdateView')
    category_list_view = get_class('dashboard.views', 'CustomCategoryListView')

    stock_alert_view = get_class('dashboard.views', 'CustomStockAlertListView')
    product_type_update = get_class('dashboard.views', 'ProductTypeUpdateView')

    product_unit_list = get_class('dashboard.views', 'ProductUnitListView')
    product_unit_create = get_class('dashboard.views', 'ProductUnitCreateView')
    product_unit_update = get_class('dashboard.views', 'ProductUnitUpdateView')
    product_unit_delete = get_class('dashboard.views', 'ProductUnitDeleteView')
    arrange_sub = get_class('dashboard.views', 'ArrangeSubCategory')
    arrange_category = get_class('dashboard.views', 'ArrangeCategory')

    combo_index = get_class('dashboard.combo.combo', 'ComboOfferIndexView')
    combo_createupdate_view = get_class('dashboard.views', 'CreateUpdateCombo')
    combo_product_create_redirect_view = get_class('dashboard.views', 'ProductComboCreateRedirectView')
    combo_delete = get_class('dashboard.views', 'ProductComboDeleteView')

    # combo lastet
    create_combo = get_class('dashboard.combo.combo', 'CreateCombo')
    create_combo_v1 = get_class('dashboard.combo.combo', 'CreateComboV1')
    update_combo_v1 = get_class('dashboard.combo.combo', 'UpdateComboV1')
    delete_combo = get_class('dashboard.combo.combo', 'DeleteCombo')

    premium_index = get_class('dashboard.premiumproduct.premium', 'PremiumIndexView')
    create_premium_product = get_class('dashboard.premiumproduct.premium', 'CreatePremiumProduct')
    premium_product_delete = get_class('dashboard.premiumproduct.premium', 'PremiumProductDelete')
    premium_product_update = get_class('dashboard.premiumproduct.premium', 'PremiumProductUpdateView')

    taxation_index = get_class('dashboard.taxation.taxation', 'TaxationIndexView')
    create_tax = get_class('dashboard.taxation.taxation', 'CreateTax')
    tax_delete = get_class('dashboard.taxation.taxation', 'TaxDelete')
    tax_update = get_class('dashboard.taxation.taxation', 'TaxUpdateView')
    create_update_tax_perc = get_class('dashboard.taxation.taxation', 'CreateUpdateTaxPercentageView')

    adv_percentage_index = get_class('dashboard.advanced_pay.advanced_pay', 'PercentageIndexView')
    create_adv_percentage = get_class('dashboard.advanced_pay.advanced_pay', 'CreatePercentage')
    adv_percentage_delete = get_class('dashboard.advanced_pay.advanced_pay', 'PercentageDelete')
    adv_percentage_update = get_class('dashboard.advanced_pay.advanced_pay', 'PercentageUpdateView')
    create_update_adv_perc = get_class('dashboard.advanced_pay.advanced_pay', 'CreateUpdatePercentageView')

    attribute_index = get_class('dashboard.attributes.attribute', 'AttributeIndexView')
    create_attribute = get_class('dashboard.attributes.attribute', 'CreateAttribute')
    attribute_delete = get_class('dashboard.attributes.attribute', 'AttributeDelete')
    attribute_update = get_class('dashboard.attributes.attribute', 'AttributeUpdateView')

    manage_menu_index = get_class('dashboard.manage_menu.combo', 'ManageMenuIndexView')
    create_manage_menu = get_class('dashboard.manage_menu.combo', 'CreateManageMenu')
    update_manage_menu = get_class('dashboard.manage_menu.combo', 'UpdateHeaderMenu')
    delete_cmanage_menu = get_class('dashboard.manage_menu.combo', 'DeleteManageMenu')

    exhibition_offers_index = get_class('dashboard.manage_menu.combo', 'ExhibitionOffersIndexView')
    create_exhibition_offers = get_class('dashboard.manage_menu.combo', 'CreateExhibitionOffers')
    update_exhibition_offers = get_class('dashboard.manage_menu.combo', 'UpdateExhibitionOffers')
    delete_exhibition_offers = get_class('dashboard.manage_menu.combo', 'DeleteExhibitionOffers')

    rate_card_list = get_class('dashboard.products.product', 'RateCardListView')
    rate_card_list_details = get_class('dashboard.products.product', 'RateCardDetailListView')
    rate_card_create = get_class('dashboard.products.product', 'RateCardCreateView')
    rate_card_update = get_class('dashboard.products.product', 'RateCardUpdateView')
    rate_card_delete = get_class('dashboard.products.product', 'RateCardDeleteView')

    product_update_adv_payment = get_class('dashboard.products.product', 'UpdateAdvancePayment')

    category_filter_list = get_class('dashboard.categoryfilter.categoryfilter', 'CategoryFilterIndexView')
    categoryfilter_update = get_class('dashboard.categoryfilter.categoryfilter', 'CategoryFilterUpdateView')

    create_category_price_filter = get_class('dashboard.categoryfilter.categoryfilter', 'CategoryPriceFilterCreateUpdateView')
    category_price_filter_list = get_class('dashboard.categoryfilter.categoryfilter', 'CategoryPriceFilterIndexView')
    price_filter_delete_view = get_class('dashboard.categoryfilter.categoryfilter', 'PriceFilterDeleteView')


    featured_product_list = get_class('dashboard.products.product', 'FeaturedProductListView')
    featured_products_remove = get_class('dashboard.products.product', 'RemoveFeaturedView')

    def get_urls(self):

        urls = [

            url(r'^update-adv-payment/$', self.product_update_adv_payment.as_view(), name='update-adv-payment'),

            url(r'^rate-card/products/$', self.rate_card_list.as_view(), name='rate-card-products'),
            url(r'^rate-card/products/create/$', self.rate_card_create.as_view(), name='rate-card-products-create'),
            url(r'^rate-card/products/(?P<pk>\d+)/update/$', self.rate_card_update.as_view(), name='rate-card-products-update'),
            url(r'^rate-card/products/(?P<pk>\d+)/delete/$', self.rate_card_delete.as_view(), name='rate-card-products-delete'),
            url(r'^rate-card/products/(?P<pk>\d+)/details/$', self.rate_card_list_details.as_view(), name='rate-card-products-details'),

            url(r'^featured_products_remove/(?P<pk>\d+)/delete/$', self.featured_products_remove.as_view(),
                name='featured-products-remove'),

            url(r'^featured_product_list/products/$', self.featured_product_list.as_view(), name='featured-product-list'),

            url(r'^combo/index/', self.combo_index.as_view(), name='combo-index'),
            url(r'^combo/create-offer-x/(?P<pk>\d+)/$', self.create_combo.as_view(), name='create-combo'),
            url(r'^combo/create-offer/$', self.create_combo_v1.as_view(), name='create-combo-v1'),
            url(r'^combo/create-offer-update/(?P<pk>\d+)/$', self.update_combo_v1.as_view(), name='update-combo-v1'),
            url(r'^combo/(?P<pk>\d+)/delete-combo/$', self.delete_combo.as_view(), name='delete-combo-v1'),

            url(r'^combo/redirect/$', self.combo_product_create_redirect_view.as_view(), name='combo-product-redirect'),
            url(r'^combo/create/(?P<pk>\d+)/$', self.combo_createupdate_view.as_view(), name='combo-create-update'),
            url(r'^combo/create/(?P<product_class_slug>[\w-]+)/$', self.combo_createupdate_view.as_view(), name='combo-create-update'),
            url(r'^combo/delete/(?P<pk>\d+)/$', self.combo_delete.as_view(), name='combo-delete'),

            url(r'product_unit$', self.product_unit_list.as_view(), name='product_unit'),
            url(r'product_unit_create$', self.product_unit_create.as_view(), name='product_unit_create'),
            url(r'product_unit/(?P<pk>\d+)/edit/', self.product_unit_update.as_view(), name='product_unit_update'),
            url(r'product_unit_delete/(?P<pk>\d+)/delete/', self.product_unit_delete.as_view(), name='product_unit_delete'),
            url(r'product_type_update/(?P<pk>\d+)/update/', self.product_type_update.as_view(), name='product_type_update'),
            url(r'arrange_sub/(?P<pk>\d+)/range/', self.arrange_sub.as_view(), name='arrange_sub'),
            url(r'arrange_category/', self.arrange_category.as_view(), name='arrange_category'),

            url(r'^premium/index/', self.premium_index.as_view(), name='premium-index'),
            url(r'^catalogue/premium/create-product/$', self.create_premium_product.as_view(), name='create-premium-product'),
            url(r'catalogue/premium/(?P<pk>\d+)/delete$', self.premium_product_delete.as_view(), name='premium-product-delete'),
            url(r'catalogue/premium/(?P<pk>\d+)/', self.premium_product_update.as_view(), name='premium-product-update'),

            url(r'^manage_menu/index/', self.manage_menu_index.as_view(), name='manage-menu-index'),
            url(r'^manage_menu/create-offer/$', self.create_manage_menu.as_view(), name='create-manage-menu'),
            url(r'^manage_menu/create-offer-update/(?P<pk>\d+)/$', self.update_manage_menu.as_view(), name='update-manage-menu'),
            url(r'^manage_menu/(?P<pk>\d+)/delete/$', self.delete_cmanage_menu.as_view(), name='delete-manage-menu'),

            url(r'^exhibition_offers/index/', self.exhibition_offers_index.as_view(), name='exhibition-offers-index'),
            url(r'^exhibition_offers/create-offer/$', self.create_exhibition_offers.as_view(), name='create-exhibition-offers'),
            url(r'^exhibition_offers/create-offer-update/(?P<pk>\d+)/$', self.update_exhibition_offers.as_view(),
                name='update-exhibition-offers'),
            url(r'^exhibition_offers/(?P<pk>\d+)/delete/$', self.delete_exhibition_offers.as_view(), name='delete-exhibition-offers'),

            url(r'^taxation/index/', self.taxation_index.as_view(), name='taxation-index'),
            url(r'^catalogue/create-tax/$', self.create_tax.as_view(),
                name='create-tax'),
            url(r'catalogue/tax/(?P<pk>\d+)/delete$', self.tax_delete.as_view(),
                name='tax-delete'),
            url(r'catalogue/tax/(?P<pk>\d+)/', self.tax_update.as_view(),
                name='tax-update'),

            url(r'^adv_percentage/index/', self.adv_percentage_index.as_view(), name='adv-percentage-index'),
            url(r'^catalogue/create-adv_percentage/$', self.create_adv_percentage.as_view(),
                name='create-adv-percentage'),
            url(r'catalogue/adv_percentage/(?P<pk>\d+)/delete$', self.adv_percentage_delete.as_view(),
                name='adv-percentage-delete'),
            url(r'catalogue/adv_percentage/(?P<pk>\d+)/', self.adv_percentage_update.as_view(),
                name='adv-percentage-update'),

            url(r'^adv_percentage/$', self.create_update_adv_perc.as_view(),name='adv-percentage-v1'),
            url(r'^tax_percentage/$', self.create_update_tax_perc.as_view(),name='tax-percentage-v1'),

            url(r'^attribute/index/', self.attribute_index.as_view(), name='attribute-index'),
            url(r'^catalogue/create-attribute/$', self.create_attribute.as_view(),
                name='create-attribute'),
            url(r'catalogue/attribute/(?P<pk>\d+)/delete$', self.attribute_delete.as_view(),
                name='attribute-delete'),
            url(r'catalogue/attribute/(?P<pk>\d+)/', self.attribute_update.as_view(),
                name='attribute-update'),

            url(r'^category_filter/$', self.category_filter_list.as_view(), name='category-filter-index'),
            url(r'^category_filter/create-filter/(?P<pk>\d+)/$', self.categoryfilter_update.as_view(),
                name='categoryfilter-update'),

            url(r'^create_category_price_filter/$', self.create_category_price_filter.as_view(), name='create-price-filter'),
            url(r'^category_price_filter/$', self.category_price_filter_list.as_view(), name='category-filter-price-index'),
            url(r'^update-price-filter/(?P<pk>\d+)/$', self.create_category_price_filter.as_view(), name='update-price-filter'),
            url(r'^delete-price-filter/(?P<pk>\d+)/$', self.price_filter_delete_view.as_view(),
                name='delete-price-filter'),

        ]
        urls = urls + super(CatalogueApplication, self).get_urls()
        return urls


class OrdersDashboardApplication(CoreOrdersDashboardApplication):

    """
    Oscar extended method of dashboard apps.
    """

    order_list_view = get_class('dashboard.order.order', 'CustomOrderListView')
    order_detail_view = get_class('dashboard.order.order', 'CustomOrderDetailView')

    vendor_order_list = get_class('dashboard.sales.vendor_orders', 'VendorOrders')
    order_summary_invoice = get_class('dashboard.order.order', 'OrderSummaryInvoiceView')
    order_invoice = get_class('dashboard.order.order', 'OrderInvoiceView')
    order_invoice_raw = get_class('dashboard.order.order', 'OrderInvoiceRaw')

    order_invoice_product_wise = get_class('dashboard.order.order', 'OrderInvoiceProductView')

    def get_urls(self):

        urls = [
            url(r'^vendor-orders/$', self.vendor_order_list.as_view(), name='vendor-orders'),
            url(r'^order-summary-invoice/(?P<pk>\d+)/$', self.order_summary_invoice.as_view(), name='order-summary-invoice'),
            url(r'^order-invoice/(?P<pk>\d+)/$', self.order_invoice.as_view(), name='order-invoice'),
            url(r'^order-invoice-raw/(?P<pk>\d+)/$', self.order_invoice_raw.as_view(), name='order-invoice-raw'),
            url(r'^order-invoice-product/(?P<pk>\d+)/(?P<vendor_id>\d+)/$', self.order_invoice_product_wise.as_view(), name='order-invoice-product-wise'),
        ]

        urls = urls + super(OrdersDashboardApplication, self).get_urls()
        return urls


class ReportsApplication(CoreReportsApplication):

    """
    Oscar reports extended method.
    """

    index_view = get_class('dashboard.report.report', 'CustomReportIndexView')


class PartnersDashboardApplication(CorePartnersDashboardApplication):

    """
    Oscar partner extended method.
    """

    list_view = get_class('dashboard.views', 'CustomPartnerListView')
    #manage_view = get_class('dashboard.views', 'CustomPartnerManageView')
    manage_view = get_class('dashboard.vendor.vendor', 'CustomPartnerManageView')
    vendor_calender_list = get_class('dashboard.views', 'VendorCalenderListView')
    vendor_calender_add = get_class('dashboard.views', 'VendorCalendarEventAddView')
    vendor_calender_table_list = get_class('dashboard.views', 'VendorCalendarTableView')
    vendor_calender_edit = get_class('dashboard.views', 'VendorCalendarEditForm')
    vendor_calender_delete = get_class('dashboard.views', 'VendorCalendarDeleteView')
    vendor_calendar_delete_confirm = get_class('dashboard.views', 'VendorCalendarConfirm')

    sales_list = get_class('dashboard.sales.sales', 'SalesListView')
    sales_event_update = get_class('dashboard.sales.sales', 'SalesEventUpdateView')
    sales_event_delete = get_class('dashboard.sales.sales', 'SaleVendorDeleteEvent')
    sales_prime_bucket = get_class('dashboard.sales.sales', 'SalesPrimeBucketView')
    re_allocate_order = get_class('dashboard.sales.sales', 'ReallocateOrderListView')
    sales_order_allocate = get_class('dashboard.sales.sales', 'OrderAllocateView')
    order_re_allocate = get_class('dashboard.sales.sales', 'OrderReallocateView')
    offers_prime_bucket = get_class('dashboard.sales.sales', 'OffersPrimeBucketView')
    offers_reallocate_order = get_class('dashboard.sales.sales', 'OffersOrderReallocate')
    offers_order_allocate = get_class('dashboard.sales.sales', 'OffersOrderAllocateView')
    offers_order_reallocate = get_class('dashboard.sales.sales', 'OffersOrderReallocateView')

    cancel_order = get_class('dashboard.sales.sales', 'CancelledOrderListView')
    change_refund_status = get_class('dashboard.sales.sales', 'ChangeOrderStatus')

    asp_db = get_class('dashboard.sales.asp_db', 'ASPDBView')
    create_asp_db = get_class('dashboard.sales.asp_db', 'CreateFormDB')

    individualdb_table_list = get_class('dashboard.sales.asp_db', 'IndividualDBListView')
    individualdb_details_view = get_class('dashboard.sales.asp_db', 'IndividualDBDetailView')
    individualdb_update_view = get_class('dashboard.sales.asp_db', 'IndividualDBUpdateView')
    individualdb_delete_view = get_class('dashboard.sales.asp_db', 'IndividualDBDelete')

    multidb_table_list = get_class('dashboard.sales.asp_db', 'MultiDBListView')
    multidb_details_view = get_class('dashboard.sales.asp_db', 'MultiDetailView')
    multidb_update_view = get_class('dashboard.sales.asp_db', 'MultiDBUpdateView')
    multidb_delete_view = get_class('dashboard.sales.asp_db', 'MultiDBDelete')

    admin_create_event = get_class('dashboard.events.events', 'CreateEventAdmin')
    admin_update_event = get_class('dashboard.events.events', 'UpdateEventAdmin')

    best_quote = get_class('dashboard.sales.best_quote', 'BestQuoteView')
    quote_delete = get_class('dashboard.sales.best_quote', 'BestQuoteDelete')
    best_quote_allocate = get_class('dashboard.sales.best_quote', 'BestQuoteAllocateView')
    delete_view = get_class('dashboard.views', 'CustomPartnerDeleteView')

    cancellation_index = get_class('dashboard.cancellation_charge.cancellation_charge', 'CancellationChargesIndexview')
    create_cancellation_charge = get_class('dashboard.cancellation_charge.cancellation_charge',
                                           'CreateCancellationCharge')
    delete_cancellation_charge = get_class('dashboard.cancellation_charge.cancellation_charge',
                                           'DeleteCancellationCharge')
    update_cancellation_charge = get_class('dashboard.cancellation_charge.cancellation_charge',
                                           'UpdateCancellationCharge')


    def get_urls(self):
        urls = [
            url(r'calender$', self.vendor_calender_list.as_view(), name='vendor-calender'),
            url(r'calender/add$', self.vendor_calender_add.as_view(), name='vendor-calender-add'),
            url(r'calender/list/', self.vendor_calender_table_list.as_view(), name='vendor-calender-list'),
            url(r'calender/(?P<pk>\d+)/edit/', self.vendor_calender_edit.as_view(), name='vendor-calender-edit'),
            url(r'calender/(?P<pk>\d+)/delete$', self.vendor_calender_delete.as_view(), name='vendor-calender-delete'),
            url(r'calender/(?P<pk>\d+)/confirm$', self.vendor_calendar_delete_confirm.as_view(), name='vendor-calender-delete-confirm'),

            url(r'sales/event/(?P<pk>\d+)/edit$', self.sales_event_update.as_view(), name='sales-event-update'),
            url(r'sales/event/(?P<pk>\d+)/delete$', self.sales_event_delete.as_view(), name='sales-event-delete'),
            url(r'sales', self.sales_list.as_view(), name='sales-index'),

            url(r'prime/prime-bucket$', self.sales_prime_bucket.as_view(), name='prime-bucket'),
            url(r're_allocate_order$', self.re_allocate_order.as_view(), name='re-allocate-order'),
            url(r'prime/prime-order-allocate/(?P<pk>\d+)/$', self.sales_order_allocate.as_view(), name='prime-order-allocate'),
            url(r're_allocate/(?P<pk>\d+)/$', self.order_re_allocate.as_view(), name='re-allocate'),
            url(r'prime/offers-prime-bucket/$', self.offers_prime_bucket.as_view(), name='offers-prime-bucket'),
            url(r'prime/offers-order-reallocate/$', self.offers_reallocate_order.as_view(), name='offers-order-reallocate'),
            url(r'prime/offers-order-allocate/(?P<pk>\d+)/$', self.offers_order_allocate.as_view(), name='offers-order-allocate'),
            url(r'prime/offers-order-reallocate/(?P<pk>\d+)/$', self.offers_order_reallocate.as_view(), name='offers-order-reallocate'),

            url(r'cancel_order$', self.cancel_order.as_view(), name='cancel-order-index'),
            url(r'^change_order_refund_status/$', self.change_refund_status.as_view(), name='change-order-refund-status'),

            url(r'asp-db$', self.asp_db.as_view(), name='asp-db'),
            url(r'create_asp_db$', self.create_asp_db.as_view(), name='create-asp-db'),

            url(r'individualdb/list/', self.individualdb_table_list.as_view(), name='individualdb-list'),
            url(r'individualdb/details/(?P<pk>\d+)', self.individualdb_details_view.as_view(), name='individualdb-details'),
            url(r'individualdb/update/(?P<pk>\d+)/', self.individualdb_update_view.as_view(), name='individualdb-update'),
            url(r'individualdb/delete/(?P<pk>\d+)/', self.individualdb_delete_view.as_view(), name='individualdb-delete'),

            url(r'multidb/list/', self.multidb_table_list.as_view(), name='multidb-list'),
            url(r'multidb/details/(?P<pk>\d+)', self.multidb_details_view.as_view(), name='multidb-details'),
            url(r'multidb/update/(?P<pk>\d+)/', self.multidb_update_view.as_view(), name='multidb-update'),
            url(r'multidb/delete/(?P<pk>\d+)/', self.multidb_delete_view.as_view(), name='multidb-delete'),

            url(r'create-event-admin$', self.admin_create_event.as_view(), name='create-event-admin'),
            url(r'admin_update_event/(?P<pk>\d+)$', self.admin_update_event.as_view(), name='update-event-admin'),

            url(r'best_quote$', self.best_quote.as_view(), name='best_quote'),
            url(r'catalogue/quote/(?P<pk>\d+)/delete$', self.quote_delete.as_view(),
                name='quote-delete'),

            url(r'best_quote/best_quote_allocate/(?P<pk>\d+)/$', self.best_quote_allocate.as_view(),
                name='best-quote-allocate'),
            url(r'^(?P<pk>\d+)/delete/$', self.delete_view.as_view(),
                name='partner-delete'),

            url(r'^cancellation/', self.cancellation_index.as_view(), name='cancellation_index'),
            url(r'^dashboard/create_cancellation_charge/$', self.create_cancellation_charge.as_view(),
                name='create-cancellation-charge'),
            url(r'dashboard/delete_cancellation_charge/(?P<pk>\d+)/delete$', self.delete_cancellation_charge.as_view(),
                name='delete_cancellation_charge'),
            url(r'dashboard/update_cancellation_charge/(?P<pk>\d+)/', self.update_cancellation_charge.as_view(),
                name='update_cancellation_charge'),

        ]
        urls = urls + super(PartnersDashboardApplication, self).get_urls()
        return urls


class UserManagementApplication(CoreUserManagementApplication):

    """
    Oscar extended user app method.
    """

    index_view = get_class('dashboard.views', 'CustomIndexView')


class RangeDashboardApplication(CoreRangeDashboardApplication):

    """
    Oscar extended range app method.
    """

    list_view = get_class('dashboard.views', 'CustomRangeListView')
    create_view = get_class('dashboard.views', 'CustomRangeCreateView')
    update_view = get_class('dashboard.views', 'CustomRangeUpdateView')
    create_new_coupon = get_class('dashboard.views', 'CustomRangeCreateView1')

    def get_urls(self):
        urls = [
        url(r'^dashboard/create_new_coupon/$', self.create_new_coupon.as_view(),
                name='create-new-coupon'),
        ]
        urls = urls + super(RangeDashboardApplication, self).get_urls()
        return urls


class VoucherDashboardApplication(CoreVoucherDashboardApplication):

    """
    Oscar extended voucher range app method.
    """

    list_view = get_class('dashboard.views', 'CustomVoucherListView')
    create_view = get_class('dashboard.views', 'CustomVoucherCreateView')
    update_view = get_class('dashboard.views','CustomVoucherUpdateView')
    delete_view = get_class('dashboard.views', 'CustomVoucherDeleteView')

    create_view1 = get_class('dashboard.views', 'CustomVoucherCreateView1')
    list_view1 = get_class('dashboard.views', 'CustomVoucherListView1')
    update_view1 = get_class('dashboard.views','CustomVoucherUpdateView1')
    custom_stats_view = get_class('dashboard.views', 'CustomVoucherStatsView')

    price_range_add_view = get_class('dashboard.coupon.offers_views', 'PriceRangeView')
    price_range_list_view = get_class('dashboard.coupon.offers_views', 'PriceRangeList')
    price_range_delete_view = get_class('dashboard.coupon.offers_views', 'PriceRangeDeleteView')

    customize_list_view1 = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'CustomizeCouponListView1')
    customize_create_view1 = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'CustomizeCouponCreateView1')
    customize_coupon_delete_view = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'CustomizeVoucherDeleteView')
    customize_stats_view = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'CustomizeVoucherStatsView')

    def get_urls(self):
        urls = [
            url(r'^create1/$', self.create_view1.as_view(),
                name='voucher-create1'),
            url(r'^list$', self.list_view1.as_view(), name='voucher-list1'),
            url(r'^update1/(?P<pk>\d+)/$', self.update_view1.as_view(),
                name='voucher-update1'),
            url(r'^custom-stats/(?P<pk>\d+)/$', self.custom_stats_view.as_view(),
                name='voucher-stats1'),

            url(r'^add-price-range/$', self.price_range_add_view.as_view(), name='add-price-range'),
            url(r'^update-price-range/(?P<pk>\d+)/$', self.price_range_add_view.as_view(), name='update-price-range'),
            url(r'^delete-price-range/(?P<pk>\d+)/$', self.price_range_delete_view.as_view(), name='delete-price-range'),
            url(r'^price-range-list/$', self.price_range_list_view.as_view(), name='price-range-list'),

            url(r'^customize-coupon-list$', self.customize_list_view1.as_view(), name='customize-voucher-list1'),
            url(r'^create-customize-coupon/$', self.customize_create_view1.as_view(),
                name='customize-create1'),
            url(r'^update-customize-coupon/(?P<pk>\d+)/$', self.customize_create_view1.as_view(), name='update-customize-coupon'),
            url(r'^delete-customize-coupon/(?P<pk>\d+)/$', self.customize_coupon_delete_view.as_view(),
                name='customize-coupon-delete'),
            url(r'^customize-coupon-stats/(?P<pk>\d+)/$', self.customize_stats_view.as_view(),
                name='customize-voucher-stats'),

        ]
        urls = urls + super(VoucherDashboardApplication, self).get_urls()
        return urls



application = CatalogueApplication()
order_application = OrdersDashboardApplication()
report_application = ReportsApplication()
partner_application = PartnersDashboardApplication()
user_application = UserManagementApplication()
range_application = RangeDashboardApplication()
voucher_application = VoucherDashboardApplication()
review_application = ReviewsApplication()
accounts_application = AccountsApplication()
sales_application = SalesApplication()