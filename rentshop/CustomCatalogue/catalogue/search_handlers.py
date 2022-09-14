import json
from collections import Counter
from itertools import chain

# django imports
from django.conf import settings
from django.utils.module_loading import import_string
from django.views.generic.list import MultipleObjectMixin
from oscar.core.loading import get_class, get_model
from django.db.models import Case, When, Value
from django.db.models import F, Q

BrowseCategoryForm = get_class('search.forms', 'BrowseCategoryForm')
SearchHandler = get_class('search.search_handlers', 'SearchHandler')
is_solr_supported = get_class('search.features', 'is_solr_supported')
is_elasticsearch_supported = get_class('search.features', 'is_elasticsearch_supported')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue','Category')
Attribute_Mapping = get_model('catalogue','Attribute_Mapping')
StockRecord = get_model('partner','StockRecord')
PremiumProducts = get_model('catalogue', 'PremiumProducts')


def get_product_search_handler_class():
    """
    Determine the search handler to use.

    Currently only Solr is supported as a search backend, so it falls
    back to rudimentary category browsing if that isn't enabled.
    """
    # Use get_class to ensure overridability
    if settings.OSCAR_PRODUCT_SEARCH_HANDLER is not None:
        return import_string(settings.OSCAR_PRODUCT_SEARCH_HANDLER)
    if is_solr_supported():
        return get_class('catalogue.search_handlers', 'SolrProductSearchHandler')
    elif is_elasticsearch_supported():
        return get_class(
            'catalogue.search_handlers', 'ESProductSearchHandler',
        )
    else:
        return get_class(
            'catalogue.search_handlers', 'NewProductSearchHandler')


class SolrProductSearchHandler(SearchHandler):
    """
    Search handler specialised for searching products.  Comes with optional
    category filtering. To be used with a Solr search backend.
    """
    form_class = BrowseCategoryForm
    model_whitelist = [Product]
    paginate_by = settings.OSCAR_PRODUCTS_PER_PAGE

    def __init__(self, request_data, full_path, categories=None):
        self.categories = categories
        super().__init__(request_data, full_path)

    def get_search_queryset(self):
        sqs = super().get_search_queryset()
        if self.categories:
            # We use 'narrow' API to ensure Solr's 'fq' filtering is used as
            # opposed to filtering using 'q'.
            pattern = ' OR '.join([
                '"%s"' % sqs.query.clean(c.full_name) for c in self.categories])
            sqs = sqs.narrow('category_exact:(%s)' % pattern)
        return sqs


class ESProductSearchHandler(SearchHandler):
    """
    Search handler specialised for searching products.  Comes with optional
    category filtering. To be used with an ElasticSearch search backend.
    """
    form_class = BrowseCategoryForm
    model_whitelist = [Product]
    paginate_by = settings.OSCAR_PRODUCTS_PER_PAGE

    def __init__(self, request_data, full_path, categories=None):
        self.categories = categories
        super().__init__(request_data, full_path)

    def get_search_queryset(self):
        sqs = super().get_search_queryset()
        if self.categories:
            for category in self.categories:
                sqs = sqs.filter_or(category=category.full_name)
        return sqs


class SimpleProductSearchHandler(MultipleObjectMixin):
    """
    A basic implementation of the full-featured SearchHandler that has no
    faceting support, but doesn't require a Haystack backend. It only
    supports category browsing.

    Note that is meant as a replacement search handler and not as a view
    mixin; the mixin just does most of what we need it to do.
    """
    paginate_by = settings.OSCAR_PRODUCTS_PER_PAGE

    def __init__(self, request_data, full_path,
                 categories=None, other_data=None,
                 search_category=None, search_price=None, _search_type=None, search_venue=None, search_filter_list= None):
        self.categories = categories
        self.kwargs = {
            'page': request_data.get('page', 1),
            'other_data': other_data, 'search_category': search_category,
            'search_price': search_price,
            '_search_type': _search_type,
            'search_venue': search_venue,
            'search_filter_list': search_filter_list,
        }
        self.object_list = self.get_queryset()
        self.other_data = other_data
        self.search_category = search_category
        self.search_price = search_price
        self._search_type = _search_type
        self.search_venue = search_venue
        self.search_filter_list = search_filter_list

    def get_queryset(self):
        qs = Product.browsable.base_queryset()
        cat_obj = Category.objects.filter(show_on_frontside=True, depth=1)
        cat_list = []


        for category in cat_obj:
            id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
            for element in id_list:
                cat_list.append(element)
        service_products = Product.browsable.base_queryset().filter(product_class__name = 'Service',is_deleted = False,categories__in = cat_list)

        qs = qs.filter(is_approved='Approved', is_deleted=False, categories__in = cat_list)

        qs = qs.annotate(price_order=Case(When(product_class_id__name = 'Sale', then=F('stockrecords__price_excl_tax')),default=F('stockrecords__rent_price'),),
                    ).order_by('price_order')

        if self.kwargs['_search_type'] == 'wedding_venue':
            category_list = (
            'Lawn/Halls', '5 Star Hotels', 'Resorts', 'Hotels / 5 Star hotels', 'Lawns / Banquet Halls'
            )
            wedding_category = Category.objects.filter(name__in=category_list)
            qs = qs.filter(categories__in=wedding_category.values_list('id', flat=True))
            service_products = service_products.filter(categories__in=wedding_category.values_list('id', flat=True))

        if self.kwargs.get('search_venue'):
            search_venue = self.kwargs.get('search_venue')
            vn_category = Category.objects.filter(id=search_venue)
            qs = qs.filter(categories__in=vn_category.values_list('id', flat=True))
            service_products = service_products.filter(categories__in=vn_category.values_list('id', flat=True))

        try:
            other_data = self.kwargs['other_data']
        except:
            other_data = None

        try:
            search_category = self.kwargs['search_category']
        except:
            search_category = None

        try:
            search_price = self.kwargs['search_price']
        except:
            search_price = None

        try:
            search_filter_list = self.kwargs['search_filter_list']
        except:
            search_filter_list = None
        print('cat@')

        if self.categories:
            qs = qs.filter(categories__in=self.categories)
            service_products = service_products.filter(categories__in=self.categories)

        if other_data:
            qs = qs.filter(Q(title__icontains=other_data)|Q(upc__iexact = other_data))
            service_products = service_products.filter(Q(title__icontains=other_data)|Q(upc__iexact = other_data))

        if search_category:
            try:
                category = Category.objects.get(id=search_category)
                # if category.has_children():
                #     id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
                #
                #     category = Category.objects.filter(id__in=id_list)
                #     qs = qs.filter(categories__in=category.values_list('id', flat=True))
                #     service_products = service_products.filter(categories__in=category.values_list('id', flat=True))
                #
                # else:
                qs = qs.filter(categories=category)
                service_products = service_products.filter(categories=category)
            except Exception as e:

                import os
                import sys
                print('-----------in exception----------')
                print(e.args)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

                pass

        if search_price:
            _max = None
            _min = None
            if search_price:
                search_price_list = search_price.split('-')
                _min = int(search_price_list[0])
                _max = int(search_price_list[1])
                sale_price = 0
                rent_price = 0
                price_rent = 0
                price_sale = 0
                stock_record = StockRecord.objects.filter(product__in=qs.values_list('id', flat=True))
                stock_list = []
                for price in stock_record:
                    if price.sale_price_with_tax and price.sale_round_off_price:
                        sale_price = price.sale_price_with_tax + price.sale_round_off_price
                    elif price.sale_price_with_tax and not price.sale_round_off_price:
                        sale_price = round(price.sale_price_with_tax)
                    elif not price.sale_price_with_tax and price.price_excl_tax:
                        sale_price = round(price.price_excl_tax)

                    if price.rent_price_with_tax and price.rent_round_off_price:
                        rent_price = price.rent_price_with_tax + price.rent_round_off_price
                    elif price.rent_price_with_tax and not price.rent_round_off_price:
                        rent_price = round(price.rent_price_with_tax)
                    elif not price.rent_price_with_tax and price.rent_price:
                        rent_price = round(price.rent_price)

                    # for rent
                    if price.product.product_class.name == 'Sale':
                        if sale_price in range(_min, _max + 1):
                            stock_list.append(price.id)

                    # for sale
                    if price.product.product_class.name == 'Rent':
                        if rent_price in range(_min, _max + 1):
                            stock_list.append(price.id)

                    # for professional
                    if price.product.product_class.name == 'Professional':
                        if rent_price in range(_min, _max + 1):
                            stock_list.append(price.id)

                    # for rent sale

                    if price.product.product_class.name == 'Rent Or Sale':
                        if rent_price in range(_min, _max + 1) or sale_price in range(_min, _max + 1):
                            stock_list.append(price.id)


                # stock_record = StockRecord.objects.filter(Q(sale_price_with_tax__range=(_min, _max)) | Q(rent_price_with_tax__range=(_min, _max))  )
                if qs:
                    stock_record = stock_record.filter(id__in=stock_list)
                    qs = qs.filter(id__in=stock_record.values_list('product', flat=True))
                    
                # else:
                #     print("there")
                #
                #     stock_record = stock_record.values_list('product__id', flat=True)
                #
                #     qs = qs.filter(id__in=stock_record)


        if search_filter_list:

            data = json.loads(search_filter_list)
            print(data)
            cat_list = self.categories
            cat_id_list = [obj.id for obj in cat_list[-1].get_descendants_and_self()]
            attr_obj = Attribute_Mapping.objects.filter(product__categories__id__in=cat_id_list)

            attr_x = []

            for item in data:
                for key in item:
                    print(attr_obj.filter(attribute__attribute=key, value__icontains= item[key]).values_list('product__id', flat=True))
                    attr_x.extend(list(attr_obj.filter(attribute__attribute=key, value__icontains= item[key]).values_list('product__id', flat=True)))

            print("countr",attr_x)

            final_attr = []
            for c in Counter(attr_x).items():
                if len(data) == c[1]:
                    final_attr.append(c[0])

            # for item in data:
            #     for key in item:
            #         attr_obj = attr_obj.filter(attribute__attribute=key, value__icontains= item[key])

            #qs = qs.filter(id__in=attr_obj.values('product__id'))

            qs = qs.filter(id__in=final_attr)
            service_products = service_products.filter(id__in=attr_obj.values('product__id'))

        if not qs and service_products:
            qs = service_products

        return qs

    def get_search_context_data(self, context_object_name):

        # Set the context_object_name instance property as it's needed
        # internally by MultipleObjectMixin
        self.context_object_name = context_object_name
        if context_object_name == 'wedding_products':
            context = self.get_context_data(
                object_list=self.object_list.filter(categories__in=self.get_queryset_wedding_venue())
            )

        else:
            context = self.get_context_data(object_list=self.object_list)
        context[context_object_name] = context['page_obj'].object_list
        return context

    def get_search_context_data_wedding_venue(self, context_object_name):

        self.context_object_name = context_object_name
        context = self.get_context_data(object_list=self.get_queryset_wedding_venue())
        context[context_object_name] = context['page_obj'].object_list

        return context

    def get_queryset_wedding_venue(self):

        category_list = ('Lawn/Halls', '5 Star Hotels', 'Resorts', 'Hotels / 5 Star hotels', 'Lawns / Banquet Halls')
        c_obj = Category.objects.filter(name__in=category_list)

        return c_obj


class NewProductSearchHandler(MultipleObjectMixin):
    """
    A basic implementation of the full-featured SearchHandler that has no
    faceting support, but doesn't require a Haystack backend. It only
    supports category browsing.

    Note that is meant as a replacement search handler and not as a view
    mixin; the mixin just does most of what we need it to do.
    """
    paginate_by = settings.OSCAR_PRODUCTS_PER_PAGE

    def __init__(self, request_data, full_path,
                 categories=None, other_data=None,
                 search_category=None, search_price=None, _search_type=None, search_venue=None,
                 search_filter_list=None):
        self.categories = categories
        self.kwargs = {
            'page': request_data.get('page', 1),
            'other_data': other_data, 'search_category': search_category,
            'search_price': search_price,
            '_search_type': _search_type,
            'search_venue': search_venue,
            'search_filter_list': search_filter_list,
        }
        self.object_list = self.get_queryset()
        self.other_data = other_data
        self.search_category = search_category
        self.search_price = search_price
        self._search_type = _search_type
        self.search_venue = search_venue
        self.search_filter_list = search_filter_list

    def get_queryset(self):
        category_list = []

        if self.categories:
            premium_products = PremiumProducts.objects.filter(category=int(self.categories))
            category_list = [obj.id for obj in Category.objects.get(id=int(self.categories)).get_descendants_and_self() if obj.show_on_frontside]
        else:
            cat_obj = Category.objects.filter(show_on_frontside=True, depth=1)

            for category in cat_obj:
                id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
                for element in id_list:
                    category_list.append(element)
            premium_products = PremiumProducts.objects.filter(category__in=category_list)


        qs = Product.browsable.base_queryset()
        qs = qs.filter(is_approved='Approved', is_deleted=False, categories__in=category_list)

        qs = qs.annotate(price_order=Case(When(product_class_id__name='Sale', then=F('stockrecords__price_excl_tax')),
                                          default=F('stockrecords__rent_price'), ),
                         ).order_by('price_order')
        other_data = self.kwargs.get('other_data')
        search_category = self.kwargs.get('search_category')
        search_filter_list = self.kwargs.get('search_filter_list')
        search_price = self.kwargs.get('search_price')
        if other_data:
            qs = qs.filter(Q(title__icontains=other_data) | Q(upc__iexact=other_data))

        if search_category:
            qs = qs.filter(categories__id=search_category)
        if search_price:
            search_price_list = search_price.split('-')
            _min = int(search_price_list[0])
            _max = int(search_price_list[1])

            stock_record = StockRecord.objects.filter(product__in=qs.values_list('id', flat=True))
            stock_list = []
            for price in stock_record:
                sale_price = price.sale_float_price
                rent_price = price.rent_float_price

                # for sale products
                if price.product.product_class.name == 'Sale':
                    if sale_price in range(_min, _max + 1):
                        stock_list.append(price.id)

                # for rent or professional products
                if price.product.product_class.name == 'Rent' or price.product.product_class.name == 'Professional':
                    if rent_price in range(_min, _max + 1):
                        stock_list.append(price.id)

                # for rent & sale products
                if price.product.product_class.name == 'Rent Or Sale':
                    if rent_price in range(_min, _max + 1) or sale_price in range(_min, _max + 1):
                        stock_list.append(price.id)

            if qs:
                stock_record = stock_record.filter(id__in=stock_list)
                qs = qs.filter(id__in=stock_record.values_list('product', flat=True))

        if search_filter_list:

            data = json.loads(search_filter_list)
            attr_obj = Attribute_Mapping.objects.filter(product__categories__id__in=category_list)

            attr_x = []

            for item in data:
                for key in item:
                    attr_x.extend(list(
                        attr_obj.filter(attribute__attribute=key, value__icontains=item[key]).values_list('product__id',
                                                                                                          flat=True)))

            final_attr = []
            for c in Counter(attr_x).items():
                if len(data) == c[1]:
                    final_attr.append(c[0])

            qs = qs.filter(id__in=final_attr)

        service_products = qs.filter(product_class__name='Service')
        if qs.filter(id__in=premium_products.values('product__id')):
            premium_qs = qs.filter(id__in=premium_products.values('product__id')).exclude(product_class__name='Service')
            qs = qs.exclude(Q(id__in=premium_products.values('product__id')) | Q(product_class__name='Service'))
            result_list = list(chain(premium_qs, qs, service_products))
        else:
            qs = qs.exclude(product_class__name='Service')
            result_list = list(chain(qs, service_products))
        print('result',result_list)
        return result_list

    def get_search_context_data(self, context_object_name):
        # Set the context_object_name instance property as it's needed
        # internally by MultipleObjectMixin
        self.context_object_name = context_object_name
        context = self.get_context_data(object_list=self.object_list)
        context[context_object_name] = context['page_obj'].object_list
        return context
