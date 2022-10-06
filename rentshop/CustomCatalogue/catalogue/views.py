# python imports
import warnings, json

# django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.paginator import InvalidPage
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, TemplateView, View
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.http import Http404, HttpResponsePermanentRedirect
from django.db.models import Count, Min, Sum, Avg, Max
from django.views import generic
from django.http import JsonResponse

# 3rd party imports
from oscar.apps.catalogue.views import CatalogueView, ProductDetailView, ProductCategoryView
from oscar.apps.catalogue.signals import product_viewed
from oscar.core.loading import get_class, get_model
from oscar.apps.catalogue.reviews.views import CreateProductReview

# internal imports
from .forms import BrowseSearchForm, EnquiryModelForm
from .bind import get_product_blocked_date

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms', 'ProductAlertForm')
get_product_search_handler_class = get_class('catalogue.search_handlers', 'get_product_search_handler_class')
Admin_HeaderMenu = get_model('HeaderMenu','Admin_HeaderMenu')
Admin_HeaderSubMenu = get_model('HeaderMenu','Admin_HeaderSubMenu')
Admin_Header = get_model('HeaderMenu','Admin_Header')
Manage_Menu = get_model('HeaderMenu','Manage_Menu')
ManageMenuMasterProducts = get_model('HeaderMenu','ManageMenuMasterProducts')
ExhibitionOffers = get_model('HeaderMenu','ExhibitionOffers')
ExhibitionOffersCategory = get_model('HeaderMenu','ExhibitionOffersCategory')

VendorCalender = get_model('partner','VendorCalender')
Line = get_model('order','Line')
ProductReviewForm = get_class('catalogue.forms','CustomProductReviewForm')
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')
Basket_Line = get_model('basket', 'Line')
Basket_Onj = get_model('basket', 'Basket')
OrderObj = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
trigger_email = get_class('RentCore.tasks', 'trigger_email')
send_email = get_class('RentCore.email', 'send_email')
Partner = get_model('partner', 'Partner')
CategoriesWisePriceFilter = get_model('catalogue', 'CategoriesWisePriceFilter')


class CustomCatalogueView(CatalogueView):

    """
    Browse product page view
    """

    context_object_name = "products"
    # template_name = 'catalogue/browse.html'
    template_name = 'new_design/catalogue/browse.html'
    form_class = BrowseSearchForm

    def get(self, request, *args, **kwargs):

        """
        Method to return template.
        :param request: default
        :param args: default
        :param kwargs: default
        :return: template
        """

        search_value = None
        search_category = None
        search_price = None
        search_filter_list = None

        if request.GET.get('mega_search'):
            search_value = str(request.GET.get('mega_search')).strip()

        if request.GET.get('price_range'):
            search_price = request.GET.get('price_range')

        if request.GET.get('category'):
            search_category = request.GET.get('category')

        if request.GET.get('filter_list'):
            search_filter_list = request.GET.get('filter_list')

        try:
            self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), kwargs.get('pk'), search_value, search_category, search_price,None,None,search_filter_list)
        except InvalidPage:
            messages.error(request, _('The given page number was invalid.'))
            return redirect('catalogue:index')

        return super(CatalogueView, self).get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):

        """
        Search filter
        :param args: default
        :param kwargs: default
        :return: queryset
        """

        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):

        ctx = super(CatalogueView, self).get_context_data(**kwargs)
        try:
            ctx['search_form'] = self.form_class(self.request.GET, category=self.category)
        except:
            ctx['search_form'] = self.form_class(self.request.GET, category=None)

        ctx['summary'] = _("All products")
        ctx['category_list'] = Category.objects.filter(show_on_frontside=True, depth=1)
        if self.request.GET.get('mega_search'):
            ctx['q'] = self.request.GET.get('mega_search')
        ctx['filters'] = self.get_selected_filter()
        ctx['price_filter'] = self.get_price_filter()
        search_context = self.search_handler.get_search_context_data(self.context_object_name)
        ctx.update(search_context)

        return ctx

    def get_selected_filter(self):
        selected_filter = {
            'filter_list': self.request.GET.get('filter_list'),
            'category': self.request.GET.get('category'),
        }

        if selected_filter.get('category'):
            selected_filter['category'] = int(selected_filter['category'])
        return selected_filter

    def get_price_filter(self):
        price_filter = (
            ("0-500", "0 - 500"),
            ("500-1000", "500 - 1000"),
            ("1000-2000", "1000 - 2000"),
            ("2000-5000", "2000 - 5000"),
            ("5000-50000", "5000 & Above"),
        )
        return price_filter


class CustomProductDetailView(ProductDetailView):

    """
    Product details views extended.
    """
    template_folder = "new_design/catalogue"
    def all_categories(self):

        """
        Method to get all categories
        :return: queryset
        """

        all_cat = Category.objects.all()

        dict_obj = {'all_category':all_cat}

        return dict_obj

    def get_context_data(self, **kwargs):

        """
        Extend context data
        :param kwargs:
        :return:
        """

        ctx = super().get_context_data(**kwargs)
        ctx.update(self.all_categories())
        return ctx


class CustomProductCategoryView(ProductCategoryView):

    """
    Product category wise view
    """

    template_name = 'catalogue/category.html'
    form_class = BrowseSearchForm

    def get(self, request, *args, **kwargs):

        # get method to fetch initial data
        self.category = self.get_category()
        potential_redirect = self.redirect_if_necessary(request.path, self.category)

        search_value = None
        search_category = None
        search_price = None
        search_filter_list = None

        if request.GET.get('mega_search'):
            search_value = str(request.GET.get('mega_search')).strip()

        if request.GET.get('category'):
            search_category = request.GET.get('category')

        if request.GET.get('price_range'):
            search_price = request.GET.get('price_range')

        if request.GET.get('filter_list'):
            search_filter_list = request.GET.get('filter_list')


        if potential_redirect is not None:
            return potential_redirect

        try:
            self.search_handler = self.get_search_handler(
                request.GET, request.get_full_path(), self.get_categories(), search_value,
                search_category, search_price, None, None,search_filter_list
            )
        except InvalidPage:
            messages.error(request, _('The given page number was invalid.'))
            return redirect(self.category.get_absolute_url())

        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    def get_category(self):

        # get category according to URL
        if 'pk' in self.kwargs:
            return get_object_or_404(Category, pk=self.kwargs['pk'])
        elif 'category_slug' in self.kwargs:

            concatenated_slugs = self.kwargs['category_slug']
            slugs = concatenated_slugs.split(Category._slug_separator)
            try:
                last_slug = slugs[-1]
            except IndexError:
                raise Http404
            else:
                for category in Category.objects.filter(slug=last_slug):
                    if category.full_slug == concatenated_slugs:
                        message = ("Accessing categories without a primary keyis deprecated will be removed in Oscar "\
                                   " 1.2.")
                        warnings.warn(message, DeprecationWarning)

                        return category

        raise Http404

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            expected_path = category.get_absolute_url()
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_categories(self):
        return self.category.get_descendants_and_self()

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['category'] = self.category
        try:
            context['search_form'] = self.form_class(self.request.GET, category=self.category)
        except:
            context['search_form'] = self.form_class(self.request.GET, category=None)

        search_context = self.search_handler.get_search_context_data(
            self.context_object_name)
        context.update(search_context)
        return context

    def post(self, request, *args, **kwargs):

        # search post method custom.
        search_value = None
        try:
            search_data = request.POST.dict()
            search_value = search_data.get('q')
        except Exception as e:

            pass

        self.category = self.get_category()
        self.search_handler = self.get_search_handler(
            request.GET, request.get_full_path(), self.get_categories(), search_value)

        return super(ProductCategoryView, self).get(request, *args, **kwargs)


class ProductWeddingVenueView(CatalogueView):

    """
    Wedding venue browse product page view.
    """

    context_object_name = "wedding_products"
    template_name = 'catalogue/Wedding_venue_category.html'
    form_class = BrowseSearchForm

    def get(self, request, *args, **kwargs):

        """
        Method to return template.
        :param request: default
        :param args: default
        :param kwargs: default
        :return: template
        """

        search_value = None
        search_category = None
        search_price = None
        search_venue = None
        search_filter_list = None

        if request.GET.get('mega_search'):
            search_value = str(request.GET.get('mega_search')).strip()

        if request.GET.get('category'):
            search_category = request.GET.get('category')

        if request.GET.get('price_range'):
            search_price = request.GET.get('price_range')

        if request.GET.get('venues'):
            search_venue = request.GET.get('venues')

        if request.GET.get('filter_list'):
            search_filter_list = request.GET.get('filter_list')

        try:
            self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), [], search_value, search_category, search_price, None, search_venue, search_filter_list)
        except InvalidPage:
            messages.error(request, _('The given page number was invalid.'))
            return redirect('catalogue:index')

        return super(CatalogueView, self).get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):

        """
        Search filter
        :param args: default
        :param kwargs: default
        :return: queryset
        """

        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):

        ctx = super(CatalogueView, self).get_context_data(**kwargs)
        try:
            ctx['search_form'] = self.form_class(self.request.GET, category=self.category)
        except:
            ctx['search_form'] = self.form_class(self.request.GET, category=None)

        ctx['summary'] = _("All products")
        search_context = self.search_handler.get_search_context_data(self.context_object_name)

        ctx.update(search_context)

        return ctx

    # def get(self, request, *args, **kwargs):
    #
    #     search_value = None
    #     search_category = None
    #     search_price = None
    #
    #     if request.GET.get('mega_search'):
    #         search_value = request.GET.get('mega_search')
    #
    #     if request.GET.get('category'):
    #         search_category = request.GET.get('category')
    #
    #     if request.GET.get('price_range'):
    #         search_price = request.GET.get('price_range')
    #
    #     try:
    #         self.search_handler = self.get_search_handler(
    #             self.request.GET, request.get_full_path(), [], search_value,
    #             search_category, search_price, 'wedding_venue'
    #         )
    #
    #     except InvalidPage:
    #         messages.error(request, _('The given page number was invalid.'))
    #         return redirect('catalogue:index')
    #
    #     return super(CatalogueView, self).get(request, *args, **kwargs)
    #
    # def get_search_handler(self, *args, **kwargs):
    #     return get_product_search_handler_class()(*args, **kwargs)
    #
    # def get_context_data(self, **kwargs):
    #
    #     ctx = super(CatalogueView, self).get_context_data(**kwargs)
    #     ctx['search_form'] = self.form_class(self.request.GET or None)
    #     ctx['summary'] = _("All products")
    #     search_context = self.search_handler.get_search_context_data_wedding_venue(self.context_object_name)
    #     ctx.update(search_context)
    #
    #     return ctx


class CategoryWiseProductView(DetailView):

    """
    Category wise product detail view.
    """

    context_object_name = 'product'
    model = Product
    template_name = 'promotions/category_product.html'

    def get(self, request, pk, *args, **kwars):

        header_menu_obj = Admin_HeaderMenu.objects.get(id=pk)
        header_submenu_obj = Admin_HeaderSubMenu.objects.filter(header_menu_id=header_menu_obj)
        lst = []

        for h in header_submenu_obj:
            url = h.url
            lst.append(url.split('/')[3].split('_')[0])

        category_obj = Category.objects.filter(slug__in=lst)
        product_obj = Product.objects.filter(categories__in=category_obj,is_deleted=False)

        return render(request,self.template_name,{'products':product_obj})


class HeaderCategoryProductView(TemplateView):

    """
    Category header template view.
    """

    context_object_name = 'category'
    template_name = 'promotions/header_menu.html'

    def get(self, request, pk, *args, **kwargs):

        ctx={}

        header_menu_obj = Admin_Header.objects.get(id=pk)
        header_submenu_obj = Admin_HeaderMenu.objects.filter(title_id=header_menu_obj.id)

        ctx[self.context_object_name] = header_submenu_obj
        ctx['title'] = header_menu_obj.title

        if header_menu_obj.title == 'My Offers':

            return render(request, 'promotions/header_menu/my-offers.html', ctx)

        if header_menu_obj.title == 'Exhibitions Offers':
            header_menu_obj = ExhibitionOffers.objects.filter(header_menu_id=pk)
            cat_obj = Category.objects.filter(show_on_frontside=True, depth=1)
            cat_list = []
            for category in cat_obj:
                id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
                for element in id_list:
                    cat_list.append(element)
            header_submenu_obj = ExhibitionOffersCategory.objects.filter(manage_menu=header_menu_obj.last(), manage_category__id__in=cat_list)
            ctx[self.context_object_name] = header_submenu_obj

            return render(request, 'promotions/header_menu/exhibitions-offers.html', ctx)

        return render(request, self.template_name, ctx)


class ManageHeaderCategoryProductView(TemplateView):

    """
    Category header template view.
    """

    context_object_name = 'category'
    template_name = 'promotions/header_menu/corporate_offers_1.0.html'

    def get(self, request, pk, *args, **kwargs):

        list_obj = list()

        header_menu_obj = Manage_Menu.objects.filter(header_menu_id=pk)

        for header_obj in header_menu_obj:

            ctx = {}

            header_submenu_obj = ManageMenuMasterProducts.objects.filter(manage_menu=header_obj).values_list('manage_product__id', flat=True)
            cat_obj = Category.objects.filter(show_on_frontside=True,depth = 1)
            cat_list = []
            for category in cat_obj:
                id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
                for element in id_list:
                    cat_list.append(element)
            obj = Product.objects.filter(id__in = header_submenu_obj,is_approved = 'Approved',is_deleted = False, categories__in = cat_list)

            ctx['id'] = header_obj.id
            ctx['offer_title'] = header_obj.offer_title
            ctx['products'] = obj

            list_obj.append(ctx)

        return render(request,self.template_name,{'list_obj':list_obj})


class GetBestQuoteView(TemplateView):

    """
    Category header template view.
    """

    context_object_name = 'category'
    template_name = 'promotions/header_menu/get_best_quote.html'

    def get(self, request, pk, *args, **kwargs):


        list_obj = list()
        # header menus
        header_menu_obj = Manage_Menu.objects.filter(header_menu_id=pk)
        for header_obj in header_menu_obj:
            ctx = {}
            header_submenu_obj = ManageMenuMasterProducts.objects.filter(manage_menu=header_obj).values_list('manage_product__id', flat=True)
            obj = Product.objects.filter(id__in = header_submenu_obj,is_deleted=False)
            ctx['id'] = header_obj.id
            ctx['offer_title'] = header_obj.offer_title
            ctx['products'] = obj
            list_obj.append(ctx)

        return render(request,self.template_name,{'list_obj':list_obj})


class GetBestQuoteCreateView(View):

    """
    Vendor register form
    """

    form = EnquiryModelForm
    template_name = 'promotions/header_menu/enquiry_form.html'

    def get(self, request, *args, **kwargs):

        form = self.form()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST)

        if form.is_valid():

            try:
                base_form = form.save(commit=False)
                base_form.created_by = request.user
                base_form.save()
                messages.success(request, 'Your response has been recorded successfully.')
                return render(request, 'promotions/header_menu/enquiry_success.html')

            except Exception as e:
                messages.error(request, 'Something went wrong.')
                return redirect('/')
        else:
            pass

        return render(request, self.template_name, {'form': form})


class MenuOfferProductView(TemplateView):

    """
    Category header template view.
    """

    context_object_name = 'category'
    template_name = 'promotions/header_menu/header_products.html'

    def get(self, request, pk, *args, **kwargs):


        list_obj = list()
        # header menus
        header_menu_obj = Manage_Menu.objects.get(id=pk)

        ctx = {}
        header_submenu_obj = ManageMenuMasterProducts.objects.filter(manage_menu=header_menu_obj).values_list('manage_product__id', flat=True)
        obj = Product.objects.filter(id__in = header_submenu_obj,is_deleted=False)
        ctx['offer_title'] = header_menu_obj.offer_title
        ctx['products'] = obj


        return render(request,self.template_name,ctx)


class GetSubCategoriesView(DetailView):

    """
    Get sub-categories view.
    """

    context_object_name = "products"
    template_name = 'catalogue/Wedding_venue_category.html'

    def get(self, request, pk):

        cat_obj = Category.objects.get(id=pk)

        ctx = {}
        ctx[self.context_object_name] = cat_obj.get_descendants()

        return render(request, self.template_name, ctx)


class MenuView(TemplateView):

    """
    Main menu template view.
    """

    # template name
    template_name = 'catalogue/menu.html'

    # get method
    def get(self, request, *args, **kwargs):

        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        context={}
        context['category_tree'] = Category.objects.all()
        return render(request,self.template_name,context)


######################################################
# User reviews method's
######################################################


class CustomCreateProductReview(CreateProductReview):

    """
    Customer/User product review method.
    """

    # template_name = "catalogue/reviews/review_form.html"
    template_name = "new_design/catalogue/partials/review_form.html"
    form_class = ProductReviewForm

    def form_valid(self, form):
        response = super(CustomCreateProductReview, self).form_valid(form)
        self.send_signal(self.request, response, self.object)
        return response

    def form_invalid(self, form):
        response = super(CreateProductReview, self).form_valid(form)
        self.send_signal(self.request, response, self.object)
        return response


def product_blocked_dates(request):

    """
    Ajax method to return product blocked list.
    :param request:
    :return: array
    """

    try:

        data = request.GET

        product = Product.objects.get(id=data.get('product_id'), is_deleted=False)
        if product:
            if not product.product_class.name == 'Rent Or Sale':
                unsorted_dates = get_product_blocked_date(data.get('product_id'))

                dates = {'date': unsorted_dates['unsorted_dates'],
                         'diff': unsorted_dates['default'],
                         'status': unsorted_dates['status']
                         }
            else:
                dates = {'date': [],
                         'diff': 0,
                         'status': False,
                         }

        return HttpResponse(json.dumps(dates))

    except Exception as e:

        dates = {'date': [],
                 'diff' : 0,
                 'status' : False,
                 }
        return HttpResponse(json.dumps(dates))


@csrf_exempt
def get_total_price(request):

    """
    Ajax method to return state list.
    """

    if request.is_ajax():

        try:
            quantity = request.GET['quantity']
            product = request.GET['product']
            diffDays = request.GET['diffDays']
            status = 0
            quantity = int(quantity)
            if not quantity:
                status = 200
                return  HttpResponse(status)
            prod_obj = Product.objects.filter(id = product,is_deleted=False)
            if not prod_obj:
                status = 201
                return HttpResponse(status)

            prod = prod_obj.last()

            if prod.product_cost_type != 'Multiple':
                price_obj = prod.stockrecords.last()
                price1 = get_price(price_obj)
                if prod.product_class.name in ['Rent', 'Professional', 'Sale']:

                    shipping_price = get_product_shipping(price_obj,price_obj.product.product_class.name,quantity,diffDays)
                    if price1 and quantity and shipping_price:
                        total = (price1 * quantity)+shipping_price
                        shipping_price = '₹ %s + ₹ %s' % ('{:,.2f}'.format(price1*quantity), '{:,.2f}'.format(shipping_price))
                    elif price1 and quantity and not shipping_price:
                        total = (price1 * quantity)
                        shipping_price = '₹ %s + ₹ %s' % ('{:,.2f}'.format(price1*quantity), '{:,.2f}'.format(shipping_price))
                    else:
                        total = price1
                        shipping_price = '₹ %s + ₹ %s' % ('{:,.2f}'.format(price1* quantity), '{:,.2f}'.format(shipping_price))
                    total = '{:,.2f}'.format(total)
                else:
                    shipping_price1 = get_product_shipping(price_obj, 'Rent', quantity, diffDays)
                    shipping_price2 = get_product_shipping(price_obj, 'Sale', quantity, diffDays)

                    rent_price = price1['rent_price']
                    sale_price = price1['sale_price']
                    if rent_price and quantity and shipping_price1:
                        total1 = (rent_price * quantity) + shipping_price1
                    elif rent_price and quantity and not shipping_price1:
                        total1 = (rent_price * quantity)
                    if sale_price and quantity and shipping_price2:
                        total2 = (sale_price * quantity) + shipping_price2
                    elif sale_price and quantity and not shipping_price2:
                        total2 = (sale_price * quantity)

                    total = '%s/ ₹ %s' % ('{:,.2f}'.format(total1), '{:,.2f}'.format(total2))
                    shipping_price = '₹ %s/ ₹ %s + ₹ %s/ ₹ %s' % (
                    '{:,.2f}'.format(rent_price* quantity), '{:,.2f}'.format(sale_price*quantity), '{:,.2f}'.format(shipping_price1),
                    '{:,.2f}'.format(shipping_price2))

                context = {
                    'status' : 500,
                    'total' : total,
                    'total_cal' : shipping_price,

                }
                return JsonResponse(context)

            else:
                if prod.product_class.name in ['Rent', 'Professional', 'Sale']:
                    price_obj = prod.stockrecords.last()
                    price1 = get_product_shipping(price_obj,price_obj.product.product_class.name,quantity, diffDays)
                    if not price1:
                        status = 202
                        return HttpResponse(status)
                    if not price1['status']:
                        status = 203

                        msg = "Give range of quantity between %s and %s" %(price1['min_quantity'], price1['max_quantity'])

                        context = {
                            'status': 203,
                            'msg' : msg
                        }
                        return JsonResponse(context)

                    total = (price1['product_price'] * quantity)+ price1['ship_price']
                    total = '{:,.2f}'.format(total)
                    shipping_price = '₹ %s + ₹ %s' % (
                    '{:,.2f}'.format(price1['product_price']* quantity), '{:,.2f}'.format(price1['ship_price']))

                    context = {
                        'status' : 500,
                        'total' : total,
                        'total_cal' : shipping_price,
                    }
                    return JsonResponse(context)


                else:
                    price_obj = prod.stockrecords.last()
                    price1 = get_product_shipping(price_obj, 'Rent', quantity, diffDays)
                    price2 = get_product_shipping(price_obj, 'Sale', quantity, diffDays)
                    if not price1['status'] and not price2['status']:
                        status = 203
                        msg = "Give range of quantity for rent between %s ,%s and for sale between %s, %s " %(price1['min_quantity'], price1['max_quantity'],price2['min_quantity'], price2['max_quantity'])

                        context = {
                            'status': 203,
                            'msg': msg
                        }
                        return JsonResponse(context)

                    if not price1['status'] and price2['status']:
                        status = 204
                        msg = "Give range of quantity for rent between %s ,%s " % (price1['min_quantity'], price1['max_quantity'])
                        total1 = (price2['product_price']* quantity)  + price2['ship_price']
                        total = '{:,.2f}'.format(total1)
                        shipping_price = '₹ %s + ₹ %s' % (
                        '{:,.2f}'.format(price2['product_price'] * quantity), '{:,.2f}'.format(price2['ship_price']))

                        context = {
                            'status': 204,
                            'msg': msg,
                            'total' : total,
                            'total_cal': shipping_price,

                        }
                        return JsonResponse(context)

                    if price1['status'] and not price2['status']:
                        status = 204
                        msg = "Give range of quantity for sale between %s ,%s " % (price2['min_quantity'], price2['max_quantity'])
                        totall = (price1['product_price'] * quantity) + price1['ship_price']
                        total = '{:,.2f}'.format(totall)
                        shipping_price = '₹ %s + ₹ %s' % (
                        '{:,.2f}'.format(price1['product_price'] * quantity), '{:,.2f}'.format(price1['ship_price']))
                        context = {
                            'status': 204,
                            'msg': msg,
                            'total' : total,
                            'total_cal': shipping_price,

                        }
                        return JsonResponse(context)

                    totall = (price1['product_price']* quantity) + price1['ship_price']
                    total2 = (price2['product_price']* quantity) + price2['ship_price']
                    total = '%s/ ₹ %s' % ('{:,.2f}'.format(totall), '{:,.2f}'.format(total2))
                    shipping_price = '₹ %s/ ₹ %s + ₹ %s/ ₹ %s' % (
                    '{:,.2f}'.format(price1['product_price'] * quantity), '{:,.2f}'.format(price2['product_price'] * quantity),
                    '{:,.2f}'.format(price1['ship_price']), '{:,.2f}'.format(price2['ship_price']))

                    context = {
                        'status' : 500,
                        'msg' : 'successful',
                        'total' : total,
                        'total_cal': shipping_price,
                    }
                    return JsonResponse(context)

        except Exception as e:
            import os
            import sys
            print('-----------in exception----------')
            print(e.args)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            return HttpResponse(str(e.args[0]))


def get_product_shipping(price, type, quantity, days):

    ship_sale_price, ship_rent_price = 0, 0
    sale_price, rent_price = 0, 0

    costs_product = ProductCostEntries.objects.filter(product=price.product)
    if price.product.product_cost_type == 'Multiple':

        if type == 'Sale':
            costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity, requirement_day__gte = days ).order_by('-requirement_day')
            if not costs:
                costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity ).order_by('requirement_day')
            if costs:
                costs = costs.last()
                if costs.transport_cost and price.product.is_transporation_available:
                    ship_sale_price = costs.transport_cost
                else:
                    ship_sale_price = 0
                if costs.cost_incl_tax :
                    sale_price = costs.cost_incl_tax
                else:
                    if price.sale_price_with_tax and price.sale_round_off_price:
                        sale_price = price.sale_price_with_tax + price.sale_round_off_price
                    if price.sale_price_with_tax and not price.sale_round_off_price:
                        sale_price = round(price.sale_price_with_tax)
                    if not price.sale_price_with_tax and price.price_excl_tax:
                        sale_price = round(price.price_excl_tax)
                    ship_sale_price = 0
                context = {
                    'status' : True,
                    'ship_price' : ship_sale_price,
                    'product_price' : sale_price
                }

                return context
            else:
                costs = ProductCostEntries.objects.filter(product=price.product)
                if costs:
                    min_quantity = costs.aggregate(Min('quantity_from'))
                    max_quantity = costs.aggregate(Max('quantity_to'))
                    if min_quantity['quantity_from__min'] and max_quantity['quantity_to__max']:
                        context = {
                            'status' : False,
                            'min_quantity' : min_quantity['quantity_from__min'],
                            'max_quantity' : max_quantity['quantity_to__max'],
                        }
                        return context

            if price.sale_price_with_tax and price.sale_round_off_price:
                sale_price = price.sale_price_with_tax + price.sale_round_off_price
            if price.sale_price_with_tax and not price.sale_round_off_price:
                sale_price = round(price.sale_price_with_tax)
            if not price.sale_price_with_tax and price.price_excl_tax:
                sale_price = round(price.price_excl_tax)
            ship_sale_price = 0
            context = {
                'status': True,
                'ship_price': ship_sale_price,
                'product_price': sale_price
            }
            return context

        if type in ['Rent' ,'Professional']:
            costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity, rent_requirement_day__gte = days).order_by('-rent_requirement_day')
            if not costs:
                costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity).order_by('rent_requirement_day')
            if costs:
                costs = costs.last()
                if costs.rent_transport_cost and price.product.is_transporation_available:
                    ship_rent_price = costs.rent_transport_cost
                else:
                    ship_rent_price = 0
                if costs.rent_cost_incl_tax :
                    rent_price = costs.rent_cost_incl_tax
                else:
                    if price.rent_price_with_tax and price.rent_round_off_price:
                        rent_price = price.rent_price_with_tax + price.rent_round_off_price
                    if price.rent_price_with_tax and not price.rent_round_off_price:
                        rent_price = round(price.rent_price_with_tax)
                    if not price.rent_price_with_tax and price.rent_price:
                        rent_price = round(price.rent_price)
                    ship_rent_price = 0

                context = {
                    'status' : True,
                    'ship_price' : ship_rent_price,
                    'product_price' : rent_price
                }

                return context
            else:
                costs = ProductCostEntries.objects.filter(product=price.product)

                if costs:

                    min_quantity = costs.aggregate(Min('rent_quantity_from'))
                    max_quantity = costs.aggregate(Max('rent_quantity_to'))

                    if min_quantity['rent_quantity_from__min'] and max_quantity['rent_quantity_to__max']:
                        context = {
                            'status': False,
                            'min_quantity': min_quantity['rent_quantity_from__min'],
                            'max_quantity': max_quantity['rent_quantity_to__max'],
                        }
                        return context

            if price.rent_price_with_tax and price.rent_round_off_price:
                rent_price = price.rent_price_with_tax + price.rent_round_off_price
            if price.rent_price_with_tax and not price.rent_round_off_price:
                rent_price = round(price.rent_price_with_tax)
            if not price.rent_price_with_tax and price.rent_price:
                rent_price = round(price.rent_price)
            ship_rent_price = 0
            context = {
                'status': True,
                'ship_price': ship_rent_price,
                'product_price': rent_price
            }
            return context

    elif price.product.product_cost_type == 'Single':
        if type == 'Sale':
            if price.sale_transportation_price and price.product.is_transporation_available:
                ship_sale_price = price.sale_transportation_price
            return ship_sale_price

        if type in ['Rent', 'Professional']:
            if price.rent_transportation_price and price.product.is_transporation_available:
                ship_rent_price = price.rent_transportation_price
            return ship_rent_price
    return 0


def get_price(price):

    rent_price=0
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
            context = {
                'rent_price' : rent_price,
                'sale_price' : sale_price,
            }
            return context

        return cost

    except Exception as e:

        return cost


def set_is_discountable(request):


    ay = Product.objects.all()
    ay.update( is_discountable=True)
    Basket_Onj.objects.filter(status="Open").delete()


    return HttpResponse('****')


def set_product_is_deleted(request):

    Product.objects.filter(product_class__name = "Service").update(is_deleted = False)
    ay = Product.objects.filter(stockrecords__isnull=True).exclude(product_class__name = "Service").update(is_deleted = True)

    return HttpResponse('****')


# def send_full_payment_email(request):
#     try:
#         order_obj = OrderObj.objects.filter(number=100656)
#         if order_obj.last().order_type == 'partial':
#             mail_context = {
#                 'user': order_obj.last().user,
#             }
#             advanced_pay_email_data = {
#                 'mail_subject': 'TakeRentPe : Advanced Payment',
#                 'mail_template': 'customer/email/order_advanced_payment.html',
#                 'mail_to': [order_obj.last().user.email],
#                 'mail_type': 'order_placed_advance_payment',
#                 'order_id': order_obj.last().id,
#                 'order_user_id': order_obj.last().user.id,
#             }
#
#             # send_email(**advanced_pay_email_data)
#             trigger_email.delay(**advanced_pay_email_data)
#
#         if order_obj.last().order_type == 'full':
#             mail_context = {
#                 'user': order_obj.last().user,
#             }
#             full_pay_email_data = {
#                 'mail_subject': 'TakeRentPe : Full Payment',
#                 'mail_template': 'customer/email/order_full_payment.html',
#                 'mail_to': [order_obj.last().user.id,],
#                 'mail_type': 'order_placed_full_payment',
#                 'order_id': order_obj.last().id,
#                 'order_user_id': order_obj.last().user.id,
#             }
#
#             trigger_email.delay(**full_pay_email_data)
#
#         return HttpResponse('**Done**')
#     except Exception as e:
#         import os
#         import sys
#         print('-----------in exception----------')
#         print(e.args)
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         return HttpResponse('****')


def order_reminder(request):

    import datetime
    today_date = datetime.datetime.now().date()
    no_list = [100654, 100655, 100656,100658, 100659]
    # order_obj = OrderObj.objects.filter(number__in = no_list)
    order_obj = OrderObj.objects.all()

    current_site = Site.objects.get_current()

    for order in order_obj:
        lines = order.lines.all()
        for line in lines:

            # diff_day = (line.booking_start_date.date() - today_date).days
            if line.booking_start_date and int((line.booking_start_date.date() - today_date).days) == 2 and line.allocated_order_line.all():

                part_obj = Partner.objects.filter(id=line.allocated_order_line.last().vendor_id, users__is_active=True)
                if part_obj:

                    email_data = {
                        'mail_subject': 'TakeRentPe : Order Reminder',
                        'mail_template': 'dashboard/sales/prime_bucket/email_order_reminder.html',
                        'mail_to': [line.allocated_order_line.last().vendor.email_id],
                        'mail_type': 'order_reminder',
                        'allocated_obj_id': line.allocated_order_line.last().id,
                        'domain': current_site.domain
                    }

                    trigger_email.delay(**email_data)

                    # sms send code TWO DAY’S BEFORE ORDER REMINDER SMS
                    order_link = current_site.domain + '/dashboard/orders/' + str(line.allocated_order_line.last().order_number) + '/'
                    message = 'This is a kind remind you that the order no. ' \
                              + str(line.allocated_order_line.last().order_number) \
                              + ' event is 2 days away.Visit the link for more details and be prepared for the event. ' \
                                '(' + order_link + ') Happy Celebranto!'
                    msg_kwargs = {
                        'message': message,
                        'mobile_number': part_obj.last().telephone_number,
                    }
                    send_sms(**msg_kwargs)

    return HttpResponse('*************** Order Reminder Called ***************')


def send_full_payment_email(request):
    order_obj = OrderObj.objects.filter(number = 100656)
    summary_pdf = generate_order_summary(order_obj.last())
    current_site = Site.objects.get_current()
    if summary_pdf:
        return HttpResponse("<a href="+current_site.domain+'/' + summary_pdf+"> link </a>")

    return HttpResponse('*************** Done ***************')


def generate_order_summary(order):
    import pdfkit, tempfile
    from django.template.loader import get_template

    pdf_name = 'order_summary_%s.pdf' % (str(order.number))
    pdf_path = 'media/order_summary/' + pdf_name

    options = {}

    current_site = Site.objects.get_current()

    context = dict()
    context['order'] = order
    context['site'] = 'TakeRentPe'  # replace this
    context['site_logo'] = current_site.domain + '/static/' + settings.LOGO_URL

    # create pdf body
    template = get_template('dashboard/orders/invoices/order_summary.html')
    html = template.render(context)
    # create pdf body
    try:
        pdfkit.from_string(
            html, pdf_path, options=options
        )
    except:
        pass

    return pdf_path


def product_blocked_dates_onsubmit(request):
    """
    Ajax method to return product blocked list.
    :param request:
    :return: array
    """

    try:
        data = request.GET
        unsorted_dates = get_product_blocked_date(data.get('product_id'))
        startDate = data.get('booking_start_date')
        import datetime
        startDate= datetime.datetime.strptime(str(startDate), '%Y-%m-%d').strftime('%m/%d/%Y')
        if startDate in unsorted_dates['unsorted_dates']:
            status = True
        else:
            status = False
        return HttpResponse(status)

    except Exception as e:
        import os
        import sys
        print('-----------in exception----------')
        print(e.args)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        status = False

        return HttpResponse(status)


@csrf_exempt
def get_total_price_new(request):

    """
    Ajax method to return state list.
    """

    if request.is_ajax():

        try:
            flower_type = None
            quantity = request.GET['quantity']
            product = request.GET['product']
            diffDays = int(request.GET['diffDays'])
            flower_type = request.GET['flower_type']
            status = 0
            quantity = int(quantity)
            if not quantity:
                status = 200
                return  HttpResponse(status)
            prod_obj = Product.objects.filter(id=product, is_deleted=False)
            if not prod_obj:
                status = 201
                return HttpResponse(status)

            prod = prod_obj.last()

            if quantity>prod.daily_capacity:
                return HttpResponse(420)
            if prod.product_cost_type != 'Multiple':
                price_obj = prod.stockrecords.last()
                price1 = get_price_new(price_obj,flower_type)
                if prod.product_class.name in ['Rent', 'Professional', 'Sale']:
                    if prod.is_artificial_flower and prod.is_real_flower:
                        price1 = get_price_new(price_obj, 'artificial')
                        shipping_price = get_product_shipping(price_obj, price_obj.product.product_class.name,
                                                                  quantity,
                                                                  diffDays)
                        if price1 and quantity and shipping_price:
                            art_total = (price1 * quantity) + shipping_price
                            art_total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            art_shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))
                        elif price1 and quantity and not shipping_price:
                            art_total = (price1 * quantity)
                            art_total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            art_shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))
                        else:
                            art_total = price1
                            art_total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            art_shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))

                        shipping_price = get_product_shipping(price_obj, price_obj.product.product_class.name, quantity,
                                                              diffDays)
                        price1 = get_price_new(price_obj,'real')
                        if price1 and quantity and shipping_price:
                            total = (price1 * quantity) + shipping_price
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))

                        elif price1 and quantity and not shipping_price:
                            total = (price1 * quantity)
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))
                        else:
                            total = price1
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))

                        context ={
                            'status': 501,
                            'art_total': art_total,
                            'art_total_price': art_total_price,
                            'art_shipping_price': art_shipping_price,
                            'total': total,
                            'total_price': total_price,
                            'shipping_price': shipping_price,
                        }
                        return JsonResponse(context)

                    if prod.is_artificial_flower and flower_type == 'artificial':
                        shipping_price = get_product_shipping(price_obj, price_obj.product.product_class.name, quantity,
                                                              diffDays)
                        if price1 and quantity and shipping_price:
                            total = (price1 * quantity) + shipping_price
                            total_price = '₹ %s' %('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))
                        elif price1 and quantity and not shipping_price:
                            total = (price1 * quantity)
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))
                        else:
                            total = price1
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))

                        context = {
                            'status': 502,
                            'total': total,
                            'total_price': total_price,
                            'shipping_price': shipping_price,
                        }
                        return JsonResponse(context)

                    else:
                        shipping_price = get_product_shipping(price_obj,price_obj.product.product_class.name,quantity,diffDays)
                        if price1 and quantity and shipping_price:
                            total = (price1 * quantity)+shipping_price
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))

                        elif price1 and quantity and not shipping_price:
                            total = (price1 * quantity)
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))
                        else:
                            total = price1
                            total_price = '₹ %s' % ('{:,.2f}'.format(round(price1 * quantity * diffDays,0)))
                            shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price,0)))

                        context = {
                            'status': 503,
                            'total': total,
                            'total_price': total_price,
                            'shipping_price': shipping_price,
                        }
                        return JsonResponse(context)
                else:
                    shipping_price1 = get_product_shipping(price_obj, 'Rent', quantity, diffDays)
                    shipping_price2 = get_product_shipping(price_obj, 'Sale', quantity, diffDays)
                    price1 = get_price_new(price_obj, 'artificial')
                    price2 = get_price_new(price_obj, 'real')
                    if prod.is_artificial_flower and prod.is_real_flower:
                        art_rent_price = price1['rent_price']
                        art_sale_price = price1['sale_price']
                        if art_rent_price and quantity and shipping_price1:
                            total1 = (art_rent_price * quantity) + shipping_price1
                        elif art_rent_price and quantity and not shipping_price1:
                            total1 = (art_rent_price * quantity)
                        if art_sale_price and quantity and shipping_price2:
                            total2 = (art_sale_price * quantity) + shipping_price2
                        elif art_sale_price and quantity and not shipping_price2:
                            total2 = (art_sale_price * quantity)

                        art_total = '%s/ ₹ %s' % ('{:,.2f}'.format(total1), '{:,.2f}'.format(total2))
                        art_total_price = '₹ %s/ ₹ %s' % (
                        '{:,.2f}'.format(round(art_rent_price * quantity * diffDays,0)), '{:,.2f}'.format(round(art_sale_price * quantity * diffDays,0)))
                        art_shipping_price = '₹ %s/ ₹ %s' % (
                        '{:,.2f}'.format(round(shipping_price1,0)), '{:,.2f}'.format(round(shipping_price2,0)))

                        rent_price = price2['rent_price']
                        sale_price = price2['sale_price']
                        if rent_price and quantity and shipping_price1:
                            total1 = (rent_price * quantity) + shipping_price1
                        elif rent_price and quantity and not shipping_price1:
                            total1 = (rent_price * quantity)
                        if sale_price and quantity and shipping_price2:
                            total2 = (sale_price * quantity) + shipping_price2
                        elif sale_price and quantity and not shipping_price2:
                            total2 = (sale_price * quantity)

                        total = '%s/ ₹ %s' % ('{:,.2f}'.format(total1), '{:,.2f}'.format(total2))
                        total_price = '₹ %s/ ₹ %s' % (
                        '{:,.2f}'.format(round(rent_price * quantity * diffDays,0)), '{:,.2f}'.format(round(sale_price * quantity * diffDays,0)))
                        shipping_price = '₹ %s/ ₹ %s' % (
                        '{:,.2f}'.format(round(shipping_price1,0)), '{:,.2f}'.format(round(shipping_price2,0)))

                        context = {
                            'status': 501,
                            'art_total': art_total,
                            'art_total_price': art_total_price,
                            'art_shipping_price': art_shipping_price,
                            'total': total,
                            'total_price': total_price,
                            'shipping_price': shipping_price,
                        }
                        return JsonResponse(context)

                    if prod.is_artificial_flower and flower_type =='artificial':
                        shipping_price1 = get_product_shipping(price_obj, 'Rent', quantity, diffDays)
                        shipping_price2 = get_product_shipping(price_obj, 'Sale', quantity, diffDays)

                        rent_price = price1['rent_price']
                        sale_price = price1['sale_price']
                        if rent_price and quantity and shipping_price1:
                            total1 = (rent_price * quantity) + shipping_price1
                        elif rent_price and quantity and not shipping_price1:
                            total1 = (rent_price * quantity)
                        if sale_price and quantity and shipping_price2:
                            total2 = (sale_price * quantity) + shipping_price2
                        elif sale_price and quantity and not shipping_price2:
                            total2 = (sale_price * quantity)

                        total = '%s/ ₹ %s' % ('{:,.2f}'.format(total1), '{:,.2f}'.format(total2))
                        total_price = '₹ %s/ ₹ %s' % ('{:,.2f}'.format(round(rent_price* quantity * diffDays,0)), '{:,.2f}'.format(round(sale_price*quantity * diffDays,0)))
                        shipping_price = '₹ %s/ ₹ %s' % ('{:,.2f}'.format(round(shipping_price1,0)), '{:,.2f}'.format(round(shipping_price2,0)))

                        context = {
                            'status': 502,
                            'total': total,
                            'total_price': total_price,
                            'shipping_price': shipping_price,
                        }
                        return JsonResponse(context)
                    else:
                        shipping_price1 = get_product_shipping(price_obj, 'Rent', quantity, diffDays)
                        shipping_price2 = get_product_shipping(price_obj, 'Sale', quantity, diffDays)

                        rent_price = price2['rent_price']
                        sale_price = price2['sale_price']
                        if rent_price and quantity and shipping_price1:
                            total1 = (rent_price * quantity) + shipping_price1
                        elif rent_price and quantity and not shipping_price1:
                            total1 = (rent_price * quantity)
                        if sale_price and quantity and shipping_price2:
                            total2 = (sale_price * quantity) + shipping_price2
                        elif sale_price and quantity and not shipping_price2:
                            total2 = (sale_price * quantity)

                        total = '%s/ ₹ %s' % ('{:,.2f}'.format(total1), '{:,.2f}'.format(total2))
                        # total_price = '₹ %s/ ₹ %s' % (
                        # '{:,.2f}'.format(round(rent_price * quantity * diffDays,0)), '{:,.2f}'.format(round(sale_price * quantity * diffDays,0)))
                        # shipping_price = '₹ %s/ ₹ %s' % (
                        # '{:,.2f}'.format(round(shipping_price1,0)), '{:,.2f}'.format(round(shipping_price2,0)))

                        rent_total_price = '₹ %s' % ('{:,.2f}'.format(round(rent_price * quantity * diffDays, 0)))
                        sale_total_price = '₹ %s' % ('{:,.2f}'.format(round(sale_price * quantity * diffDays, 0)))
                        rent_shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price1, 0)))
                        sale_shipping_price = '₹ %s' % ('{:,.2f}'.format(round(shipping_price2, 0)))

                        context = {
                            'status' : 506,
                            'total' : total,
                            'rent_total_price' : rent_total_price,
                            'sale_total_price' : sale_total_price,
                            'rent_shipping_price' :rent_shipping_price,
                            'sale_shipping_price' :sale_shipping_price,

                        }
                        return JsonResponse(context)

            else:
                if prod.product_class.name in ['Rent', 'Professional', 'Sale']:
                    price_obj = prod.stockrecords.last()
                    price1 = get_product_shipping(price_obj,price_obj.product.product_class.name,quantity, diffDays)
                    if not price1:
                        status = 202
                        return HttpResponse(status)
                    if not price1['status']:
                        status = 203

                        msg = "Give range of quantity between %s and %s" %(price1['min_quantity'], price1['max_quantity'])

                        context = {
                            'status': 203,
                            'msg' : msg
                        }
                        return JsonResponse(context)

                    total = (price1['product_price'] * quantity) + price1['ship_price']
                    total = '{:,.2f}'.format(total)
                    total_price = '₹ %s' % ('{:,.2f}'.format(round(price1['product_price']* quantity,0)))
                    shipping_price = '₹ %s' % ('{:,.2f}'.format(round(price1['ship_price'],0)))
                    context = {
                        'status': 500,
                        'total': total,
                        'total_price': total_price,
                        'shipping_price': shipping_price
                    }
                    return JsonResponse(context)

                else:
                    price_obj = prod.stockrecords.last()
                    price1 = get_product_shipping(price_obj, 'Rent', quantity, diffDays)
                    price2 = get_product_shipping(price_obj, 'Sale', quantity, diffDays)
                    if not price1['status'] and not price2['status']:
                        status = 203
                        msg = "Give range of quantity for rent between %s ,%s and for sale between %s, %s " %(price1['min_quantity'], price1['max_quantity'],price2['min_quantity'], price2['max_quantity'])

                        context = {
                            'status': 203,
                            'msg': msg
                        }
                        return JsonResponse(context)

                    if not price1['status'] and price2['status']:
                        status = 204
                        msg = "Give range of quantity for rent between %s ,%s " % (price1['min_quantity'], price1['max_quantity'])
                        total1 = (price2['product_price']* quantity)  + price2['ship_price']
                        total = '{:,.2f}'.format(total1)

                        total_price = '₹ %s' % ('{:,.2f}'.format(round(price2['product_price'] * quantity,0)))
                        shipping_price = '₹ %s' % ('{:,.2f}'.format(round(price2['ship_price'],0)))

                        context = {
                            'status': 507,
                            'msg': msg,
                            'total' : total,
                            'total_price': total_price,
                            'shipping_price': shipping_price

                        }
                        return JsonResponse(context)

                    if price1['status'] and not price2['status']:

                        msg = "Give range of quantity for sale between %s ,%s " % (price2['min_quantity'], price2['max_quantity'])
                        totall = (price1['product_price'] * quantity) + price1['ship_price']
                        total = '{:,.2f}'.format(totall)
                        total_price = '₹ %s' % ('{:,.2f}'.format(round(price1['product_price'] * quantity,0)))
                        shipping_price = '₹ %s' % ('{:,.2f}'.format(round(price1['ship_price'],0)))

                        context = {
                            'status': 508,
                            'msg': msg,
                            'total' : total,
                            'total_price' : total_price,
                            'shipping_price' :shipping_price

                        }
                        return JsonResponse(context)

                    totall = (price1['product_price']* quantity) + price1['ship_price']
                    total2 = (price2['product_price']* quantity) + price2['ship_price']
                    total = '%s/ ₹ %s' % ('{:,.2f}'.format(totall), '{:,.2f}'.format(total2))
                    shipping_price = '₹ %s/ ₹ %s + ₹ %s/ ₹ %s' % (
                    '{:,.2f}'.format(round(price1['product_price'] * quantity,0)), '{:,.2f}'.format(round(price2['product_price'] * quantity,0)),
                    '{:,.2f}'.format(round(price1['ship_price'],0)), '{:,.2f}'.format(round(price2['ship_price'],0)))

                    # total_price = '₹ %s/ ₹ %s' % (
                    #     '{:,.2f}'.format(round(price1['product_price'] * quantity,0)), '{:,.2f}'.format(round(price2['product_price'] * quantity,0)))
                    # shipping_price = '₹ %s/ ₹ %s' % ('{:,.2f}'.format(round(price1['ship_price'],0)), '{:,.2f}'.format(round(price2['ship_price'],0)))
                    rent_total_price = '₹ %s' % ('{:,.2f}'.format(round(price1['product_price'] * quantity, 0)))
                    rent_shipping_price = '₹ %s' % ('{:,.2f}'.format(round(price1['ship_price'], 0)))
                    sale_total_price = '₹ %s' % ('{:,.2f}'.format(round(price2['product_price'] * quantity, 0)))
                    sale_shipping_price = '₹ %s' % ('{:,.2f}'.format(round(price2['ship_price'], 0)))

                    # context = {
                    #     'status' : 500,
                    #     'msg' : 'successful',
                    #     'total' : total,
                    #     'total_price' : total_price,
                    #     'shipping_price' :shipping_price
                    #
                    # }

                    context = {
                        'status': 506,
                        'total': total,
                        'rent_total_price': rent_total_price,
                        'sale_total_price': sale_total_price,
                        'rent_shipping_price': rent_shipping_price,
                        'sale_shipping_price': sale_shipping_price,

                    }
                    return JsonResponse(context)

        except Exception as e:
            import os
            import sys
            print('-----------in exception----------')
            print(e.args)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            return HttpResponse(str(e.args[0]))


def get_product_shipping_new(price, type, quantity, days, flower_type):

    ship_sale_price, ship_rent_price = 0, 0
    sale_price, rent_price = 0, 0

    costs_product = ProductCostEntries.objects.filter(product=price.product)
    if price.product.product_cost_type == 'Multiple':

        if type == 'Sale':
            costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity, requirement_day__gte = days ).order_by('-requirement_day')
            if not costs:
                costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity ).order_by('requirement_day')
            if costs:
                costs = costs.last()
                if costs.transport_cost and price.product.is_transporation_available:
                    ship_sale_price = costs.transport_cost
                else:
                    ship_sale_price = 0
                if costs.cost_incl_tax :
                    sale_price = costs.cost_incl_tax
                else:
                    if price.sale_price_with_tax and price.sale_round_off_price:
                        sale_price = price.sale_price_with_tax + price.sale_round_off_price
                    if price.sale_price_with_tax and not price.sale_round_off_price:
                        sale_price = round(price.sale_price_with_tax)
                    if not price.sale_price_with_tax and price.price_excl_tax:
                        sale_price = round(price.price_excl_tax)
                    ship_sale_price = 0
                context = {
                    'status' : True,
                    'ship_price' : ship_sale_price,
                    'product_price' : sale_price
                }

                return context
            else:
                costs = ProductCostEntries.objects.filter(product=price.product)
                if costs:
                    min_quantity = costs.aggregate(Min('quantity_from'))
                    max_quantity = costs.aggregate(Max('quantity_to'))
                    if min_quantity['quantity_from__min'] and max_quantity['quantity_to__max']:
                        context = {
                            'status' : False,
                            'min_quantity' : min_quantity['quantity_from__min'],
                            'max_quantity' : max_quantity['quantity_to__max'],
                        }
                        return context

            if price.sale_price_with_tax and price.sale_round_off_price:
                sale_price = price.sale_price_with_tax + price.sale_round_off_price
            if price.sale_price_with_tax and not price.sale_round_off_price:
                sale_price = round(price.sale_price_with_tax)
            if not price.sale_price_with_tax and price.price_excl_tax:
                sale_price = round(price.price_excl_tax)
            ship_sale_price = 0
            context = {
                'status': True,
                'ship_price': ship_sale_price,
                'product_price': sale_price
            }
            return context

        if type in ['Rent' ,'Professional']:
            costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity, rent_requirement_day__gte = days).order_by('-rent_requirement_day')
            if not costs:
                costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity).order_by('rent_requirement_day')
            if costs:
                costs = costs.last()
                if costs.rent_transport_cost and price.product.is_transporation_available:
                    ship_rent_price = costs.rent_transport_cost
                else:
                    ship_rent_price = 0
                if costs.rent_cost_incl_tax :
                    rent_price = costs.rent_cost_incl_tax
                else:
                    if price.rent_price_with_tax and price.rent_round_off_price:
                        rent_price = price.rent_price_with_tax + price.rent_round_off_price
                    if price.rent_price_with_tax and not price.rent_round_off_price:
                        rent_price = round(price.rent_price_with_tax)
                    if not price.rent_price_with_tax and price.rent_price:
                        rent_price = round(price.rent_price)
                    ship_rent_price = 0

                context = {
                    'status' : True,
                    'ship_price' : ship_rent_price,
                    'product_price' : rent_price
                }

                return context
            else:
                costs = ProductCostEntries.objects.filter(product=price.product)

                if costs:

                    min_quantity = costs.aggregate(Min('rent_quantity_from'))
                    max_quantity = costs.aggregate(Max('rent_quantity_to'))

                    if min_quantity['rent_quantity_from__min'] and max_quantity['rent_quantity_to__max']:
                        context = {
                            'status': False,
                            'min_quantity': min_quantity['rent_quantity_from__min'],
                            'max_quantity': max_quantity['rent_quantity_to__max'],
                        }
                        return context

            if price.rent_price_with_tax and price.rent_round_off_price:
                rent_price = price.rent_price_with_tax + price.rent_round_off_price
            if price.rent_price_with_tax and not price.rent_round_off_price:
                rent_price = round(price.rent_price_with_tax)
            if not price.rent_price_with_tax and price.rent_price:
                rent_price = round(price.rent_price)
            ship_rent_price = 0
            context = {
                'status': True,
                'ship_price': ship_rent_price,
                'product_price': rent_price
            }
            return context


    elif price.product.product_cost_type == 'Single':
        if price.product.is_artificial_flower and flower_type == 'artificial':
            if type == 'Sale':
                if price.art_sale_transportation_price and price.product.is_transporation_available:
                    ship_sale_price = price.art_sale_transportation_price
                return ship_sale_price

            if type in ['Rent', 'Professional']:
                if price.art_rent_transportation_price and price.product.is_transporation_available:
                    ship_rent_price = price.art_rent_transportation_price
                return ship_rent_price
        else:
            if type == 'Sale':
                if price.sale_transportation_price and price.product.is_transporation_available:
                    ship_sale_price = price.sale_transportation_price
                return ship_sale_price

            if type in ['Rent' ,'Professional']:
                if price.rent_transportation_price and price.product.is_transporation_available:
                    ship_rent_price = price.rent_transportation_price
                return ship_rent_price
    return 0


def get_price_new(price, flower_type= None):

    rent_price=0
    sale_price = 0
    cost = 0

    try:
        if price.product.is_real_flower and flower_type == 'real':

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
            context = {
                'rent_price' : rent_price,
                'sale_price' : sale_price,
            }
            return context

        return cost

    except Exception as e:

        return cost


send_sms = get_class('RentCore.email', 'send_sms')
def test_sms(request):
    # Voucher = get_model('voucher', 'Voucher')
    # Benefit = get_model('offer', 'Benefit')
    # Benefit.objects.filter(range__isnull=True).delete()
    msg_kwargs = {
        'message': "Order booked: Thank you for connecting with us. For your next purchase, we are going to share you more offers soon. Take Rent Pe",
        'mobile_number': '9049815844'
    }
    responce = send_sms(**msg_kwargs)
    print('responce@',responce)
    return HttpResponse("*******send sms*************"+str(responce.content))

# Product listing view for New Design
class CustomNewCatalogueView(ProductCategoryView):

    template_name = 'new_design/catalogue/category.html'
    form_class = BrowseSearchForm

    def get(self, request, *args, **kwargs):

        # get method to fetch initial data
        self.category = self.get_category()
        potential_redirect = self.redirect_if_necessary(request.path, self.category)
        search_value = None
        search_category = None
        search_price = None
        search_filter_list = None

        pk = kwargs.get('pk')
        print('data',request.GET.get('category'))

        if request.GET.get('price_range'):
            search_price = request.GET.get('price_range')

        if request.GET.get('mega_search'):
            search_value = str(request.GET.get('mega_search')).strip()

        if request.GET.get('category'):
            search_category = request.GET.get('category')
            pk = self.get_main_category(kwargs.get('pk'))

        if request.GET.get('filter_list'):
            search_filter_list = request.GET.get('filter_list')

        if potential_redirect is not None:
            return potential_redirect

        try:
            self.search_handler = self.get_search_handler(
                request.GET, request.get_full_path(), pk, search_value,
                search_category, search_price, None, None, search_filter_list
            )
        except InvalidPage:
            messages.error(request, _('The given page number was invalid.'))
            return redirect(self.category.get_absolute_url())

        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    def get_category(self):

        # get category according to URL
        if 'pk' in self.kwargs:
            return get_object_or_404(Category, pk=self.kwargs['pk'])
        elif 'category_slug' in self.kwargs:

            concatenated_slugs = self.kwargs['category_slug']
            slugs = concatenated_slugs.split(Category._slug_separator)
            try:
                last_slug = slugs[-1]
            except IndexError:
                raise Http404
            else:
                for category in Category.objects.filter(slug=last_slug):
                    if category.full_slug == concatenated_slugs:
                        message = ("Accessing categories without a primary keyis deprecated will be removed in Oscar " \
                                   " 1.2.")
                        warnings.warn(message, DeprecationWarning)

                        return category

        raise Http404

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            expected_path = category.get_absolute_url()
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_categories(self):
        return self.category.get_descendants_and_self()

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['category'] = self.category
        if self.category:
            category  = self.category
        else:
            category = None
       

        if self.request.GET.get('category'):
            cat_obj = Category.objects.filter(id= self.request.GET.get('category'))
            search_category = cat_obj.last()
        else:
            search_category = None

        try:
            context['search_form'] = self.form_class(self.request.GET, category=self.category)
        except:
            context['search_form'] = self.form_class(self.request.GET, category=None)
        if self.category.depth == 1:
            context['category_list'] = self.category.get_descendants().filter(show_on_frontside=True)
        else:
            context['category_list'] = self.category.get_parent().get_descendants().filter(show_on_frontside=True)
        context['service_rands'] = ['Service', 'Rent Or Sale']

        context['filters'] = self.get_selected_filter()

        context['title'] = self.get_title(kwargs.get('pk'))
        context['price_filter'] = self.get_price_filter(category,search_category)

        search_context = self.search_handler.get_search_context_data(
            self.context_object_name)
        context.update(search_context)

        return context

    def post(self, request, *args, **kwargs):

        # search post method custom.
        search_value = None
        try:
            search_data = request.POST.dict()
            search_value = search_data.get('q')
        except Exception as e:

            pass

        self.category = self.get_category()
        self.search_handler = self.get_search_handler(
            request.GET, request.get_full_path(), self.get_categories(), search_value)

        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    def get_selected_filter(self):
        selected_filter = {
            'filter_list': self.request.GET.get('filter_list'),
            'category': self.request.GET.get('category'),
        }

        if selected_filter.get('category'):
            selected_filter['category'] = int(selected_filter['category'])
        return selected_filter

    def get_main_category(self, pk):
        category = Category.objects.get(pk=int(pk))
        if category.depth == 1:
            return pk
        else:
            parent = category.get_parent()
            return parent.id

    def get_title(self, pk):

        category = Category.objects.get(pk=int(pk))
        if category.depth != 1 and self.request.GET.get('category'):
            try:
                category = Category.objects.get(id=int(self.request.GET.get('category')))
                return category.name
            except Exception as e:
                print(e.args)
        return category.name

    def get_price_filter(self, category = None, search_category= None):
        if search_category:
            cat_obj = CategoriesWisePriceFilter.objects.filter(category=search_category).order_by("id")
            if cat_obj:
                price_filter = []
                for cat in cat_obj:
                    choice_tup = (cat.range, cat.range)
                    if choice_tup not in price_filter:
                        price_filter.append(choice_tup)
            else:
                price_filter = (
                    ("0-500", "0 - 500"),
                    ("500-1000", "500 - 1000"),
                    ("1000-2000", "1000 - 2000"),
                    ("2000-5000", "2000 - 5000"),
                    ("5000-50000", "5000 & Above"),
                )

        elif category:
            cat_obj = CategoriesWisePriceFilter.objects.filter(category= category).order_by("id")
            if cat_obj:
                price_filter = []
                for cat in cat_obj:
                    choice_tup = (cat.range, cat.range)
                    if choice_tup not in price_filter:
                        price_filter.append(choice_tup)
            else:
                price_filter = (
                    ("0-500", "0 - 500"),
                    ("500-1000", "500 - 1000"),
                    ("1000-2000", "1000 - 2000"),
                    ("2000-5000", "2000 - 5000"),
                    ("5000-50000", "5000 & Above"),
                )
        else:
            price_filter = (
                ("0-500", "0 - 500"),
                ("500-1000", "500 - 1000"),
                ("1000-2000", "1000 - 2000"),
                ("2000-5000", "2000 - 5000"),
                ("5000-50000", "5000 & Above"),
            )
        return price_filter