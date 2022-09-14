# python imports
import datetime

# django imports
from django.shortcuts import HttpResponse, render, redirect
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy
from CustomDashboard.dashboard import utils

# packages imports
from oscar.core.loading import get_class, get_model

# internal import
from .asp_db_forms import *

MultiDB = get_model('partner', 'MultiDB')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')

generate_excel = get_class('dashboard.utils', 'generate_excel')


class ASPDBView(generic.ListView):
    """
    Method to view asp list.
    """

    template_name = 'dashboard/sales/asp_db/list.html'
    model = IndividualDB
    context_object_name = 'asp_db'
    paginate_by = 20
    form_class = SalesASPDBSearchForm
    second_form_class = SalesASPDBForm

    def get_queryset(self):

        qs = self.model.objects.all()
        data = self.request.GET
        ctx = dict()
        if data.get('category'):
            if data.get('type') == 'INDIVIDUAL':
                qs = IndividualDB.objects.filter(category_id=data.get('category'))
                ctx['individual'] = qs
            elif data.get('type') == 'MULTI':
                qs = MultiDB.objects.filter(category_id=data.get('category'))
                ctx['multi'] = qs

        return qs

    def get_context_data(self, **kwargs):

        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        ctx['form2'] = self.second_form_class(data=self.request.GET)
        ctx['individual'] = IndividualDB.objects.all().distinct('category')
        ctx['multi'] = MultiDB.objects.all().distinct('category')
        data = self.request.GET
        if data.get('category'):
            if data.get('type') == 'INDIVIDUAL':
                qs = IndividualDB.objects.filter(category_id=data.get('category'))
                ctx['individual'] = qs
            elif data.get('type') == 'MULTI':
                qs = MultiDB.objects.filter(category_id=data.get('category'))
                ctx['multi'] = qs

        return ctx


class CreateFormDB(generic.FormView):
    template_name = 'dashboard/sales/asp_db/form.html'
    form_class = DBSearchForm

    success_url = reverse_lazy('dashboard:individualdb-list')

    def get_context_data(self, **kwargs):
        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)

        return ctx


class IndividualDBListView(generic.ListView):
    """
    Method to view individual asp list.
    """

    template_name = 'dashboard/sales/asp_db/individual_asp/list.html'
    model = IndividualDB
    context_object_name = 'individual'
    paginate_by = 20
    form_class = DBSearchForm

    def get_queryset(self):
        qs = self.model.objects.all()
        data = self.request.GET

        if data.get('category'):
            qs = qs.filter(category=data.get('category'))

        return qs

    def get_context_data(self, **kwargs):
        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx


class MultiDBListView(generic.ListView):
    """
    Method to view mullti asp list.
    """

    template_name = 'dashboard/sales/asp_db/multi_asp/list.html'
    model = MultiDB
    context_object_name = 'multi'
    paginate_by = 20
    form_class = DBSearchForm

    def get_queryset(self):
        qs = self.model.objects.all()
        data = self.request.GET

        if data.get('category'):
            qs = qs.filter(category=data.get('category'))

        return qs

    def get_context_data(self, **kwargs):
        """
        Extended listview context data
        :param kwargs: default
        :return: context
        """
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(data=self.request.GET)
        return ctx


class CreateIndividualDB(generic.FormView):
    template_name = 'dashboard/sales/asp_db/individual_asp/form.html'
    form_class = IndividualDBModelForm

    success_url = reverse_lazy('dashboard:individualdb-list')

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()
        data = self.request.GET
        if data and data['category']:
            kwargs['initial'] = {'category': data['category']}

        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(self.request.POST.form)

    def post(self, request, *args, **kwargs):
        existing_asp = None
        if not request.user.is_superuser:
            return self.invalid_request()
        form=self.form_class(request.POST)
        individual_product = IndividualDB.objects.filter(category=request.POST['category'])

        if individual_product:
            existing_asp = individual_product.last().get_individual_asp_values()
            form = self.form_class(request.POST, instance=individual_product.last())
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            if existing_asp:
                return self.is_valid(form,existing_asp)
            else:
                return self.is_valid(form,existing_asp)
        else:
            return self.is_invalid(form)

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)

    def is_valid(self, form,existing_asp):

        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()

        if existing_asp:
            individual_obj = individual_product = IndividualDB.objects.filter(category=form.cleaned_data['category'])
            success_str = 'Replacing %s by %s for %s category.' % (existing_asp, individual_obj.last().get_individual_asp_values(),individual_obj.last().category.name)
            messages.success(self.request, success_str)
        else:
            messages.success(self.request, 'Individual ASP created successfully.')
        return redirect('/dashboard/partners/asp-db')

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')


class CreateMultiDBModelForm(generic.FormView):
    template_name = 'dashboard/sales/asp_db/multi_asp/form.html'
    form_class = MultiDBModelForm

    success_url = reverse_lazy('dashboard:multidb-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = self.request.GET
        if data and data['category']:
            kwargs['initial'] = {'category': data['category']}
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def post(self, request, *args, **kwargs):


        if not request.user.is_superuser:
            return self.invalid_request()
        multi_product = MultiDB.objects.filter(category=request.POST['category'])

        if multi_product:
            form = self.form_class(request.POST, instance=multi_product.last())
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)


    def is_valid(self, form):
        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()
        messages.success(self.request, 'Multi ASP created successfully.')
        return redirect('/dashboard/partners/asp-db')

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')


class IndividualDBUpdateView(generic.View):
    """
    To update individual db.
    """
    context_object_name = 'individual'

    template_name = 'dashboard/sales/asp_db/individual_asp/update_form.html'
    form_class = IndividualDBModelForm

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        individual_product = IndividualDB.objects.filter(id=pk)

        if not individual_product:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=individual_product.last())

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        individual_product = IndividualDB.objects.filter(id=pk)

        if not individual_product:
            return self.invalid_request()

        form = self.form_class(request.POST, instance=individual_product.last())
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()
        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/partners/asp-db')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form
        return render(self.request, self.template_name, context=context)


class MultiDBUpdateView(generic.View):
    """
    To update multi db.
    """
    context_object_name = 'multi'

    template_name = 'dashboard/sales/asp_db/multi_asp/update_form.html'
    form_class = MultiDBModelForm

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        multi_product = MultiDB.objects.filter(id=pk)

        if not multi_product:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=multi_product.last())

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        multi_product = MultiDB.objects.filter(id=pk)

        if not multi_product:
            return self.invalid_request()

        form = self.form_class(request.POST, instance=multi_product.last())

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()
        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/partners/asp-db')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)


class IndividualDBDetailView(generic.DetailView):
    model = IndividualDB
    template_name = 'dashboard/sales/asp_db/individual_asp/details.html'
    context_object_name = 'individual'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MultiDetailView(generic.DetailView):
    model = MultiDB
    template_name = 'dashboard/sales/asp_db/multi_asp/details.html'
    context_object_name = 'multi'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        data = self.request.GET

        if data.get('category'):
            qs = qs.filter(category=data.get('category'))

        return qs


def find_details(request):
    category = request.GET.get('category')
    type = request.GET.get('type')

    try:
        if type and category:
            if type == 'INDIVIDUAL':
                individual_obj = IndividualDB.objects.filter(category_id=category)

                if individual_obj:
                    obj = individual_obj.last()
                    url = '/dashboard/partners/individualdb/details/' + str(obj.id)
                    return redirect(url)

                messages.error(request, 'No record found.')
                return redirect('/dashboard/partners/asp-db')

            else:
                multi_obj = MultiDB.objects.filter(category_id=category)
                if multi_obj:
                    obj = multi_obj.last()
                    url = '/dashboard/partners/multidb/details/' + str(obj.id)
                    return redirect(url)

            messages.error(request, 'No record found.')
            return redirect('/dashboard/partners/asp-db')

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


class IndividualDBDelete(generic.View):
    """
    Delete individual db
    """

    template_name = 'dashboard/sales/asp_db/individual_asp/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        individual_product = IndividualDB.objects.filter(id=pk)

        if not individual_product:
            return self.invalid_request()

        context = dict()
        context['product'] = individual_product.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            individual_product = IndividualDB.objects.filter(id=pk)

            if not individual_product:
                return self.invalid_request()

            IndividualDB.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/partners/asp-db')

        except:

            return self.invalid_request()


class MultiDBDelete(generic.View):
    """
    delete multi db
    """

    template_name = 'dashboard/sales/asp_db/multi_asp/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        multi_product = MultiDB.objects.filter(id=pk)

        if not multi_product:
            return self.invalid_request()

        context = dict()
        context['product'] = multi_product.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            multi_product = MultiDB.objects.filter(id=pk)

            if not multi_product:
                return self.invalid_request()

            MultiDB.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/partners/asp-db')

        except:

            return self.invalid_request()


def export_individualdb(request):
    """

            :param request:
            :return:
            """

    try:

        data = request.GET
        queryset = IndividualDB.objects.all()

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('category'):
            queryset = queryset.filter(category_id=data.get('category'))

        excel_data = [
            [
                'Sr. No', 'Category', 'Individual ASP', 'Date Created'
            ]
        ]

        counter = 0

        for obj in queryset:
            ret = ''
            counter = counter + 1
            excel_data.append(
                [
                    str(counter),
                    str(obj.category),
                    str(obj.get_individual_asp_values()),
                    str(obj.date_created.date()),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'individual_db%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


def export_multidb(request):
    """

            :param request:
            :return:
            """

    try:

        data = request.GET
        queryset = MultiDB.objects.all()

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('category'):
            queryset = queryset.filter(category_id=data.get('category'))


        excel_data = [
            [
                'Sr. No', 'Category', 'Frontliener', 'Backup1', 'Backup2', 'Date Created'
            ]
        ]

        counter = 0

        for obj in queryset:
            ret = ''
            counter = counter + 1
            excel_data.append(
                [
                    str(counter),
                    str(obj.category),
                    str(obj.get_frontliener_values()),
                    str(obj.get_backup1_values()),
                    str(obj.get_backup2_values()),

                    str(obj.date_created.date()),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'multi_db%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_multi_data(request):
    """
    Ajax method to delete bulk premium.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        multi_id = request.GET.get('multi_id')
        if not multi_id:
            messages.error(request, 'Something went wrong.....')
            return HttpResponse('IN_SERVER')

        multi_list = multi_id.split(',')

        MultiDB.objects.filter(id__in=multi_list).delete()

        _pr_str = 'db'
        if len(multi_list) > 1:
            _pr_str = 'dbs'

        success_str = 'Total multi  %s %s deleted successfully.' % (len(multi_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')


@csrf_exempt
def delete_bulk_individual_data(request):
    """
    Ajax method to delete bulk premium.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        individual_id = request.GET.get('individual_id')
        if not individual_id:
            messages.error(request, 'Something went wrong.....')
            return HttpResponse('IN_SERVER')

        individual_list = individual_id.split(',')

        IndividualDB.objects.filter(id__in=individual_list).delete()

        _pr_str = 'db'
        if len(individual_list) > 1:
            _pr_str = 'dbs'

        success_str = 'Total individual  %s %s deleted successfully.' % (len(individual_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')


# Ajax Calls
def load_vendors(request):
    category_id = request.GET.get('category_id')
    prods = None

    if category_id:
        Category = get_model('catalogue', 'Category')

        cat = Category.objects.get(id=category_id)

        prods = cat.product_set.all().values_list('stockrecords__partner')
        li = list(prods)
        vendors = Partner.objects.filter(id__in=prods, users__is_active = True)

    return render(request, 'dashboard/sales/individualdropdown_form.html', {'prods': vendors})


def load_categories(request):
    type_value = request.GET.get('type_value')

    prods = None
    if type_value:
        if type_value == 'INDIVIDUAL':
            cat_db = MultiDB.objects.all().values_list('category')
            cat = Category.objects.exclude(id__in=cat_db)
        else:
            cat_db = IndividualDB.objects.all().values_list('category')
            cat = Category.objects.exclude(id__in=cat_db)

    return render(request, 'dashboard/sales/categories_dropdown.html', {'prods': cat})