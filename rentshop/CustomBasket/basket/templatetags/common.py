# python imports
import datetime
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

# django imports
from django import template
from datetime import datetime
from django.conf import settings
from django.db.models import Case, When, Value
from django.db.models import F
from django.utils.safestring import mark_safe
from django.db.models import Count, Min, Sum, Avg, Max
from django.db.models import Q
from django.db.models.functions import Length

# 3rd party imports
from math import ceil
from oscar.apps.customer import history
from oscar.core.loading import get_model, get_class
from oscar.core.compat import get_user_model

# template tag init
register = template.Library()

# model imports
Header = get_model('HeaderMenu', 'Admin_Header')
HeaderMenu = get_model('HeaderMenu', 'Admin_HeaderMenu')
HeaderSubMenu = get_model('HeaderMenu', 'Admin_HeaderSubMenu')
Coupon = get_model('voucher', 'Voucher')
Basket_Line = get_model('basket', 'Line')
Basket_Onj = get_model('basket', 'Basket')
StockRecord = get_model('partner', 'StockRecord')
MultiDB = get_model('partner', 'MultiDB')
IndividualDB = get_model('partner', 'IndividualDB')
VendorCalender = get_model('partner', 'VendorCalender')
Benefits = get_model('offer', 'Benefit')
Reviews = get_model('reviews', 'ProductReview')
Product = get_model('catalogue', 'Product')
Partner = get_model('partner', 'Partner')
Category = get_model('catalogue', 'category')
ProductCategory = get_model('catalogue', 'ProductCategory')
PremiumProducts = get_model('catalogue', 'PremiumProducts')
OrderAllocatedVendor = get_model('order', 'OrderAllocatedVendor')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')

User = get_user_model()
Notes = get_model('customer', 'Notes')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')
Attribute = get_model('catalogue', 'Attribute')
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')
CategoriesWiseFilterValue = get_model('catalogue', 'CategoriesWiseFilterValue')

ProductReviewForm = get_class('catalogue.forms','CustomProductReviewForm')

@register.simple_tag
def line_item_checker(request, value):
    if not request.user.is_anonymous:
        basket_i = Basket_Onj.objects.filter(owner=request.user, status='Open').values_list('id')
        in_basket = Basket_Line.objects.filter(product=value.id, basket_id__in=basket_i)
        return in_basket
    else:
        basket_i = Basket_Onj.objects.filter(owner=None, status='Open').values_list('id')
        in_basket = Basket_Line.objects.filter(product=value.id, basket_id__in=basket_i)
        return in_basket


@register.simple_tag
def wish_list_price(request, value):
    ids = [value]
    stock_obj = StockRecord.objects.filter(product_id__in=ids)

    return stock_obj


@register.simple_tag
def header_tag():
    header_obj = Header.objects.all().order_by('sequence_number')
    return header_obj


@register.filter
def coupon_value(value):
    benefits_id = Benefits.objects.filter(id=value)
    return benefits_id


@register.filter
def header_sub(value):
    headermenu = HeaderMenu.objects.filter(title_id=value).order_by('sub_title')
    return headermenu


@register.filter
def header_submenu(value):
    headersubmenu = HeaderSubMenu.objects.filter(header_menu_id=value).order_by('sub_menu_title')
    return headersubmenu


@register.simple_tag
def coupon():
    coupon = Coupon.objects.filter(end_datetime__gte=datetime.now())

    return coupon


@register.inclusion_tag('customer/history/recently_view_home.html', takes_context=True)
def recently_viewed_products(context, current_product=None):
    request = context['request']
    products = history.get(request)
    filter_product = []

    cat_obj = Category.objects.filter(show_on_frontside=True, depth=1)
    cat_list = []
    for category in cat_obj:
        id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
        for element in id_list:
            cat_list.append(element)
    for p in products:
        front_side = True
        for cat in p.get_categories().all():
            if cat.id not in cat_list:
                front_side = False
                break

        if p.stockrecords.all() and p.is_approved == "Approved" and front_side :
            filter_product.append(p)

    if current_product:
        filter_product = [p for p in filter_product if p != current_product]
    return {'products': filter_product,
            'request': request}


@register.simple_tag
def universe():
    return settings


@register.simple_tag
def footer_text():
    current_year = datetime.now().year
    last_year = current_year - 1

    foot_year = str(last_year) + '-' + str(current_year)

    return 'Copyright © %s Take Rent Pe, All rights reserved' % (foot_year)


@register.simple_tag
def contact_info():
    data = {
        'email': 'admin@takerentpe.com',
        'number': '+91-7378989996'
    }

    return data


@register.simple_tag
def review_list():
    re = Reviews.objects.order_by('user_id').distinct('user_id')

    reviews = re.filter(status = 1, product__is_deleted = False, product__is_approved = 'Approved')
    return reviews[:7]


@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


@register.simple_tag
def freeze_product(product):
    freeze = True

    try:

        product = Product.objects.get(id=product)
        # check if is is freeze by vendor
        is_freeze = VendorCalender.objects.filter(product=product)

        is_freeze = is_freeze.filter(
            from_date__date__lte=datetime.now().date(),
            to_date__date__gte=datetime.now().date()
        )

        if is_freeze:
            return freeze
        else:
            freeze = False
            return freeze

    except Exception as e:
        print(e.args)
        return freeze


@register.simple_tag
def get_vendor(user):
    try:

        user = User.objects.get(id=user, is_staff=True)
        vendor = Partner.objects.filter(users=user)
        vendor = vendor.last()

        return vendor

    except Exception as e:

        return None


@register.simple_tag
def category_header_tree():
    return Category.objects.filter(depth=1, show_on_frontside=True).order_by('master_sequence', 'path')


@register.simple_tag
def category_child(parent_id):
    if parent_id == 14:
        parent = Category.objects.get(id=239)
    else:
        parent = Category.objects.get(id=parent_id)

    return parent.get_children


@register.simple_tag
def get_tomorrows_notes(request_data):
    today_date = datetime.now()
    next_4_hr = today_date + timedelta(hours=4)
    next_12_hr = today_date + timedelta(hours=12)
    next_8_hr = today_date + timedelta(hours=8)
    next_24_hr = today_date + timedelta(hours=24)
    next_48_hr = today_date + timedelta(hours=48)

    data = Notes.objects.filter(
        start_date__range=[next_12_hr, next_48_hr],
        is_active=True
    )

    if data:
        return data
    else:
        return None


@register.simple_tag
def get_premium_product(products):
    for product in products:
        cat = ProductCategory.objects.filter(product_id=product.id)

    if cat:

        data1 = PremiumProducts.objects.filter(category=cat.last().category)
        if data1:
            premium_data = data1.last().product.filter(is_approved = 'Approved',is_deleted = False)
            return premium_data
    return None


@register.simple_tag
def get_product_sorted(products):
    for product in products:
        cat = ProductCategory.objects.filter(product_id=product.id)
        if cat:
            arr = []
            list1 = dict()
            data1 = PremiumProducts.objects.filter(category=cat.last().category)

            if data1:
                premium_data = data1.last().product.all()

                final_product = Product.objects.filter(id__in=products,is_deleted=False).exclude(id__in=premium_data).order_by(
                    'stockrecords__price_excl_tax', 'stockrecords__sale_price_with_tax', 'stockrecords__rent_price', )

            else:

                final_product = Product.objects.filter(id__in=products, is_deleted=False).order_by('stockrecords__sale_price_with_tax',
                                                                                 'stockrecords__rent_price_with_tax',
                                                                                 'stockrecords__rent_price')

            final_product = final_product.annotate(
                price_order=Case(When(product_class_id__name='Sale', then=F('stockrecords__price_excl_tax')),
                                 default=F('stockrecords__rent_price'), ),
            ).order_by('price_order')

            for final in final_product:
                base_price = get_price_for_sort(final.stockrecords.last())
                arr.append(base_price)
                list1[final.id] = base_price
            a = sorted(list1.items(), key=lambda x: x[1])

            p_id = list()
            for item in a:
                p_id.append(item[0])

            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(p_id)])
            final_product = Product.objects.filter(id__in=p_id, is_deleted=False).order_by(preserved)

            return final_product

        return products


@register.simple_tag
def get_price_for_sort(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return sale_price

        # for sale
        if price.product.product_class.name == 'Rent':
            return rent_price

        # for professional
        if price.product.product_class.name == 'Professional':
            return rent_price

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':
            return rent_price

        return cost

    except Exception as e:

        return cost


@register.simple_tag
def get_price_whole(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return '{:,.2f}'.format(sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return '{:,.2f}'.format(rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return '{:,.2f}'.format(rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':
            a = mark_safe('%s/<br/> ₹ %s' % ('{:,.2f}'.format(rent_price), '{:,.2f}'.format(sale_price)))
            return a
            return '%s/<br/> ₹ %s' % ('{:,.2f}'.format(rent_price), '{:,.2f}'.format(sale_price))

        return cost

    except Exception as e:

        return cost

@register.simple_tag
def get_price_whole_browse(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return '{:,.2f}'.format(sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return '{:,.2f}'.format(rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return '{:,.2f}'.format(rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':
            return '%s/ ₹ %s' % ('{:,.2f}'.format(rent_price), '{:,.2f}'.format(sale_price))

        return cost

    except Exception as e:

        return cost

@register.simple_tag
def get_price_whole_details(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return '{:,.2f}'.format(sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return '{:,.2f}'.format(rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return '{:,.2f}'.format(rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':

            return '%s/ ₹ %s' % ('{:,.2f}'.format(rent_price), '{:,.2f}'.format(sale_price))

        return cost

    except Exception as e:

        return cost


@register.simple_tag
def get_price_whole_int(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return (sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return (rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return (rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':
            return (rent_price, sale_price)

        return (cost)

    except Exception as e:

        return cost


@register.simple_tag
def get_rent_price(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return '{:,.2f}'.format(sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return '{:,.2f}'.format(rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return '{:,.2f}'.format(rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':
            return '{:,.2f}'.format(rent_price)

        return cost

    except Exception as e:

        return cost


@register.simple_tag
def get_price_whole_for_cart(price, type):
    rent_price, sale_price = 0, 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if type == 'Sale':
            return '{:,.2f}'.format(sale_price)

        # for sale
        if type == 'Rent':
            return '{:,.2f}'.format(rent_price)

        # for professional
        if type == 'Professional':
            return '{:,.2f}'.format(rent_price)

        # for rent sale

        return cost

    except Exception as e:

        return cost


@register.simple_tag
def freeze_product_capacity(product):
    """
    Template tag to check rent product capacity
    :param product: product object
    :return: boolean
    """

    is_available = True

    try:

        if product.is_approved != 'Approved':
            return True

        if product.product_class == 'Sale':
            return False

        vendor_calendar = VendorCalender.objects.filter(product=product)
        vendor_calendar = vendor_calendar.filter(from_date__date__lte=datetime.now().date(),
                                                 to_date__date__gte=datetime.now().date())

        if vendor_calendar:
            return True

        today_date = datetime.now()

        orders = Order.objects.all().values_list('id', flat=True)
        order_lines = Line.objects.filter(order__id__in=orders)
        order_lines = order_lines.exclude(product__product_class__name=['Sale', 'Service'])

        placed_order_lines = order_lines.filter(product=product, booking_start_date__date__lte=today_date,
                                                booking_end_date__date__gte=today_date)

        if placed_order_lines.count() >= product.daily_capacity:
            return True

        return False

    except Exception as e:

        print('--------------- Error in product freeze template tag ---------------')
        print(e.args)
        print('--------------- Error in product freeze template tag ---------------')

    return is_available


@register.simple_tag
def product_category_asp(category):
    status = True
    message = 'No ASP found.'

    try:

        indi = IndividualDB.objects.filter(category=category)
        multi = MultiDB.objects.filter(category=category)

        if not indi and not multi:
            status = 3
            message = 'No ASP found.'
            return {'status': status, 'message': message}

        if indi and multi:
            status = False
            message = 'Invalid ASP Data.'
            return {'status': status, 'message': message}

        if multi:
            status = True
            multi = multi.last()
            message = 'Front liners: %s, Backup one: %s, Backup two: %s' % (
                multi.frontliener.filter(users__is_active = True).count(),
                multi.backup1.filter(users__is_active = True).count(),
                multi.backup2.filter(users__is_active = True).count(),
            )
            return {'status': status, 'message': message}

        if indi:
            status = 2
            message = indi.last().individual_asp.last()
            return {'status': status, 'message': message}

        # if indi:
        #     status = 4
        #     indi = indi.last()
        #     message = 'Individual: %s' % (
        #         indi.individual_asp.filter(users__is_active = True).count()
        #     )
        #     return {'status': status, 'message': message}


    except Exception as e:

        status = False

    return {
        'status': status,
        'message': message
    }


@register.simple_tag
def product_category_asp_data(order_line):
    try:

        ml_vendors_list, ml_vendors_list_existed = [], []
        b1_vendors_list, b1_vendors_list_existed = [], []
        b2_vendors_list, b2_vendors_list_existed = [], []

        order_product = order_line.product
        product_category = order_product.categories.last()

        multi_data = MultiDB.objects.filter(category=product_category)
        multi_data = multi_data.last()

        allocated_vendors = OrderAllocatedVendor.objects.filter(product_category=product_category)
        allocated_vendors_list = list(allocated_vendors.values_list('vendor__id', flat=True))
        allocated_vendors_list = list(set(allocated_vendors_list))

        # list of front liner
        for ml_vendor in multi_data.frontliener.filter(users__is_active = True):

            if ml_vendor.id not in allocated_vendors_list:
                ml_vendors_dict = dict()
                ml_vendors_dict['name'] = ml_vendor.name
                ml_vendors_dict['id'] = ml_vendor.id
                ml_vendors_list.append(ml_vendors_dict)
            else:
                ml_vendors_dict = dict()
                ml_vendors_dict['name'] = ml_vendor.name
                ml_vendors_dict['id'] = ml_vendor.id
                ml_vendors_list_existed.append(ml_vendors_dict)

        if ml_vendors_list_existed:
            ml_vendors_list.extend(ml_vendors_list_existed)
        # list of front liner

        # list of b1
        for b1_vendor in multi_data.backup1.filter(users__is_active = True):

            if b1_vendor.id not in allocated_vendors_list:
                b1_vendors_dict = dict()
                b1_vendors_dict['name'] = b1_vendor.name
                b1_vendors_dict['id'] = b1_vendor.id
                b1_vendors_list.append(b1_vendors_dict)
            else:
                b1_vendors_dict = dict()
                b1_vendors_dict['name'] = b1_vendor.name
                b1_vendors_dict['id'] = b1_vendor.id
                b1_vendors_list_existed.append(b1_vendors_dict)

        if b1_vendors_list_existed:
            b1_vendors_list.extend(b1_vendors_list_existed)
        # list of b1

        # list of b2
        for b2_vendor in multi_data.backup2.filter(users__is_active = True):

            if b2_vendor.id not in allocated_vendors_list:
                b2_vendors_dict = dict()
                b2_vendors_dict['name'] = b2_vendor.name
                b2_vendors_dict['id'] = b2_vendor.id
                b2_vendors_list.append(b2_vendors_dict)
            else:
                b2_vendors_dict = dict()
                b2_vendors_dict['name'] = b2_vendor.name
                b2_vendors_dict['id'] = b2_vendor.id
                b2_vendors_list_existed.append(b2_vendors_dict)

        if b2_vendors_list_existed:
            b2_vendors_list.extend(b2_vendors_list_existed)
        # list of b2

        vendors = {
            'front_liner': ml_vendors_list,
            'backup_1': b1_vendors_list,
            'backup_2': b2_vendors_list,
        }

        return vendors

    except Exception as e:
        print(e.args)

        return {
            'front_liner': [],
            'backup_1': [],
            'backup_2': [],
        }


@register.simple_tag
def product_category_indiasp_data(order_line):
    try:

        ml_vendors_list, ml_vendors_list_existed = [], []

        order_product = order_line.product
        product_category = order_product.categories.last()

        indi_data = IndividualDB.objects.filter(category=product_category)
        indi_data = indi_data.last()
        existing_values = OrderAllocatedVendor.objects.filter(order_line=order_line).values_list('vendor__id')

        part_obj = Partner.objects.filter(users__is_active= True).exclude(id__in = existing_values)

        allocated_vendors = OrderAllocatedVendor.objects.filter(product_category=product_category)
        allocated_vendors_list = list(allocated_vendors.values_list('vendor__id', flat=True))
        allocated_vendors_list = list(set(allocated_vendors_list))

        # list of front liner
        for ml_vendor in part_obj:
            if ml_vendor.id not in allocated_vendors_list:

                ml_vendors_dict = dict()
                ml_vendors_dict['name'] = ml_vendor.name
                ml_vendors_dict['id'] = ml_vendor.id
                ml_vendors_list.append(ml_vendors_dict)
            else:

                ml_vendors_dict = dict()
                ml_vendors_dict['name'] = ml_vendor.name
                ml_vendors_dict['id'] = ml_vendor.id
                ml_vendors_list_existed.append(ml_vendors_dict)

        if ml_vendors_list_existed:
            ml_vendors_list.extend(ml_vendors_list_existed)
        # list of front liner

        vendors = {
            'indi_liner': ml_vendors_list,
        }
        return vendors

    except Exception as e:
        print(e.args)

        return {
            'indi_liner': [],
        }

@register.simple_tag
def logo_url(request):
    return settings.LOGO_URL


@register.simple_tag
def get_attribute(request):
    attribute_obj = Attribute_Mapping.objects.filter(product__upc=request)

    att_dict = dict()

    if attribute_obj:

        list_obj = list()
        color_dict = {'pink' : '#FFC0CB','red':'#FF0000','yellow' :'#FFFF00','purple' :'#800080','golden':'#FFD700'}
        for obj in attribute_obj:

            wordList = re.split("[^\w\# ]", obj.value)
            for word in wordList:
                if word == '' or word == ' ':
                    continue
                if word.lower() in  color_dict.keys():
                    word = color_dict[word.lower()]
                if obj.attribute in att_dict.keys():

                    att_dict[obj.attribute].append(word)
                else:
                    att_dict[obj.attribute] = [word]

        return att_dict

    return None



@register.simple_tag
def get_saving_price(price):
    if price:

        if price.product.product_class.name == 'Sale':
            if price.sale_total_saving and price.sale_market_price:
                return True
        if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
            if price.rent_market_price and price.rent_total_saving:
                return True
        if price.product.product_class.name == 'Rent Or Sale':

            if (price.sale_total_saving and price.sale_market_price) or (
                    price.rent_market_price and price.rent_total_saving):
                return True

    return False


@register.simple_tag
def check_end(request):
    if request and request.endswith('/basket/'):
        return True
    return False


@register.simple_tag
def get_total_cost(price):
    if price:

        if not price.product.product_cost_type == 'Multiple':
            quantity = 1

            if price.product.product_class.name in ['Rent', 'Professional', 'Sale']:
                price1 = get_price_for_sort(price)
                shipping_price = get_product_shipping(price, price.product.product_class.name, 1)
                if price1 and quantity and shipping_price:
                    total = (price1 * quantity) + shipping_price
                elif price1 and quantity and not shipping_price:
                    total = (price1 * quantity)
                elif price1 and not quantity and shipping_price:
                    total = price1 + shipping_price
                else:
                    total = price1
                total = '{:,.2f}'.format(total)
            else:
                if price.sale_price_with_tax and price.sale_round_off_price:
                    sale_price = price.sale_price_with_tax + price.sale_round_off_price
                if price.sale_price_with_tax and not price.sale_round_off_price:
                    sale_price = round(price.sale_price_with_tax)
                if not price.sale_price_with_tax and price.price_excl_tax:
                    sale_price = round(price.price_excl_tax)

                if price.rent_price_with_tax and price.rent_round_off_price:
                    rent_price = price.rent_price_with_tax + price.rent_round_off_price
                if price.rent_price_with_tax and not price.rent_round_off_price:
                    rent_price = round(price.rent_price_with_tax)
                if not price.rent_price_with_tax and price.rent_price:
                    rent_price = round(price.rent_price)

                total1 = (rent_price * quantity) + get_product_shipping(price, "Rent", 1)
                total2 = (sale_price * quantity) + get_product_shipping(price, "Sale", 1)
                total = '%s/ ₹ %s' % ('{:,.2f}'.format(total1), '{:,.2f}'.format(total2))
            return total
        else:
            quantity = get_quantity_for_multiple(price)

            if price.product.product_class.name in ['Rent', 'Professional', 'Sale']:
                price1 = get_price_whole_total_cost_multiple(price,quantity)
                shipping_price = get_product_shipping(price, price.product.product_class.name, quantity)
                # if price1 and quantity and shipping_price:
                #     total = price1 + shipping_price
                # elif price1 and quantity and not shipping_price:
                #     total = price1
                # elif price1 and not quantity and shipping_price:
                #     total = price1
                # else:
                #     total = price1
                # if total:
                #     total = '{:,.2f}'.format(total)
                # else:
                #     total = 0
                # changes added for multiple quantity
                if price1 and quantity and shipping_price:
                    total = (price1 * quantity) + shipping_price
                elif price1 and quantity and not shipping_price:
                    total = (price1 * quantity)
                elif price1 and not quantity and shipping_price:
                    total = price1 + shipping_price
                else:
                    total = price1
                if total:
                    total = '{:,.2f}'.format(total)
                else:
                    total = 0
            else:
                total1, total2 = 0 , 0
                price1 = get_price_whole_total_cost_multiple(price, quantity)
                rent_shipping = get_product_shipping(price, "Rent", quantity)
                sale_shipping = get_product_shipping(price, "Sale", quantity)
                # if price1['rent_price'] and price1['sale_price'] and rent_shipping and sale_shipping:
                #
                #     total1 = price1['rent_price'] + rent_shipping
                #     total2 = price1['sale_price'] + sale_shipping
                # if price1['rent_price'] and price1['sale_price'] and rent_shipping and not sale_shipping:
                #     total1 = price1['rent_price'] + rent_shipping
                #     total2 = price1['sale_price']
                # if price1['rent_price'] and price1['sale_price'] and not rent_shipping and sale_shipping:
                #     total1 =  price1['rent_price']
                #     total2 = price1['sale_price'] + sale_shipping
                # if price1['rent_price'] and price1['sale_price'] and not rent_shipping and not sale_shipping:
                #
                #     total1 = price1['rent_price']
                #     total2 = price1['sale_price']

                if price1['rent_price'] and price1['sale_price'] and rent_shipping and sale_shipping:

                    total1 = (price1['rent_price'] * quantity) + rent_shipping
                    total2 = (price1['sale_price'] * quantity) + sale_shipping
                if price1['rent_price'] and price1['sale_price'] and rent_shipping and not sale_shipping:
                    total1 = (price1['rent_price'] * quantity) + rent_shipping
                    total2 = (price1['sale_price'] * quantity)
                if price1['rent_price'] and price1['sale_price'] and not rent_shipping and sale_shipping:
                    total1 =  (price1['rent_price'] * quantity)
                    total2 = (price1['sale_price'] * quantity)+ sale_shipping
                if price1['rent_price'] and price1['sale_price'] and not rent_shipping and not sale_shipping:

                    total1 = (price1['rent_price']* quantity)
                    total2 = (price1['sale_price'] * quantity)

                if total1 and total2:

                    total = '%s/ ₹ %s' % ('{:,.2f}'.format(total1), '{:,.2f}'.format(total2))
                else:
                    total = 0

            return total
    return False


@register.simple_tag
def get_shipping_price(price):
    if price and price.product.is_transporation_available:
        if price.product.product_cost_type == 'Multiple':
            quantity = get_quantity_for_multiple(price)
            if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
                shipping_price1 = get_product_shipping(price, 'Rent', quantity)
                if shipping_price1:
                    return '₹ %s' %('{:,.2f}'.format(shipping_price1))
            elif price.product.product_class.name == 'Sale':
                shipping_price2 = get_product_shipping(price, 'Sale', quantity)
                if shipping_price2:
                    return '₹ %s' %('{:,.2f}'.format(shipping_price2))
            else:
                shipping_price1 = get_product_shipping(price, 'Rent', quantity)
                shipping_price2 = get_product_shipping(price, 'Sale', quantity)
                if shipping_price1 and shipping_price2:
                    return '₹ %s/ ₹ %s' % ('{:,.2f}'.format(shipping_price1), '{:,.2f}'.format(shipping_price2))
                elif shipping_price1 and not shipping_price2:
                    return '₹ %s/ %s' % ('{:,.2f}'.format(shipping_price1), 'free sale shipping')
                elif not shipping_price1 and shipping_price2:
                    return ' %s/ ₹ %s' % ('free rent shipping','{:,.2f}'.format(shipping_price2))
                else:
                    return 0


        elif price.product.product_cost_type == 'Single':
            if price.product.product_class.name in ['Rent', 'Professional']:
                if price.rent_transportation_price:
                    shipping_price = price.rent_transportation_price
                    if shipping_price:
                        return '₹ %s' %('{:,.2f}'.format(shipping_price))
            elif price.product.product_class.name == 'Sale':
                if price.sale_transportation_price:
                    shipping_price = price.sale_transportation_price
                    if shipping_price:
                        return '₹ %s' %('{:,.2f}'.format(shipping_price))
            else:
                if price.rent_transportation_price and price.sale_transportation_price:
                    shipping_price1 = price.rent_transportation_price
                    shipping_price2 = price.sale_transportation_price
                    return '₹ %s/ ₹ %s' % ('{:,.2f}'.format(shipping_price1), '{:,.2f}'.format(shipping_price2))
                elif price.rent_transportation_price and not price.sale_transportation_price:
                    shipping_price1 = price.rent_transportation_price
                    return '₹ %s/ %s' % ('{:,.2f}'.format(shipping_price1), 'free sale shipping')
                elif not price.rent_transportation_price and price.sale_transportation_price:
                    shipping_price2 = price.sale_transportation_price
                    return '%s/ ₹ %s' % ('free rent shipping','{:,.2f}'.format(shipping_price2))
        return 0


@register.simple_tag
def get_shipping_price_total(price):
    if price and price.product.is_transporation_available:
        quantity = get_quantity_for_multiple(price)
        if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
            shipping_price1 = get_product_shipping(price, 'Rent', quantity)
            return '₹ %s' % ('{:,.2f}'.format(round(shipping_price1,0)))
        elif price.product.product_class.name == 'Sale':
            shipping_price2 = get_product_shipping(price, 'Sale', quantity)
            return '₹ %s' % ('{:,.2f}'.format(round(shipping_price2,0)))
        else:
            shipping_price1 = get_product_shipping(price, 'Rent', quantity)
            shipping_price2 = get_product_shipping(price, 'Sale', quantity)

            return '₹ %s/ ₹ %s' % ('{:,.2f}'.format(round(shipping_price1,0)), '{:,.2f}'.format(round(shipping_price2,0)))

        return 0

@register.simple_tag
def get_product_shipping(price, type, quantity):
    ship_sale_price, ship_rent_price = 0, 0
    if price:
        costs_product = ProductCostEntries.objects.filter(product=price.product)

        if price.product.product_cost_type == 'Multiple':

            if type == 'Sale':
                costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity, requirement_day__gte = 1).order_by('-requirement_day')
                if not costs:
                    costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity).order_by('requirement_day')

                if costs and price.product.is_transporation_available:
                    costs = costs.last()
                    ship_sale_price = costs.transport_cost if costs.transport_cost else 0
                return ship_sale_price

            if type == 'Rent':

                costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity, rent_requirement_day__gte = 1).order_by('-rent_requirement_day')
                if not costs:
                    costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity).order_by('rent_requirement_day')

                if costs and price.product.is_transporation_available:
                    costs = costs.last()
                    ship_rent_price = costs.rent_transport_cost if costs.rent_transport_cost else 0
                return ship_rent_price

        elif price.product.product_cost_type == 'Single':
            if type == 'Sale':
                if price.sale_transportation_price and price.product.is_transporation_available:
                    ship_sale_price = price.sale_transportation_price
                return ship_sale_price

            if type == 'Rent':
                if price.rent_transportation_price and price.product.is_transporation_available:
                    ship_rent_price = price.rent_transportation_price
                return ship_rent_price
    return 0


@register.simple_tag
def get_price_whole_total_cost(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return (sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return (rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return (rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':
            context = {
                'rent_price': rent_price,
                'sale_price': sale_price
            }
            return context

        return (cost)

    except Exception as e:

        return cost


@register.simple_tag
def get_product_cost_multiple(price):
    quantity = get_quantity_for_multiple(price)
    if price and price.product.product_cost_type == 'Multiple':
        if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            if rent_total_cost:
                return '%s ' % ('{:,.2f}'.format(round(rent_total_cost,0)))
            else:
                return 0
        elif price.product.product_class.name == 'Sale':
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            if sale_total_cost:
                return '%s ' % ('{:,.2f}'.format(round(sale_total_cost,0)))

            else:
                return 0
        else:
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            if rent_total_cost and sale_total_cost:
                return '%s/ ₹ %s' % ('{:,.2f}'.format(round(rent_total_cost,0)), '{:,.2f}'.format(round(sale_total_cost,0)))
            elif rent_total_cost and not sale_total_cost:
                return '%s ' % ('{:,.2f}'.format(round(rent_total_cost,0)))
            elif not rent_total_cost and sale_total_cost:
                return '%s' % ('{:,.2f}'.format(round(sale_total_cost,0)))
            else:
                return 0

    return False

@register.simple_tag
def get_product_cost_multiple_with_quantity(price):
    quantity = get_quantity_for_multiple(price)
    if price and price.product.product_cost_type == 'Multiple':
        if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            if rent_total_cost:
                return '%s ' % ('{:,.2f}'.format(round(rent_total_cost*quantity,0)))
            else:
                return 0
        elif price.product.product_class.name == 'Sale':
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            if sale_total_cost:
                return '%s ' % ('{:,.2f}'.format(round(sale_total_cost*quantity,0)))

            else:
                return 0
        else:
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            if rent_total_cost and sale_total_cost:
                return '%s/ ₹ %s' % ('{:,.2f}'.format(round(rent_total_cost*quantity,0)), '{:,.2f}'.format(round(sale_total_cost*quantity,0)))
            elif rent_total_cost and not sale_total_cost:
                return '%s ' % ('{:,.2f}'.format(round(rent_total_cost*quantity,0)))
            elif not rent_total_cost and sale_total_cost:
                return '%s' % ('{:,.2f}'.format(round(sale_total_cost*quantity,0)))
            else:
                return 0

    return False


@register.simple_tag
def get_price_whole_total_cost_multiple(price,quantity):
    cost = 0
    if price and price.product.product_cost_type == 'Multiple':
        if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            return rent_total_cost
        elif price.product.product_class.name == 'Sale':
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            return sale_total_cost
        else:
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            context = {
                'rent_price': rent_total_cost,
                'sale_price': sale_total_cost
            }
            return context

    return cost


@register.simple_tag
def get_product_cost(price, type, quantity):
    product_sale_price, product_rent_price = 0, 0

    costs_filter = ProductCostEntries.objects.filter(product=price.product)
    if price.product.product_cost_type == 'Multiple':

        if type == 'Sale':
            costs = costs_filter.filter(quantity_from__lte=quantity, quantity_to__gte=quantity, requirement_day__gte = 1 ).order_by('-requirement_day')
            if not costs:
                costs = costs_filter.filter(quantity_from__lte=quantity, quantity_to__gte=quantity).order_by('requirement_day')

            if costs and costs.last().cost_incl_tax:
                costs = costs.last()
                product_sale_price = costs.cost_incl_tax
            else:
                if price.sale_price_with_tax and price.sale_round_off_price:
                    sale_price = price.sale_price_with_tax + price.sale_round_off_price
                if price.sale_price_with_tax and not price.sale_round_off_price:
                    sale_price = round(price.sale_price_with_tax)
                if not price.sale_price_with_tax and price.price_excl_tax:
                    sale_price = round(price.price_excl_tax)
                product_sale_price = sale_price

            return product_sale_price

        if type == 'Rent':

            costs = costs_filter.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity, rent_requirement_day__gte = 1 ).order_by('-rent_requirement_day')
            if not costs:
                costs = costs_filter.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity).order_by('rent_requirement_day')

            if costs and costs.last().rent_cost_incl_tax:
                costs = costs.last()
                product_rent_price = costs.rent_cost_incl_tax

            else:
                if price.rent_price_with_tax and price.rent_round_off_price:
                    rent_price = price.rent_price_with_tax + price.rent_round_off_price
                if price.rent_price_with_tax and not price.rent_round_off_price:
                    rent_price = round(price.rent_price_with_tax)
                if not price.rent_price_with_tax and price.rent_price:
                    rent_price = round(price.rent_price)
                product_rent_price = rent_price

            return product_rent_price
    return 0


@register.simple_tag
def check_selected(item, value):

    if value and item.data['value'] in value:
        item.data['selected'] = True
        return item
    return item

@register.simple_tag
def check_selected_filter(item, value):
    import json
    if item and value:
        data = json.loads(value)
        for items in data:
            for key in items:
                if value and item == items[key]:
                    return True
    return False


@register.simple_tag
def get_quantity_for_multiple(price):
    min_quant = 1
    if price:
        costs = ProductCostEntries.objects.filter(product=price.product)
        if costs:
            if price.product.product_class.name in ['Rent', 'Professional']:
                min_quantity = costs.aggregate(Min('rent_quantity_from'))

                if min_quantity['rent_quantity_from__min']:

                    min_quant = min_quantity['rent_quantity_from__min']
                else:
                    min_quant = 1


            elif price.product.product_class.name == 'Sale':
                min_quantity = costs.aggregate(Min('quantity_from'))

                if min_quantity['quantity_from__min']:
                    min_quant = min_quantity['quantity_from__min']
                else:
                    min_quant = 1
            else:
                min_quantity_rent = costs.aggregate(Min('rent_quantity_from'))

                if min_quantity_rent['rent_quantity_from__min']:

                    min_quant = min_quantity_rent['rent_quantity_from__min']
                else:
                    min_quant = 1
        else:
            min_quant = 1
    return min_quant

@register.simple_tag
def check_stock(products):
    zero_stock = products.exclude(is_deleted = True)
    return zero_stock


@register.simple_tag
def get_order_invoice_totals(order, vendor, order_line= None):

    from num2words import num2words
    tax_total, final_total, final_total_word, shipping_total = 0, 0, '', 0
    tax_amount_total = 0
    if order and vendor:

        lines = Line.objects.filter(order=order, partner=vendor)

        for line in lines:
            if order_line == line:
                if line.shipping_charges:
                    shipping_total = shipping_total + line.shipping_charges
                    tax_total = line.shipping_tax_price
                if line.tax_amount:
                    if line.tax_percentage and line.tax_percentage > 6:
                        tax_total = tax_total + line.tax_amount

                if line.line_price_incl_tax:
                    final_total = final_total + line.line_price_incl_tax

        final_total_word = num2words(final_total + shipping_total).title()

    return {
        'tax_total': tax_total,
        'final_total': final_total + shipping_total,
        'final_total_word': final_total_word
    }


@register.simple_tag
def get_invoice_title(order, vendor):
    invoice_dict = {
        'title': 'Tax Invoice/Bill of Supply',
        'type': 'regular'
    }
    try:

        lines = Line.objects.filter(order=order, partner=vendor)

        for line in lines:
            if line.tax_percentage and line.tax_percentage <= 6:
                invoice_dict['title'] = 'Composition Taxable Person/Bill of Supply'
                invoice_dict['type'] = 'composition'
                return invoice_dict

        return invoice_dict

    except:

        return invoice_dict

@register.simple_tag
def get_logo_url(request):

    context = {
        'logo_url': settings.EMAIL_LOGO_URL,
        'footer_url': settings.EMAIL_FOOTER_LOGO_URL,
    }
    return context

@register.simple_tag
def congo_img(request):

    return settings.CONGRATULATION_IMG

@register.simple_tag
def site_url(request):

    return settings.SITE_URL

@register.simple_tag
def get_social_link(request):

    context = {
        'fb_link': settings.TRP_FB_LINK1,
        'twitter_link': settings.TRP_TWITTER_LINK1,
        'youtube_link': settings.TRP_YOUTUBE_LINK1,
        'insta_link': settings.TRP_INSTA_LINK1,
    }
    return context

@register.simple_tag
def get_category_wise_filter(category):
    if category:

        filter_dict = dict()
        cat_obj = CategoriesWiseFilterValue.objects.filter(category = category).values_list('filter_names', flat= True)
        if cat_obj:
            obj = cat_obj.last()

            wordList = re.split("[^\w\# ]", obj)

            for word in wordList:
                attr_obj = Attribute.objects.filter(attribute = word).values_list('value', flat=True)
                for attr in attr_obj:
                    if word in filter_dict.keys():
                        filter_dict[word].append(attr)
                    else:
                        filter_dict[word] = [attr]
            return filter_dict

    return False

@register.simple_tag
def get_allocated_vendor_line(value, order_line):
    """Allows to update existing variable in template"""

    if value:
        return value.filter(order_line= order_line)
    return False

@register.simple_tag
def signature_img(request):
    return settings.SIGNATURE_IMG


@register.simple_tag
def get_only_related_values(attribute, atriibute_form_values, value_list):
    if value_list:

        obj = Attribute.objects.filter(id=attribute)
        obj1 = Attribute.objects.filter(attribute=obj.last().attribute).values_list('value', flat=True)
        if obj1:

            return obj1
    return False


@register.simple_tag
def split_to_4_columns():
    values = list(Category.objects.filter(show_on_frontside=True, depth= 1).order_by(Length('name').asc()))
    split = int(ceil(len(values)/4.))
    columns = [values[i*split:(i+1)*split] for i in range(4)]
    return columns

@register.simple_tag
def get_price_whole_new_design(price, type):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if type == 'Rent':
            return '{:,.2f}'.format(rent_price)

        if type == 'Sale':
            return '{:,.2f}'.format(sale_price)


        return cost

    except Exception as e:
        print(e.args)
        return cost

@register.simple_tag
def split_all_to_4_columns():
    cat_obj= Category.objects.filter(show_on_frontside=True, depth=1).order_by('master_sequence', 'path')
    offer_lst = ['offer', 'Offer', 'offers', 'Offers']
    cat_obj = cat_obj.exclude(name__in=offer_lst)
    cat_list =[]
    for category in cat_obj:
        if not category.get_children_count() == 0:
            id_list = []
            cat_list.append(category)
            id_list = [obj for obj in category.get_descendants() if obj.show_on_frontside]
            if id_list:
                for id in id_list:
                    cat_list.append(id)
                cat_list.append("end")

    if cat_list:
        split = int(ceil(len(cat_list) / 4.))
        columns = [cat_list[i * split:(i + 1) * split] for i in range(4)]
        return columns

    return False

@register.simple_tag
def get_non_child_category():
    offer_lst = ['offer', 'Offer', 'offers', 'Offers']
    cat_obj = [obj for obj in Category.objects.filter(show_on_frontside=True, depth=1).exclude(name__in=offer_lst).order_by('master_sequence', 'path') if obj.get_children_count() == 0]

    if len(cat_obj)>0:
        return cat_obj
    else:
        return False


@register.simple_tag
def get_decoration_category():
    obj = Category.objects.filter(name = 'Wedding Decoration Offers')
    if obj:
        return obj.last()
    return False


@register.simple_tag
def get_professional_category():
    obj = Category.objects.filter(name = 'Professionals')
    if obj:
        return obj.last()
    return False

@register.simple_tag
def get_photoandvideo_category():
    obj = Category.objects.filter(name = 'Photography and Videography')
    if obj:
        return obj.last()
    return False

@register.simple_tag
def get_total_price(product, price, type= None):

    if product.product_cost_type == 'Single' and price:
        rent_price = 0
        sale_price = 0
        cost = 0

        if product.is_real_flower and type == 'real':
            if price.art_sale_price_with_tax and price.art_sale_round_off_price:
                sale_price = price.art_sale_price_with_tax + price.art_sale_round_off_price
            if price.art_sale_price_with_tax and not price.art_sale_round_off_price:
                sale_price = round(price.art_sale_price_with_tax)
            if not price.art_sale_price_with_tax and price.art_sale_price:
                sale_price = round(price.art_sale_price)

            if price.art_rent_price_with_tax and price.art_rent_round_off_price:
                rent_price = price.art_rent_price_with_tax + price.art_rent_round_off_price
            if price.art_rent_price_with_tax and not price.art_rent_round_off_price:
                rent_price = round(price.art_rent_price_with_tax)
            if not price.art_rent_price_with_tax and price.art_rent_price:
                rent_price = round(price.art_rent_price)
            # for sale
            if price.product.product_class.name == 'Sale':
                return '%s' % ('{:,.2f}'.format(sale_price))

            # for rent
            if price.product.product_class.name == 'Rent':
                return '%s' % ('{:,.2f}'.format(rent_price))

            # for professional
            if price.product.product_class.name == 'Professional':
                return '%s' % ('{:,.2f}'.format(rent_price))

            # for rent or sale
            if price.product.product_class.name == 'Rent Or Sale':
                context = {
                    'rent_price': '%s' % ('{:,.2f}'.format(rent_price)),
                    'sale_price': '%s' % ('{:,.2f}'.format(sale_price))
                }
                return context

        if product.is_artificial_flower and type == 'art':

            if price.sale_price_with_tax and price.sale_round_off_price:
                sale_price = price.sale_price_with_tax + price.sale_round_off_price
            if price.sale_price_with_tax and not price.sale_round_off_price:
                sale_price = round(price.sale_price_with_tax)
            if not price.sale_price_with_tax and price.price_excl_tax:
                sale_price = round(price.price_excl_tax)

            if price.rent_price_with_tax and price.rent_round_off_price:
                rent_price = price.rent_price_with_tax + price.rent_round_off_price
            if price.rent_price_with_tax and not price.rent_round_off_price:
                rent_price = round(price.rent_price_with_tax)
            if not price.rent_price_with_tax and price.rent_price:
                rent_price = round(price.rent_price)

            # for rent
            if price.product.product_class.name == 'Sale':
                return '%s' % ('{:,.2f}'.format(sale_price))

            # for sale
            if price.product.product_class.name == 'Rent':
                return '%s' % ('{:,.2f}'.format(rent_price))

            # for professional
            if price.product.product_class.name == 'Professional':
                return '%s' % ('{:,.2f}'.format(rent_price))

            # for rent sale

            if price.product.product_class.name == 'Rent Or Sale':
                context = {
                    'rent_price': '%s' % ('{:,.2f}'.format(rent_price)),
                    'sale_price': '%s' % ('{:,.2f}'.format(sale_price))
                }
                return context


@register.simple_tag
def get_market_saving_price(product, price, type):

    context = {}
    if product and price and type == None:
        # for sale
        if price.product.product_class.name == 'Sale':
            if price.sale_total_saving and price.sale_market_price:
                context = {
                    'total_saving' : '%s' % ('{:,.2f}'.format(round(price.sale_total_saving,0))),
                    'market_price' : '%s' % ('{:,.2f}'.format(round(price.sale_market_price,0))),
                    'status': True
                }
            else:
                context = {
                    'status': False
                }
        # for rent or professional
        if price.product.product_class.name in ['Rent' ,'Professional']:
            if price.rent_total_saving and price.rent_market_price:
                context = {
                    'total_saving': '%s' % ('{:,.2f}'.format(round(price.rent_total_saving,0))),
                    'market_price': '%s' % ('{:,.2f}'.format(round(price.rent_market_price,0))),
                    'status': True
                }
            else:
                context = {
                    'status': False
                }

        # for rent or sale
        if price.product.product_class.name == 'Rent Or Sale':

            if price.rent_total_saving and price.sale_total_saving and price.rent_market_price and price.sale_market_price:

                context = {
                    'total_saving': '%s' % ('{:,.2f}'.format(round(price.rent_total_saving,0))),
                    'market_price': '%s' % ('{:,.2f}'.format(round(price.rent_market_price,0))),
                    'sale_total_saving':'%s' % ('{:,.2f}'.format(round(price.sale_total_saving,0))),
                    'sale_market_price': '%s' % ('{:,.2f}'.format(round(price.sale_market_price,0))),
                    'status': True
                }
            else:
                context = {
                    'status': False
                }
        return context

    if product.is_real_flower and type == 'real':
        # for sale
        if price.product.product_class.name == 'Sale':
            if price.art_sale_total_saving and price.art_sale_market_price:
                context = {
                    'total_saving' : '%s' % ('{:,.2f}'.format(round(price.art_sale_total_saving,0))),
                    'market_price' : '%s' % ('{:,.2f}'.format(round(price.art_sale_market_price,0))),
                    'status': True
                }
            else:
                context = {
                    'status': False
                }
        # for rent or professional
        if price.product.product_class.name in ['Rent' ,'Professional']:
            if price.art_rent_total_saving and price.art_rent_market_price:
                context = {
                    'total_saving': '%s' % ('{:,.2f}'.format(round(price.art_rent_total_saving,0))),
                    'market_price': '%s' % ('{:,.2f}'.format(round(price.art_rent_market_price,0))),
                    'status': True
                }
            else:
                context = {
                    'status': False
                }

        # for rent or sale
        if price.product.product_class.name == 'Rent Or Sale':

            if price.art_rent_total_saving and price.art_rent_market_price and price.art_sale_total_saving and price.art_sale_market_price:
                context = {
                    'total_saving': '%s' % ('{:,.2f}'.format(round(price.art_rent_total_saving,0))),
                    'market_price': '%s' % ('{:,.2f}'.format(round(price.art_rent_market_price,0))),
                    'sale_total_saving': '%s' % ('{:,.2f}'.format(round(price.art_sale_total_saving,0))),
                    'sale_market_price': '%s' % ('{:,.2f}'.format(round(price.art_sale_market_price,0))),
                    'status': True
                }
            else:
                context = {
                    'status': False
                }
        return context

    return False

@register.simple_tag
def get_art_rent_shipping_price(product, price, type):

    if product.product_cost_type == 'Single' and price and product.is_transporation_available:
        ship_rent_price = 0
        ship_sale_price = 0
        cost = 0

        if price.sale_transportation_price:
            ship_sale_price = price.sale_transportation_price

        if price.rent_transportation_price:
            ship_rent_price = price.rent_transportation_price

        # for sale
        if price.product.product_class.name == 'Sale':
            return round(ship_sale_price)

        # for rent
        if price.product.product_class.name == 'Rent':
            return round(ship_rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return round(ship_rent_price)

        # for rent or sale
        if price.product.product_class.name == 'Rent Or Sale':
            context = {
                'ship_rent_price': ship_rent_price,
                'ship_sale_price': ship_sale_price
            }

            return context
    return 0



@register.simple_tag
def review_form(request, product):
    if not isinstance(product, Product):
        return ''

    initial = {}
    if not product.is_parent:
        initial['product_id'] = product.id

    form_class = ProductReviewForm

    return form_class

@register.simple_tag
def update_url(link):
    if 'watch?v=' in link:
        link1=link.replace('watch?v=',  'embed/')
        return link1
    return link


@register.simple_tag
def offers_url():
    offer_lst = ['offer', 'Offer', 'offers', 'Offers']
    offers_cat = Category.objects.filter(name__in=offer_lst)
    try:
        offers_cat_descendants = offers_cat.last().get_descendants()
        cat = offers_cat_descendants.filter(name__iexact='Wedding Decor Offers')
        if not cat:
            cat = offers_cat
        try:
            offer_link = cat.last().get_absolute_url()
        except Exception as e:
            print(e.args)
            offer_link = ''
    except:
        offer_link = ''
    return offer_link

@register.simple_tag
def get_rsprice_whole_int(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        # for rent
        if price.product.product_class.name == 'Sale':
            return (sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return (rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return (rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':
            context = {
                'rent_price' : rent_price,
                'sale_price' : sale_price
            }
            return context

        return (cost)

    except Exception as e:

        return cost

@register.simple_tag
def get_rsproduct_cost_multiple(price):
    quantity = get_quantity_for_multiple(price)
    if price and price.product.product_cost_type == 'Multiple':
        if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            if rent_total_cost:
                return (rent_total_cost)
            else:
                return 0

        elif price.product.product_class.name == 'Sale':
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            if sale_total_cost:
                return (sale_total_cost)

            else:
                return 0
        else:
            rent_total_cost = get_product_cost(price, 'Rent', quantity)
            sale_total_cost = get_product_cost(price, 'Sale', quantity)
            if rent_total_cost and sale_total_cost:
                context = {
                    'rent_price' : round(rent_total_cost),
                    'sale_price' : round(sale_total_cost)
                }
            elif rent_total_cost and not sale_total_cost:
                context = {
                    'rent_price': round(rent_total_cost),
                    'sale_price': 0
                }
            elif not rent_total_cost and sale_total_cost:
                context = {
                    'rent_price': 0,
                    'sale_price': round(sale_total_cost)
                }
            else:
                context = {
                    'rent_price': 0,
                    'sale_price': 0
                }
            return  context

    return False

@register.simple_tag
def get_arprice_whole_int(price):
    rent_price = 0
    sale_price = 0
    cost = 0

    try:

        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        if price.art_sale_price_with_tax and price.art_sale_round_off_price:
            art_sale_price = price.art_sale_price_with_tax + price.art_sale_round_off_price
        if price.art_sale_price_with_tax and not price.art_sale_round_off_price:
            art_sale_price = round(price.art_sale_price_with_tax)
        if not price.sale_price_with_tax and price.art_sale_price:
            art_sale_price = round(price.art_sale_price)

        if price.art_rent_price_with_tax and price.art_rent_round_off_price:
            art_rent_price = price.art_rent_price_with_tax + price.art_rent_round_off_price
        if price.art_rent_price_with_tax and not price.art_rent_round_off_price:
            art_rent_price = round(price.art_rent_price_with_tax)
        if not price.art_rent_price_with_tax and price.art_rent_price:
            art_rent_price = round(price.rent_price)


        # for rent
        if price.product.product_class.name == 'Sale':
            return (sale_price)

        # for sale
        if price.product.product_class.name == 'Rent':
            return (rent_price)

        # for professional
        if price.product.product_class.name == 'Professional':
            return (rent_price)

        # for rent sale

        if price.product.product_class.name == 'Rent Or Sale':

            context = {
                'rent_price' : rent_price,
                'sale_price' : sale_price,
                'art_rent_price': art_rent_price,
                'art_sale_price': art_sale_price
            }
            return context

        return (cost)

    except Exception as e:

        return cost


@register.simple_tag
def get_cat(cat_list):
    ret = ' '
    if cat_list:
        for cat in cat_list:
            ret = ret + cat.name + ','
        return ret[:-1]


@register.simple_tag
def create_zip(a, b):
    return zip(a, b)


@register.simple_tag
def get_price(price):

    rent_price = sale_price = art_rent_price = art_sale_price = 0
    if price.product.product_cost_type == 'Multiple':
        quantity = get_quantity_for_multiple(price)
        if price and price.product.product_cost_type == 'Multiple':
            if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
                rent_total_cost = get_product_cost(price, 'Rent', quantity)

                context = {
                    'rent_price' : '%s' % ('{:,.2f}'.format(round(rent_total_cost))),
                }
            elif price.product.product_class.name == 'Sale':
                sale_total_cost = get_product_cost(price, 'Sale', quantity)
                context = {
                    'sale_price': '%s' % ('{:,.2f}'.format(round(sale_total_cost))),
                }
            else:
                rent_total_cost = get_product_cost(price, 'Rent', quantity)
                sale_total_cost = get_product_cost(price, 'Sale', quantity)
                if rent_total_cost and sale_total_cost:
                    context = {
                        'rent_price': '%s' % ('{:,.2f}'.format(round(rent_total_cost))),
                        'sale_price': '%s' % ('{:,.2f}'.format(round(sale_total_cost))),
                    }
                elif rent_total_cost and not sale_total_cost:
                    context = {
                        'rent_price': '%s' % ('{:,.2f}'.format(round(rent_total_cost))),
                        'sale_price': 0
                    }
                elif not rent_total_cost and sale_total_cost:
                    context = {
                        'rent_price': 0,
                        'sale_price': '%s' % ('{:,.2f}'.format(round(sale_total_cost)))
                    }
                else:
                    context = {
                        'rent_price': 0,
                        'sale_price': 0
                    }

            return context

    else:
        if price.sale_price_with_tax and price.sale_round_off_price:
            sale_price = price.sale_price_with_tax + price.sale_round_off_price
        if price.sale_price_with_tax and not price.sale_round_off_price:
            sale_price = round(price.sale_price_with_tax)
        if not price.sale_price_with_tax and price.price_excl_tax:
            sale_price = round(price.price_excl_tax)

        if price.rent_price_with_tax and price.rent_round_off_price:
            rent_price = price.rent_price_with_tax + price.rent_round_off_price
        if price.rent_price_with_tax and not price.rent_round_off_price:
            rent_price = round(price.rent_price_with_tax)
        if not price.rent_price_with_tax and price.rent_price:
            rent_price = round(price.rent_price)

        if price.art_sale_price_with_tax and price.art_sale_round_off_price:
            art_sale_price = price.art_sale_price_with_tax + price.art_sale_round_off_price
        if price.art_sale_price_with_tax and not price.art_sale_round_off_price:
            art_sale_price = round(price.art_sale_price_with_tax)
        if not price.sale_price_with_tax and price.art_sale_price:
            art_sale_price = round(price.art_sale_price)

        if price.art_rent_price_with_tax and price.art_rent_round_off_price:
            art_rent_price = price.art_rent_price_with_tax + price.art_rent_round_off_price
        if price.art_rent_price_with_tax and not price.art_rent_round_off_price:
            art_rent_price = round(price.art_rent_price_with_tax)
        if not price.art_rent_price_with_tax and price.art_rent_price:
            art_rent_price = round(price.rent_price)

        # for sale
        if price.product.product_class.name == 'Sale':
            context = {
                'sale_price': '%s' % ('{:,.2f}'.format(round(sale_price))),
                'art_sale_price': '%s' % ('{:,.2f}'.format(round(art_sale_price))),
            }

        # for rent
        if price.product.product_class.name in ['Rent', 'Professional']:
            context = {
                'rent_price': '%s' % ('{:,.2f}'.format(round(rent_price))),
                'art_rent_price': '%s' % ('{:,.2f}'.format(round(art_rent_price))),
            }

        # for rent or sale

        if price.product.product_class.name == 'Rent Or Sale':
            context = {
                'rent_price': '%s' % ('{:,.2f}'.format(round(rent_price))),
                'sale_price': '%s' % ('{:,.2f}'.format(round(sale_price))),
                'art_rent_price': '%s' % ('{:,.2f}'.format(round(art_rent_price))),
                'art_sale_price': '%s' % ('{:,.2f}'.format(round(art_sale_price)))
            }
        print('context',context)
        return context

@register.simple_tag
def get_shipping_rsprice_total(price):
    if price and price.product.is_transporation_available:
        quantity = get_quantity_for_multiple(price)
        if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
            shipping_price1 = get_product_shipping(price, 'Rent', quantity)
            return '₹ %s' % ('{:,.2f}'.format(round(shipping_price1,0)))
        elif price.product.product_class.name == 'Sale':
            shipping_price2 = get_product_shipping(price, 'Sale', quantity)
            return '₹ %s' % ('{:,.2f}'.format(round(shipping_price2,0)))
        else:
            shipping_price1 = get_product_shipping(price, 'Rent', quantity)
            shipping_price2 = get_product_shipping(price, 'Sale', quantity)

            context = {
                'rent_shipping' : shipping_price1,
                'sale_shipping' : shipping_price2,
                'status' : True,
            }
            return  context
            return '₹ %s/ ₹ %s' % ('{:,.2f}'.format(round(shipping_price1,0)), '{:,.2f}'.format(round(shipping_price2,0)))

        context ={
            'status': False,
        }

        return context














