# python imports
import datetime

# django imports
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.flatpages import views
from django.views.generic import TemplateView

# 3rd party imports
from oscar.app import application
from oscar.core.loading import get_class

# internal imports
abandoned_carts = get_class('basket.views', 'abandoned_carts')
check_cron_view = get_class('partner.views', 'check_cron_view')
state_ajax = get_class('partner.views', 'state_ajax')
city_ajax = get_class('partner.views', 'city_ajax')
search_filter_ajax = get_class('partner.views', 'search_filter_ajax')
get_state_id = get_class('country.views', 'get_state_id')

AdminChangePassword = get_class('dashboard.views', 'AdminChangePassword')
export_combo = get_class('dashboard.combo.combo', 'export_combo')
export_premium = get_class('dashboard.premiumproduct.premium', 'export_premium')
export_individualdb = get_class('dashboard.sales.asp_db', 'export_individualdb')
export_multidb = get_class('dashboard.sales.asp_db', 'export_multidb')
export_menu = get_class('dashboard.manage_menu.combo', 'export_menu')
export_exhibition_menu = get_class('dashboard.manage_menu.combo', 'export_exhibition')
export_quote = get_class('dashboard.sales.best_quote', 'export_quote')
export_tax = get_class('dashboard.taxation.taxation', 'export_tax')
export_percentage = get_class('dashboard.advanced_pay.advanced_pay', 'export_percentage')
export_attribute = get_class('dashboard.attributes.attribute', 'export_attribute')


product_blocked_dates = get_class('catalogue.views', 'product_blocked_dates')
product_blocked_dates_onsubmit = get_class('catalogue.views', 'product_blocked_dates_onsubmit')
send_full_payment_email = get_class('catalogue.views', 'send_full_payment_email')
test_sms = get_class('catalogue.views', 'test_sms')

export_products = get_class('dashboard.views', 'export_products')
export_events = get_class('dashboard.views', 'export_events')
export_bookedevents = get_class('dashboard.sales.sales', 'export_bookedevents')
export_categories = get_class('dashboard.views', 'export_categories')
export_vendors = get_class('dashboard.views', 'export_vendors')
export_customers = get_class('dashboard.views', 'export_customers')
export_users = get_class('dashboard.views', 'export_users')

allocate_vendor_sales = get_class('dashboard.sales.sales', 'allocate_vendor_sales')
vendor_re_allocate = get_class('dashboard.sales.sales', 're_allocate_vendor')
allocate_vendor = get_class('dashboard.sales.best_quote', 'allocate_vendor_best_quote')

export_prime_bucket = get_class('dashboard.sales.sales', 'export_prime_bucket')
export_offers_prime_bucket = get_class('dashboard.sales.sales', 'export_offers_prime_bucket')
get_product_attribute = get_class('dashboard.sales.customized_order', 'get_product_attribute')

update_product = get_class('dashboard.views', 'update_product')
delete_bulk_coupon = get_class('dashboard.views', 'delete_bulk_coupon')
delete_bulk_product = get_class('dashboard.views', 'delete_bulk_product')
delete_product_image = get_class('dashboard.views', 'delete_product_image')
delete_product_attribute = get_class('dashboard.views', 'delete_product_attribute')

get_values_of_attribute = get_class('dashboard.views','get_values_of_attribute')
get_total_price = get_class('catalogue.views','get_total_price')
get_total_price_new = get_class('catalogue.views','get_total_price_new')
set_is_discountable = get_class('catalogue.views','set_is_discountable')
set_product_is_deleted = get_class('catalogue.views','set_product_is_deleted')
order_reminder = get_class('catalogue.views','order_reminder')
delete_bulk_vendor = get_class('dashboard.views', 'delete_bulk_vendor')
delete_bulk_units = get_class('dashboard.views', 'delete_bulk_units')
delete_bulk_user = get_class('dashboard.views', 'delete_bulk_user')
delete_bulk_category = get_class('dashboard.views', 'delete_bulk_category')
delete_bulk_reviews = get_class('dashboard.views', 'delete_bulk_reviews')
delete_bulk_event = get_class('dashboard.views', 'delete_bulk_event')
sales_delete_bulk_event = get_class('dashboard.sales.sales', 'sales_delete_bulk_event')
delete_bulk_season = get_class('dashboard.views', 'delete_bulk_season')
delete_bulk_combo_data = get_class('dashboard.combo.combo', 'delete_bulk_combo_data')
delete_bulk_menu_data = get_class('dashboard.manage_menu.combo', 'delete_bulk_menu_data')

delete_combo_product = get_class('dashboard.views', 'delete_combo_product')
delete_header_product = get_class('dashboard.manage_menu.combo', 'delete_header_product')
delete_header_category = get_class('dashboard.manage_menu.combo', 'delete_header_category')
delete_bulk_exhibition = get_class('dashboard.manage_menu.combo', 'delete_bulk_exhibition_menu_data')

delete_bulk_premium_data = get_class('dashboard.premiumproduct.premium', 'delete_bulk_premium_data')
delete_bulk_individual_data = get_class('dashboard.sales.asp_db', 'delete_bulk_individual_data')
delete_bulk_multi_data = get_class('dashboard.sales.asp_db', 'delete_bulk_multi_data')
delete_bulk_quote_data = get_class('dashboard.sales.best_quote', 'delete_bulk_quote_data')
delete_bulk_tax_data = get_class('dashboard.taxation.taxation', 'delete_bulk_tax_data')
delete_bulk_percentage_data = get_class('dashboard.advanced_pay.advanced_pay', 'delete_bulk_percentage_data')
delete_bulk_attribute_data = get_class('dashboard.attributes.attribute', 'delete_bulk_attribute_data')

export_units = get_class('dashboard.views', 'export_units')
export_season = get_class('dashboard.views', 'export_season')
export_orders = get_class('dashboard.views', 'export_orders')
export_category = get_class('dashboard.views', 'export_category')
export_reviews = get_class('dashboard.views', 'export_reviews')
export_coupon = get_class('dashboard.views', 'export_coupon')
export_low_stock = get_class('dashboard.views', 'export_low_stock')

add_admin_notes = get_class('dashboard.views', 'add_admin_notes')
admin_notes = get_class('dashboard.views', 'admin_notes')
deactivate_note = get_class('dashboard.views', 'deactivate_note')

create_note = get_class('dashboard.notes.notes', 'add_admin_notes')
get_event_products = get_class('dashboard.events.events', 'get_event_products')

payment_cancel = get_class('checkout.views', 'payment_cancel')
payment_success = get_class('checkout.views', 'payment_success')
PaymentCancelView = get_class('checkout.views', 'PaymentCancelView')

test_email = get_class('promotions.views', 'test_email')
update_first_login = get_class('promotions.views', 'update_first_login')
CouponsView = get_class('promotions.views', 'CouponsView')
AboutUs = get_class('promotions.views', 'AboutUs')
ContactUsView = get_class('promotions.views', 'ContactUsView')
TermsPageView = get_class('promotions.views', 'TermsPageView')
FQAView = get_class('promotions.views', 'FQAView')
PoliciesView = get_class('promotions.views', 'PoliciesView')
HWorksView = get_class('promotions.views', 'HWorksView')

email_activate = get_class('customer.views', 'email_activate')
CustomPaymentDetailsView = get_class('checkout.views', 'CustomPaymentDetailsView')
updateVendorPassword = get_class('HeaderMenu.views', 'updateVendorPassword')
load_products = get_class('dashboard.premiumproduct.premium', 'load_products')

individualdb_create = get_class('dashboard.sales.asp_db','CreateIndividualDB')
multidb_create = get_class('dashboard.sales.asp_db','CreateMultiDBModelForm')
find_details = get_class('dashboard.sales.asp_db','find_details')

load_vendors = get_class('dashboard.sales.asp_db','load_vendors')
load_categories = get_class('dashboard.sales.asp_db','load_categories')

get_event_products_rate_card = get_class('dashboard.products.product', 'get_event_products_rate_card')
get_products_for_featured = get_class('dashboard.products.product', 'get_products_for_featured')
add_product_featured = get_class('dashboard.products.product', 'add_product_featured')

get_products_order = get_class('dashboard.sales.customized_order', 'get_products_order')
get_vendors_best_quote = get_class('dashboard.sales.best_quote', 'get_vendors_best_quote')

export_rate_card_products = get_class('dashboard.products.product', 'export_rate_card_products')
delete_bulk_costing_product = get_class('dashboard.products.product', 'delete_bulk_costing_product')
delete_bulk_costing_product_items = get_class('dashboard.products.product', 'delete_bulk_costing_product_items')
remove_featured_product = get_class('dashboard.products.product', 'remove_featured_product')
export_rate_card_products_items = get_class('dashboard.products.product', 'export_rate_card_products_items')
export_featured_products = get_class('dashboard.products.product', 'export_featured_products')
export_distributors = get_class('dashboard.coupon.offers_views', 'export_distributors')
export_price_range_db = get_class('dashboard.coupon.offers_views', 'export_price_range_db')
get_coupondist = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'get_coupondist')
get_coupondetails = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'get_coupondetails')

export_customcoupon_data = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'export_customcoupon_data')

test_email = get_class('partner.views', 'test_email')
welcome_mail = get_class('RentCore.email', 'welcome_mail')
create_pages = get_class('dashboard.accounts.customflatpages', 'CustomFlatPagesCreateUpateView_V1')
get_transaction_details = get_class('checkout.views', 'get_transaction_details')
create_new_cart = get_class('basket.views', 'CreateNewCart')
get_otp = get_class('customer.views', 'get_otp')
get_vendor_otp = get_class('customer.views', 'get_vendor_otp')
verify_otp = get_class('customer.views', 'verify_otp')

delete_price = get_class('dashboard.categoryfilter.categoryfilter', 'delete_price')
delete_price_range = get_class('dashboard.coupon.offers_views', 'delete_price_range')
delete_customize_category = get_class('dashboard.coupon.customize_coupon.customize_coupon', 'delete_customize_category')

export_price_filter = get_class('dashboard.categoryfilter.categoryfilter', 'export_price_filter')

urlpatterns = [

    # admin url
    url('admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # packages imports
    url(r'^select2/', include('django_select2.urls')),
    url(r'^captcha/', include('captcha.urls')),
    # url(r'ckeditor/', include('ckeditor_uploader.urls')),
    url(r'', (application.urls)),
    url(r'vendor/', include('CustomPartner.partner.urls')),
    url(r'', include('FrontendSite.urls')),
    url(r'', include('serviceOrders.urls')),

    url(r'state_ajax/', state_ajax),
    url(r'city_ajax/', city_ajax),
    url(r'search_filter_data/', search_filter_ajax),

    url(r'get_state_id/', get_state_id, name='get_state_id'),

    url(r'password_change/', AdminChangePassword.as_view(), name='Dashboard-PasswordChange'),
    url(r'coupon/', CouponsView.as_view(), name='Coupon_List'),

    url(r'^email_activate_link/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', email_activate, name='email_activate_link'),
    url('^updateVendorPassword/', updateVendorPassword, name='updateVendorPassword'),
    url(r'^preview_custom/$', CustomPaymentDetailsView.as_view(),name='previews'),
    url(r'^payment_cancel/$', payment_cancel, name='payment_cancel'),
    url(r'^payment_success/$', payment_success, name='payment_success'),
    url(r'^order_payment_cancel/$', PaymentCancelView.as_view(), name='order_payment_cancel'),

    url(r'product_blocked_dates/$', product_blocked_dates, name='product_blocked_dates'),
    url(r'product_blocked_dates_onsubmit/$', product_blocked_dates_onsubmit, name='product_blocked_dates_onsubmit'),

    url(r'export_events/$', export_events, name='export_events'),
    url(r'export_bookedevents/$', export_bookedevents, name='export_bookedevents'),
    url(r'export_coupon_data/$', export_coupon, name='export_coupon'),
    url(r'export_customcoupon_data/$', export_customcoupon_data, name='export_customcoupon_data'),
    url(r'export_season/$', export_season, name='export_season'),
    url(r'export_low_stock/$', export_low_stock, name='export_low_stock'),
    url(r'export_reviews/$', export_reviews, name='export_reviews'),
    url(r'export_orders/$', export_orders, name='export_orders'),
    url(r'export_units/$', export_units, name='export_units'),
    url(r'export_products/$', export_products, name='export_products'),
    url(r'export_categories/$', export_categories, name='export_categories'),
    url(r'export_category/$', export_category, name='export_category'),
    url(r'export_vendors/$', export_vendors, name='export_vendors'),
    url(r'export_customers/$', export_customers, name='export_customers'),
    url(r'export_users/$', export_users, name='export_users'),
    url(r'export_combo/$', export_combo, name='export_combo'),
    url(r'export_premium/$', export_premium, name='export_premium'),
    url(r'export_individualdb/$', export_individualdb, name='export_individualdb'),
    url(r'export_multidb/$', export_multidb, name='export_multidb'),
    url(r'export_menu/$', export_menu, name='export_menu'),
    url(r'export_exhibition_menu/$', export_exhibition_menu, name='export_exhibition_menu'),
    url(r'export_quote/$', export_quote, name='export_quote'),
    url(r'export_tax/$', export_tax, name='export_tax'),
    url(r'export_percentage/$', export_percentage, name='export_percentage'),
    url(r'export_attribute/$', export_attribute, name='export_attribute'),
    url(r'export_featured_products/$', export_featured_products, name='export_featured_products'),
    url(r'^export-coupon-distributors/$', export_distributors, name='export-coupon-distributors'),
    url(r'^export-price-range-db/$', export_price_range_db, name='export-price-range-db'),

    url(r'update_product/$', update_product, name='update_product'),
    url(r'delete_bulk_product/$', delete_bulk_product, name='delete_bulk_product'),
    url(r'delete_product_image/$', delete_product_image, name='delete_product_image'),
    url(r'delete_product_attribute/$', delete_product_attribute, name='delete_product_attribute'),
    url(r'remove_featured_product/$', remove_featured_product, name='remove_featured_product'),


    url(r'delete_bulk_category/$', delete_bulk_category, name='delete_bulk_category'),
    url(r'delete_bulk_reviews/$', delete_bulk_reviews, name='delete_bulk_reviews'),
    url(r'update_first_login/$', update_first_login, name='update_first_login'),

    url(r'delete_bulk_coupon_data/$', delete_bulk_coupon, name='delete_bulk_coupon'),
    url(r'delete_bulk_vendor/$', delete_bulk_vendor, name='delete_bulk_vendor'),
    url(r'delete_bulk_units/$', delete_bulk_units, name='delete_bulk_units'),
    url(r'delete_bulk_user/$', delete_bulk_user, name='delete_bulk_user'),
    url(r'delete_bulk_season/$', delete_bulk_season, name='delete_bulk_season'),
    url(r'delete_bulk_event/$', delete_bulk_event, name='delete_bulk_event'),
    url(r'sales_delete_bulk_event/$', sales_delete_bulk_event, name='sales_delete_bulk_event'),
    url(r'delete_bulk_combo_data/$', delete_bulk_combo_data, name='delete_bulk_combo_data'),
    url(r'delete_combo_product/$', delete_combo_product, name='delete_combo_product'),
    url(r'delete_bulk_menu_data/$', delete_bulk_menu_data, name='delete_bulk_menu_data'),
    url(r'delete_header_category/$', delete_header_category, name='delete_header_category'),

    url(r'export_rate_card_products/$', export_rate_card_products, name='export_rate_card_products'),
    url(r'^get_event_products_rate_card/$', get_event_products_rate_card, name='get_event_products_rate_card'),
    url(r'^get_products_for_featured/$', get_products_for_featured, name='get_products_for_featured'),
    url(r'^add_product_featured/$', add_product_featured, name='add_product_featured'),

    url(r'^get_products_order/$', get_products_order, name='get_products_order'),
    url(r'^get_vendors_best_quote/$', get_vendors_best_quote, name='get_vendors_best_quote'),

    url(r'^delete_bulk_costing_product/$', delete_bulk_costing_product, name='delete_bulk_costing_product'),
    url(r'^delete_bulk_costing_product_items/$', delete_bulk_costing_product_items, name='delete_bulk_costing_product_items'),
    url(r'^export_rate_card_products_items/$', export_rate_card_products_items, name='export_rate_card_products_items'),

    url(r'delete_bulk_premium_data/$', delete_bulk_premium_data, name='delete_bulk_premium_data'),
    url(r'delete_bulk_individual_data/$', delete_bulk_individual_data, name='delete_bulk_individual_data'),
    url(r'delete_bulk_multi_data/$', delete_bulk_multi_data, name='delete_bulk_multi_data'),
    url(r'delete_bulk_quote_data/$', delete_bulk_quote_data, name='delete_bulk_quote_data'),
    url(r'delete_bulk_tax_data/$', delete_bulk_tax_data, name='delete_bulk_tax_data'),
    url(r'delete_bulk_percentage_data/$', delete_bulk_percentage_data, name='delete_bulk_percentage_data'),
    url(r'delete_bulk_attribute_data/$', delete_bulk_attribute_data, name='delete_bulk_attribute_data'),
    url(r'delete_bulk_exhibition/$', delete_bulk_exhibition, name='delete_bulk_exhibition'),

    url(r'get_product_attribute/$', get_product_attribute, name='get_product_attribute'),

    url(r'delete_header_product/$', delete_header_product, name='delete_header_product'),

    url(r'allocate_vendor_sales/$', allocate_vendor_sales, name='allocate_vendor_sales'),
    url(r'vendor_re_allocate/$', vendor_re_allocate, name='vendor_re_allocate'),
    url(r'export_prime_bucket/$', export_prime_bucket, name='export_prime_bucket'),
    url(r'export_offers_prime_bucket/$', export_offers_prime_bucket, name='export_offers_prime_bucket'),

    url(r'^contact-us/$', ContactUsView.as_view(), name='contact-us'),
    url(r'^about_us/$', AboutUs.as_view(), name='about_us'),
    url(r'^terms-and-conditions/$', TermsPageView.as_view(), name='terms-and-conditions'),
    url(r'^faq/$', FQAView.as_view(), name='faq'),
    url(r'^policies/$', PoliciesView.as_view(), name='policies'),
    url(r'^how_it_works/$', HWorksView.as_view(), name='how_it_works'),
    url(r'^test_email/$', test_email, name='test_email'),
    url(r'^notes/$', add_admin_notes, name='add_admin_notes'),

    url(r'^create_note/$', create_note, name='create_note'),
    url(r'^admin_notes/$', admin_notes, name='admin_notes'),
    url(r'^deactivate_note/(?P<id>\d+)/$', deactivate_note, name='deactivate_note'),

    url(r'^get_event_products/$', get_event_products, name='get_event_products'),
    url(r'^load_products/$', load_products, name='load_products'),
    url(r'create_individual_db/$', individualdb_create.as_view(), name='create_individual_db'),
    url(r'create_multi_db/$', multidb_create.as_view(), name='create_multi_db'),
    url(r'find_details/$', find_details, name='find_details'),
    url(r'load_vendors/$', load_vendors, name='load_vendors'),
    url(r'load_categories/$', load_categories, name='load_categories'),
    url(r'allocate_vendor/$', allocate_vendor, name='allocate_vendor'),
    url(r'get_values_of_attribute/$', get_values_of_attribute, name='get_values_of_attribute'),
    url(r'get_total_price/$', get_total_price, name='get_total_price'),
    url(r'get_total_price_new/$', get_total_price_new, name='get_total_price_new'),
    url(r'set_is_discountable/$', set_is_discountable, name='set_is_discountable'),
    url(r'set_product_is_deleted/$', set_product_is_deleted, name='set_product_is_deleted'),
    url(r'test_email/$', test_email, name='test_email'),
    url(r'welcome_mail/$', welcome_mail, name='welcome_mail'),
    url(r'send_full_payment_email/$', send_full_payment_email, name='send_full_payment_email'),
    url(r'order_reminder/$', order_reminder, name='order_reminder'),

    url(r'cron-check/$', check_cron_view, name='check_cron_view'),
    url(r'abandoned-cart/$', abandoned_carts, name='abandoned-cart'),
    url(r'^create_pages/$', create_pages.as_view(), name='create_pages'),
    url(r'^get_transaction_details/$', get_transaction_details, name='create_pages'),
    url(r'^test_sms/$', test_sms, name='test_sms'),
    url(r'create_new_cart/(?P<pk>\d+)/$', create_new_cart.as_view(), name='create_new_cart'),
    url(r'get_coupondist/$', get_coupondist, name='get_coupondist'),
    url(r'get_coupondetails/$', get_coupondetails, name='get_coupondetails'),
    url(r'get_otp/$', get_otp, name='get_otp'),
    url(r'get_vendor_otp/$', get_vendor_otp, name='get_vendor_otp'),
    url(r'verify_otp/$', verify_otp, name='verify_otp'),

    url(r'delete_price/$', delete_price, name='delete_price'),
    url(r'delete_price_range/$', delete_price_range, name='delete_price_range'),
    url(r'delete_customize_category/$', delete_customize_category, name='delete_customize_category'),
    url(r'^export-price-filter/$', export_price_filter, name='export-price-filter'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)