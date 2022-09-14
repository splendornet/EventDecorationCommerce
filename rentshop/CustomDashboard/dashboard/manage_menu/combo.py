# python imports
import datetime

# django imports
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# internal imports
from oscar.core.loading import get_class, get_model
from .combo_forms import *
from CustomDashboard.dashboard import utils


ComboProductsMasterModelForm = get_class('dashboard.combo.combo_forms', 'ComboProductsMasterModelForm')
Product = get_model('catalogue', 'Product')
ComboProductsMaster = get_model('catalogue', 'ComboProductsMaster')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
Manage_Menu = get_model('HeaderMenu', 'Manage_Menu')
ExhibitionOffers = get_model('HeaderMenu', 'ExhibitionOffers')
ExhibitionOffersCategory = get_model('HeaderMenu', 'ExhibitionOffersCategory')


class CreateManageMenu(generic.View):

    """
    To create corporate offer.
    """

    template = 'dashboard/manage_menu/form_v1.html'
    form_class = ManagerMenuMasterModelForm
    formset = ProductFormsetExtra

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        user = request.user
        if not user.is_active or not user.is_staff:
            return self.invalid_request()

        if not user.is_superuser:
            return self.invalid_request()

        context = dict()
        form = self.form_class

        context['manage_form'] = form
        context['manage_form_set'] = self.formset

        return render(self.request, self.template, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)
        formset = self.formset(request.POST)

        if not formset.is_valid() or not form.is_valid():
            return self.is_invalid(form, formset)

        formset_product_id = []
        formset_product = []

        if formset.is_valid():

            # validate vendor products
            for fx in formset:
                if fx.cleaned_data.get('manage_product'):
                    formset_product_id.append(fx.cleaned_data.get('manage_product').id)
                    formset_product.append(fx.cleaned_data.get('manage_product'))

        if len(formset_product) == 0:
            return self.is_invalid(form, formset)

        # save.
        title = form.cleaned_data.get('offer_title')
        header_menu = form.cleaned_data.get('header_menu')

        # create manage menu product
        manage_data = {
            'offer_title': title, 'header_menu': header_menu,
        }

        manage_obj = Manage_Menu.objects.create(**manage_data)

        for product in formset_product:
            ManageMenuMasterProducts.objects.create(
                manage_menu=manage_obj, manage_product=product
            )

        messages.success(request, 'Offer successfully.')
        return redirect(reverse('dashboard:manage-menu-index'))

    def is_invalid(self, form, formset):

        messages.error(self.request, 'Please correct below errors.')

        context = dict()
        context['manage_form'] = form
        context['manage_form_set'] = formset

        return render(self.request, self.template, context=context)


class UpdateHeaderMenu(generic.View):

    """
    To update corporate offer.
    """

    template = 'dashboard/manage_menu/form_v1.html'
    form_class = ManagerMenuMasterModelForm
    formset = ProductFormsetExtra


    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def invalid_request(self):

        messages.error(self.request, 'Invalid request.')

    def get(self, request, *args, **kwargs):

        user = request.user
        pk = kwargs.get('pk')

        if not user.is_active or not user.is_staff:
            return self.invalid_request()

        if not user.is_superuser:
            return self.invalid_request()

        if not pk or not Manage_Menu.objects.filter(id=pk):
            return self.invalid_request()

        manage_obj = Manage_Menu.objects.get(id=pk)

        context = dict()
        form = self.form_class(instance=manage_obj)

        context['manage_form'] = form
        context['type'] = 'update'
        context['manage_form_set'] = self.formset(
            instance=manage_obj,
        )

        return render(self.request, self.template, context=context)

    def post(self, request, *args, **kwargs):

        user = request.user
        pk = kwargs.get('pk')
        manage_obj = Manage_Menu.objects.get(id=pk)

        form = self.form_class(data=request.POST, instance=manage_obj)
        formset = self.formset(request.POST)



        if not formset.is_valid() or not form.is_valid():
            return self.is_invalid(form, formset)

        formset_product_id = []
        formset_product = []
        if formset.is_valid():

            # validate vendor products
            for fx in formset:
                if fx.cleaned_data.get('manage_product'):
                    formset_product_id.append(fx.cleaned_data.get('manage_product').id)
                    formset_product.append(fx.cleaned_data.get('manage_product'))

        if len(formset_product) == 0:
            return self.is_invalid(form, formset)

        if len(formset_product_id) != len(set(formset_product_id)):
            return self.is_invalid(form, formset)

        # update product
        base_form = form.save(commit=True)
        base_form.save()

        for products in formset_product:
            ManageMenuMasterProducts.objects.get_or_create(
                manage_menu=base_form, manage_product=products
            )

        messages.success(request, 'offer successfully.')
        return redirect(reverse('dashboard:manage-menu-index'))

    def is_invalid(self, form, formset):

        messages.error(self.request, 'Please correct below errors.')

        context = dict()
        context['manage_form'] = form
        context['type'] = 'update'
        context['manage_form_set'] = formset

        return render(self.request, self.template, context=context)


class ManageMenuIndexView(generic.ListView):

    """
    Corporate offer index page view.
    """

    template_name = 'dashboard/manage_menu/index.html'
    model = Manage_Menu
    context_object_name = 'managemenu'
    paginate_by = 20
    form_class = ManageMenuSearchForm

    def get(self, request, *args, **kwargs):

        if request.user.is_active and request.user.is_superuser:
            return super(ManageMenuIndexView, self).get(request, *args, **kwargs)

        messages.error(request, 'Invalid request')
        return redirect('/dashboard')

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all()

            data = self.request.GET

            if data.get('header_menu'):
                queryset = queryset.filter(header_menu_id=data.get('header_menu'))

            if data.get('offer_title'):
                queryset = queryset.filter(offer_title__icontains=data.get('offer_title'))


            return queryset

        except Exception as e:

            return []

    def get_context_data(self, **kwargs):

        ctx = super(ManageMenuIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


class DeleteManageMenu(generic.View):

    """
    method to delete
    """

    template_name = 'dashboard/manage_menu/delete.html'

    def invalid_request(self, message):
        messages.error(self.request, messages)
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        user = request.user

        if not pk or not user.is_active:
            return self.invalid_request('Invalid request.')

        if not user.is_staff:
            return self.invalid_request('Invalid request.')

        context = dict()
        context['menu'] = Manage_Menu.objects.get(id=pk)

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:
            pk = kwargs.get('pk')

            offer_title = ''
            menu = Manage_Menu.objects.get(id=pk)
            offer_title = menu.offer_title
            header = menu.header_menu
            menu.delete()

            messages.success(self.request, '%s delete for %s successfully' % (offer_title,header))

        except:

            messages.error(self.request, 'Something went wrong.')

        return redirect(reverse('dashboard:manage-menu-index'))


def export_menu(request):

    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = Manage_Menu.objects.all()


        if data.get('header_menu'):
            queryset = queryset.filter(header_menu_id=data.get('header_menu'))

        if data.get('offer_title'):
            queryset = queryset.filter(offer_title__icontains=data.get('offer_title'))

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        excel_data = [
            [
                'Sr. No', 'header_menu', 'Offer Price',
                'No. Of Products',
                'Date Created', 'Products'
            ]
        ]

        counter = 0

        for obj in queryset:

            list_pr = list(ManageMenuMasterProducts.objects.filter(manage_menu = obj).values_list('manage_product__title', flat=True))
            cnt = ManageMenuMasterProducts.objects.filter(manage_menu = obj).count()

            list_pr = ','.join(list_pr)
            counter = counter + 1

            excel_data.append(
                [
                    str(counter),str(obj.header_menu), str(obj.offer_title),

                    str(cnt),

                    str(obj.date_created.date()),
                    list_pr
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'menu%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_menu_data(request):

    """
    Ajax method to delete bulk manage menu.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        menu_id = request.GET.get('menu_id')

        if not menu_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        menu_list = menu_id.split(',')

        Manage_Menu.objects.filter(id__in=menu_list).delete()

        _pr_str = 'menu'
        if len(menu_list) > 1:
            _pr_str = 'menus'

        success_str = 'Total %s %s offer deleted successfully.' % (len(menu_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')

@csrf_exempt
def delete_header_product(request):
    """
        Ajax method to delete product image.
        """

    if request.is_ajax():
        form_id = request.POST.get('form_id')

        manage_product_id = request.POST.get('manage_product_id')

        if not manage_product_id or not form_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        if not ManageMenuMasterProducts.objects.filter(manage_menu_id=form_id,manage_product_id = manage_product_id ):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        ManageMenuMasterProducts.objects.filter(manage_menu_id=form_id,manage_product_id = manage_product_id).delete()
        messages.success(request, 'Product removed successfully.')
        return HttpResponse('TRUE')

    return HttpResponse('IN_SERVER')

class ExhibitionOffersIndexView(generic.ListView):

    """
    Exhibition offer index page view.
    """

    template_name = 'dashboard/manage_menu/exhibition_offers/index.html'
    model = ExhibitionOffers
    context_object_name = 'managemenu'
    paginate_by = 20
    form_class = ManageMenuSearchForm

    def get(self, request, *args, **kwargs):

        if request.user.is_active and request.user.is_superuser:
            return super(ExhibitionOffersIndexView, self).get(request, *args, **kwargs)
        messages.error(request, 'Invalid request')
        return redirect('/dashboard')

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all()

            data = self.request.GET

            if data.get('header_menu'):
                queryset = queryset.filter(header_menu_id=data.get('header_menu'))

            return queryset

        except Exception as e:

            return []

    def get_context_data(self, **kwargs):

        ctx = super(ExhibitionOffersIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx

class CreateExhibitionOffers(generic.View):

    """
    To create Exhibition offer.
    """

    template = 'dashboard/manage_menu/exhibition_offers/form_v1.html'
    form_class = ExhibitionOffersModelForm
    formset = CategoryFormsetExtra

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        user = request.user
        if not user.is_active or not user.is_staff:
            return self.invalid_request()

        if not user.is_superuser:
            return self.invalid_request()

        context = dict()
        form = self.form_class

        context['manage_form'] = form
        context['manage_form_set'] = self.formset

        return render(self.request, self.template, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)
        formset = self.formset(request.POST)

        if not formset.is_valid() or not form.is_valid():
            return self.is_invalid(form, formset)

        formset_product_id = []
        formset_product = []

        if formset.is_valid():

            # validate vendor products
            for fx in formset:
                if fx.cleaned_data.get('manage_category'):
                    formset_product_id.append(fx.cleaned_data.get('manage_category').id)
                    formset_product.append(fx.cleaned_data.get('manage_category'))

        if len(formset_product) == 0:
            return self.is_invalid(form, formset)

        # save.
        header_menu = form.cleaned_data.get('header_menu')

        # create exhibition offer
        manage_data = {
             'header_menu': header_menu,
        }

        manage_obj = ExhibitionOffers.objects.create(**manage_data)

        for product in formset_product:
            ExhibitionOffersCategory.objects.create(
                manage_menu=manage_obj, manage_category=product
            )

        messages.success(request, 'Offer successfully.')
        return redirect(reverse('dashboard:exhibition-offers-index'))

    def is_invalid(self, form, formset):

        messages.error(self.request, 'Please correct below errors.')

        context = dict()
        context['manage_form'] = form
        context['manage_form_set'] = formset

        return render(self.request, self.template, context=context)


class UpdateExhibitionOffers(generic.View):

    """
    To create combo offer.
    """

    template = 'dashboard/manage_menu/exhibition_offers/form_v1.html'
    form_class = ExhibitionOffersModelForm
    formset = CategoryFormsetExtra


    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def invalid_request(self):

        messages.error(self.request, 'Invalid request.')

    def get(self, request, *args, **kwargs):

        user = request.user
        pk = kwargs.get('pk')

        if not user.is_active or not user.is_staff:
            return self.invalid_request()

        if not user.is_superuser:
            return self.invalid_request()

        if not pk or not ExhibitionOffers.objects.filter(id=pk):
            return self.invalid_request()

        manage_obj = ExhibitionOffers.objects.get(id=pk)

        context = dict()
        form = self.form_class(instance=manage_obj)

        context['manage_form'] = form
        context['type'] = 'update'
        context['manage_form_set'] = self.formset(
            instance=manage_obj,
        )

        return render(self.request, self.template, context=context)

    def post(self, request, *args, **kwargs):

        user = request.user
        pk = kwargs.get('pk')
        manage_obj = ExhibitionOffers.objects.get(id=pk)

        form = self.form_class(data=request.POST, instance=manage_obj)
        formset = self.formset(request.POST)



        if not formset.is_valid() or not form.is_valid():
            return self.is_invalid(form, formset)

        formset_product_id = []
        formset_product = []
        if formset.is_valid():

            # validate vendor products
            for fx in formset:
                if fx.cleaned_data.get('manage_category'):
                    formset_product_id.append(fx.cleaned_data.get('manage_category').id)
                    formset_product.append(fx.cleaned_data.get('manage_category'))

        if len(formset_product) == 0:
            return self.is_invalid(form, formset)

        if len(formset_product_id) != len(set(formset_product_id)):
            return self.is_invalid(form, formset)

        # update exhibition offer
        base_form = form.save(commit=True)
        base_form.save()

        for products in formset_product:
            ExhibitionOffersCategory.objects.get_or_create(
                manage_menu=base_form, manage_category=products
            )

        messages.success(request, 'offer successfully.')
        return redirect(reverse('dashboard:exhibition-offers-index'))

    def is_invalid(self, form, formset):

        messages.error(self.request, 'Please correct below errors.')

        context = dict()
        context['manage_form'] = form
        context['type'] = 'update'
        context['manage_form_set'] = formset

        return render(self.request, self.template, context=context)

class DeleteExhibitionOffers(generic.View):

    """
    method to delete
    """

    template_name = 'dashboard/manage_menu/delete.html'

    def invalid_request(self, message):
        messages.error(self.request, messages)
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        user = request.user

        if not pk or not user.is_active:
            return self.invalid_request('Invalid request.')

        if not user.is_staff:
            return self.invalid_request('Invalid request.')

        context = dict()
        context['menu'] = ExhibitionOffers.objects.get(id=pk)

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:
            pk = kwargs.get('pk')

            offer_title = ''
            menu = ExhibitionOffers.objects.get(id=pk)
            header = menu.header_menu
            menu.delete()

            messages.success(self.request, 'delete for %s successfully' % (header))

        except:

            messages.error(self.request, 'Something went wrong.')

        return redirect(reverse('dashboard:exhibition-offers-index'))

def export_exhibition(request):

    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = ExhibitionOffers.objects.all()


        if data.get('header_menu'):
            queryset = queryset.filter(header_menu_id=data.get('header_menu'))

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        excel_data = [
            [
                'Sr. No', 'header_menu',
                'No. Of Categroy',
                'Date Created', 'Category'
            ]
        ]

        obj = queryset.first()
        counter = 0

        list_pr = list(
            ExhibitionOffersCategory.objects.filter(manage_menu=obj, manage_category__depth=1).values_list('manage_category__name', flat=True))
        cnt = ExhibitionOffersCategory.objects.filter(manage_menu=obj, manage_category__depth=1).count()

        list_pr = ','.join(list_pr)
        counter = counter + 1

        excel_data.append(
            [
                str(counter), str(obj.header_menu),

                str(cnt),

                str(obj.date_created.date()),
                list_pr
            ]
        )

        prms = {
            'type': 'excel',
            'filename': 'exhibition_menu%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_exhibition_menu_data(request):

    """
    Ajax method to delete bulk manage menu.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        menu_id = request.GET.get('menu_id')

        if not menu_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        menu_list = menu_id.split(',')

        ExhibitionOffers.objects.filter(id__in=menu_list).delete()

        _pr_str = 'menu'
        if len(menu_list) > 1:
            _pr_str = 'menus'

        success_str = 'Total %s %s exhibition offer deleted successfully.' % (len(menu_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')

@csrf_exempt
def delete_header_category(request):
    """
        Ajax method to delete product image.
        """

    if request.is_ajax():
        form_id = request.POST.get('form_id')

        manage_category_id = request.POST.get('manage_category_id')

        if not manage_category_id or not form_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        if not ExhibitionOffersCategory.objects.filter(manage_menu_id=form_id,manage_category_id = manage_category_id ):

            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        ExhibitionOffersCategory.objects.filter(manage_menu_id=form_id,manage_category_id = manage_category_id).delete()
        messages.success(request, 'Category removed successfully.')
        return HttpResponse('TRUE')

    return HttpResponse('IN_SERVER')

