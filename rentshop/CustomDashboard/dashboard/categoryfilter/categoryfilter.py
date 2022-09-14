from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import generic
from oscar.core.loading import *
from .categoryfilter_forms import *
from django.views.decorators.csrf import csrf_exempt
from .. import utils

CategoriesWiseFilterValue = get_model('catalogue','CategoriesWiseFilterValue')
Category = get_model('catalogue','Category')
CategoriesWisePriceFilter = get_model('catalogue', 'CategoriesWisePriceFilter')


class CategoryFilterIndexView(generic.ListView):


    template_name = 'dashboard/category_filter/form.html'
    model = Category
    context_object_name = 'cat_obj'
    paginate_by = 20
    form_class = CategoryFilterSearchForm

    def get_queryset(self):

        qs = self.model.objects.all()
        data = self.request.GET
        ctx = dict()
        if data.get('category'):

            qs = qs.filter(id=data.get('category'))
        return qs

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


class CategoryFilterUpdateView(generic.FormView):

    """
    category filter view that can both create and update view.
    """

    template_name = 'dashboard/category_filter/form_v1.html'
    form = CategoryFilterModelForm

    def get(self, request, *args, **kwargs):

        form = self.form()
        categegory_name = ''
        pk = kwargs.get('pk')
        if int(pk) not in Category.objects.all().values_list('id',flat=True):
            messages.error(request, 'Invalid request.')
            return redirect('/dashboard')

        if pk:
            if CategoriesWiseFilterValue.objects.filter(category__id=pk):

                cat_obj = CategoriesWiseFilterValue.objects.filter(category__id=pk)
                obj = cat_obj.last()
                category_name = obj.category.name
                form = self.form(instance=obj)
            else:
                cat_obj = Category.objects.filter(id = pk)
                category_name = cat_obj.last().name
                form = self.form()
        return render(request, self.template_name, {'form': form, 'category_name': category_name,})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST)

        if not form.is_valid():
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard')

        pk = kwargs.get('pk')
        obj = CategoriesWiseFilterValue.objects.filter(category__id=pk)
        cat_obj = Category.objects.filter(id=pk)
        if obj:
            CategoriesWiseFilterValue.objects.filter(category__id=pk).update(category=cat_obj.last(),
                                                                             filter_names=form.cleaned_data[
                                                                                 'filter_names'])


        else:
            CategoriesWiseFilterValue.objects.create(category=cat_obj.last(),
                                                     filter_names=form.cleaned_data['filter_names'])

        return self.success_url()

    def success_url(self):

        messages.success(self.request, 'filter for category saved successfully.')
        return redirect('/dashboard/catalogue/category_filter/')

# class CategoryPriceFilterIndexView(generic.ListView):
#
#
#     template_name = 'dashboard/category_filter/price/list.html'
#     model = CategoriesWisePriceFilter
#
#     context_object_name = 'cat_obj'
#     paginate_by = 20
#     form_class = PriceFilterSearchForm
#
#     def get_queryset(self):
#
#         qs = self.model.objects.all()
#         data = self.request.GET
#         ctx = dict()
#         if data.get('category'):
#
#             qs = qs.filter(id=data.get('category'))
#         return qs
#
#     def get_context_data(self, **kwargs):
#
#         ctx = super().get_context_data(**kwargs)
#         ctx['form'] = self.form_class(self.request.GET)
#
#         return ctx

class CategoryPriceFilterIndexView(generic.ListView):
    """
    View to list price range database
    """
    template_name = 'dashboard/category_filter/price/list.html'
    model = CategoriesWisePriceFilter
    search_form = PriceFilterSearchForm

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        return super(CategoryPriceFilterIndexView, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(CategoryPriceFilterIndexView, self).get_context_data()
        obj_list = ctx['object_list'].filter()
        filtered_data = self.apply_filter(obj_list)
        ctx['object_list'] = self.get_data(filtered_data)
        ctx['form'] = self.search_form(data=self.request.GET)
        return ctx

    def apply_filter(self, queryset):
        if self.request.GET.get('category'):
            queryset = queryset.filter(category__id=self.request.GET.get('category'))
        return queryset

    def get_data(self, queryset):

        pr_obj = queryset.order_by('category__id').distinct('category__id')
        data_list = []
        for obj in pr_obj:
            price_rng = CategoriesWisePriceFilter.objects.filter(category=obj.category)
            data_list.append(
                {
                    'category': obj.category,
                    'data_count': price_rng.count()
                }
            )
        return data_list

class CategoryPriceFilterCreateUpdateView(generic.View):
    """
    View to add price range database
    """
    form = PriceFilterForm
    formset = PriceFilterFormsetExtra
    template_name = 'dashboard/category_filter/price/price_filter_add.html'

    def get(self, request, *args, **kwargs):
        try:
            pr_id = kwargs.get('pk')
            price_range = Category.objects.get(id=pr_id)
            action_done = 'update'
        except Exception as e:
            print(e.args)
            price_range = None
            action_done = 'add'

        form = self.form(instance=price_range)
        formset = self.formset(instance=price_range)
        context = {
            'form': form,
            'title': 'Add Price Filter',
            'formset': formset,
            'action': action_done,
            'category': price_range
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        try:
            category_id = kwargs.get('pk')
            price_range = Category.objects.get(id=category_id)
        except Exception as e:
            print(e.args)
            price_range = None
            category_id = request.POST.get('category')

        form = self.form(request.POST, instance=price_range)
        formset = self.formset(request.POST, instance=price_range)
        category = Category.objects.get(id=category_id)

        if formset.is_valid():
            for f in formset:
                if f.cleaned_data.get('from_value') and f.cleaned_data.get('to_value'):
                    obj_exists = CategoriesWisePriceFilter.objects.filter(
                        category=category,
                        from_value=f.cleaned_data.get('from_value'),
                        to_value=f.cleaned_data.get('to_value'),
                    )
                    if obj_exists:
                        pass
                        # CategoriesWisePriceFilter.objects.filter(
                        #     category=category,
                        #     price_rng=f.cleaned_data.get('price_rng')
                        # ).update(
                        #     discount_type=f.cleaned_data.get('discount_type'),
                        #     discount=f.cleaned_data.get('discount')
                        # )
                    else:
                        range_value = str(f.cleaned_data.get('from_value'))+ '-'+str(f.cleaned_data.get('to_value'))
                        CategoriesWisePriceFilter.objects.create(
                            category=category,
                            from_value=f.cleaned_data.get('from_value'),
                            to_value=f.cleaned_data.get('to_value'),
                            range=range_value
                        )

            messages.success(request, 'Price Filter saved successfully')
            return redirect('dashboard:category-filter-price-index')
        else:
            context = {
                'form': form,
                'title': 'Add Price Filter',
                'formset': formset,
                'category': category

            }
            messages.error(request, 'Please correct errors')
            return render(request, self.template_name, context)

@csrf_exempt
def delete_price(request):
    """
    Ajax method to delete product image.FilteredProductListView
    """

    if request.is_ajax():
        price_id = request.GET.get('price_id')

        if not price_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        if not CategoriesWisePriceFilter.objects.filter(id=price_id):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        obj = CategoriesWisePriceFilter.objects.filter(id=price_id).delete()
        messages.success(request, 'Price filter deleted successfully.')
        return HttpResponse('200')

    return HttpResponse('503')


class PriceFilterDeleteView(generic.View):

    """
    View to delete price range database
    """

    template_name = 'dashboard/category_filter/price/price_filter_delete.html'

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        context = dict()

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not CategoriesWisePriceFilter.objects.filter(category__id=pk):
            return self.invalid_request('Select valid Price filter category')

        price_rng_cat = Category.objects.get(id=pk)

        context['price_rng_cat'] = price_rng_cat

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not CategoriesWisePriceFilter.objects.filter(category__id=pk):
            return self.invalid_request('Select valid Price Filter')

        CategoriesWisePriceFilter.objects.filter(category__id=pk).delete()

        messages.success(request, 'Record delete succesfully.')
        return redirect('dashboard:category-filter-price-index')

def export_price_filter(request):

    """
    View to export price range database
    :param request: default
    :return: xlsx
    """

    try:
        data = request.GET

        queryset = CategoriesWisePriceFilter.objects.all()

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(category__id__in=checked_list)

        if data.get('category'):
            category = data.get('category')
            queryset = queryset.filter(category__id=category)

        excel_data = [
            [
                'Sr. No', 'Category', 'Price Range Count'
            ]
        ]
        counter = 0
        queryset = queryset.order_by('category__id').distinct('category__id')
        for data in queryset:
            counter = counter + 1
            cnt = CategoriesWisePriceFilter.objects.filter(category=data.category).count()
            excel_data.append(
                [
                    str(counter), str(data.category.name), str(cnt)
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'price_range_db_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('dashboard:price-range-list')





