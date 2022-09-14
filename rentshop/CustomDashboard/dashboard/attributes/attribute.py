# python imports
import datetime

# django imports
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy

# internal imports
from oscar.core.loading import get_class, get_model
from .attribute_form import *
from CustomDashboard.dashboard import utils


Attribute = get_model('catalogue', 'Attribute')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')

class AttributeIndexView(generic.ListView):

    """
    attribute product index page view.
    """

    template_name = 'dashboard/attribute/index.html'
    model = Attribute
    context_object_name = 'attributes'
    paginate_by = 20
    form_class = AttributeSearchForm

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all()

            data = self.request.GET

            if data.get('attribute'):
                queryset = queryset.filter(attribute__icontains=data.get('attribute'))

            return queryset

        except Exception as e:
            print(e.args)

            return []

    def get_context_data(self, **kwargs):

        ctx = super(AttributeIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx

class CreateAttribute(generic.View):

    """
    To create attribute.
    """

    template_name = 'dashboard/attribute/form.html'
    form_class = AttributeSearchForm
    formset = AttributeFormsetExtra

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

        context['form'] = form
        context['attribute_formset'] = self.formset

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)
        formset = self.formset(request.POST)

        if not formset.is_valid() or not form.is_valid():
            return self.is_invalid(form, formset)

        formset_attribute = []

        if formset.is_valid():

            for fx in formset:
                if fx.cleaned_data.get('value'):
                    formset_attribute.append(fx.cleaned_data.get('value'))

        if len(formset_attribute) == 0:
            return self.is_invalid(form, formset)

        attribute = form.cleaned_data.get('attribute')

        for value in formset_attribute:
            Attribute.objects.get_or_create(
                attribute=attribute, value=value
            )

        messages.success(request, 'Attribute created successfully.')
        return redirect(reverse('dashboard:attribute-index'))

    def is_invalid(self, form, formset):

        messages.error(self.request, 'Please correct below errors.')

        context = dict()
        context['form'] = form
        context['attribute_formset'] = formset

        return render(self.request, self.template_name, context=context)



class AttributeUpdateView(generic.View):

    """
    To update attribute product.
    """
    context_object_name = 'product'

    template_name = 'dashboard/attribute/update_form.html'
    form_class = AttributeModelForm
    formset = AttributeFormsetExtra

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        attribute_product = Attribute.objects.filter(id=pk)

        if not attribute_product:
            return self.invalid_request()

        context = dict()
        context['form'] = self.form_class(instance=attribute_product.last())
        context['type'] = 'update'

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        attribute_product = Attribute.objects.filter(id=pk)

        if not attribute_product:
            return self.invalid_request()

        form = self.form_class(request.POST, instance=attribute_product.last())

        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()
        form.save_m2m()
        messages.success(self.request, 'Record updated successfully.')
        return redirect('/dashboard/catalogue/attribute/index/')

    def is_invalid(self, form):

        context = dict()
        context['form'] = form

        return render(self.request, self.template_name, context=context)

class AttributeDelete(generic.View):

    """
    Attribute delete view
    """

    template_name = 'dashboard/attribute/delete.html'

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        if not request.user.is_superuser or not pk:
            return self.invalid_request()

        attribute_product = Attribute.objects.filter(id=pk)

        if not attribute_product:
            return self.invalid_request()

        context = dict()
        context['product'] = attribute_product.last()

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            pk = kwargs.get('pk')

            if not request.user.is_superuser or not pk:
                return self.invalid_request()

            attribute_product = Attribute.objects.filter(id=pk)

            if not attribute_product:
                return self.invalid_request()

            Attribute.objects.filter(id=pk).delete()

            messages.success(request, 'Record deleted successfully.')
            return redirect('/dashboard/catalogue/attribute/index/')

        except:
            return self.invalid_request()


def export_attribute(request):

    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = Attribute.objects.all()

        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('attribute'):
            queryset = queryset.filter(attribute__icontains=data.get('attribute'))

        excel_data = [
            [
                'Sr. No', 'Attribute Name',
            ]
        ]

        counter = 0

        for obj in queryset:
            counter = counter + 1
            excel_data.append(
                [
                    str(counter),
                    str(obj.attribute),
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'attribute_product_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        import os
        import sys
        print('-----------in exception----------')
        print(e.args)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_attribute_data(request):

    """
    Ajax method to delete bulk attribute.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        attribute_id = request.GET.get('attribute_id')

        if not attribute_id:
            messages.error(request, 'Something went wrong.....')
            return HttpResponse('IN_SERVER')

        attribute_list = attribute_id.split(',')

        Attribute.objects.filter(id__in=attribute_list).delete()

        _pr_str = 'product'
        if len(attribute_list) > 1:
            _pr_str = 'products'

        success_str = 'Total attribute %s %s deleted successfully.' % (len(attribute_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.*')
    return HttpResponse('IN_SERVER')


# Ajax Calls
def load_products(request):
    category_id = request.GET.get('category_id')
    prods = None

    if category_id:
        Category = get_model('catalogue', 'Category')

        cat = Category.objects.get(id=category_id)

        prods = cat.product_set.all()

    return render(request, 'admin/partials/product_dropdown_list_options.html', {'prods': prods})