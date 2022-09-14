# Python Imports
import datetime

# Django Imports
from django.http import HttpResponse
from django.views import generic
from django.shortcuts import render, redirect, HttpResponseRedirect, reverse
from django.contrib import messages
from django.utils.html import strip_tags

# Oscar Imports
from django.views.decorators.csrf import csrf_exempt
from oscar.core.loading import get_model

# Internal Imports
from .forms import *
from .. import utils

# Import Models
CouponDistributor = get_model('offer', 'CouponDistributor')
PriceRangeModel = get_model('offer', 'PriceRangeModel')
Category = get_model('catalogue', 'Category')


class CouponDistributorView(generic.View):
    """
    View to add coupon distributors
    """
    form = CouponDistributorForms
    template_name = 'dashboard/offers/coupon_distributor_add.html'

    def get(self, request, *args, **kwargs):
        try:
            distributor_id = kwargs.get('pk')
            distributor = CouponDistributor.objects.get(id=distributor_id)
        except Exception as e:
            print(e.args)
            distributor = None

        form = self.form(instance=distributor)
        context = {
            'form': form,
            'title': 'Add Coupon Distributor'
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            distributor_id = kwargs.get('pk')
            distributor = CouponDistributor.objects.get(id=distributor_id)
        except Exception as e:
            print(e.args)
            distributor = None

        form = self.form(request.POST, instance=distributor)

        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon Distributor saved successfully')
            return redirect('dashboard:coupon-distributors')
        else:
            context = {
                'form': form,
                'title': 'Add Coupon Distributor'
            }
            messages.error(request, 'Please correct errors')
            return render(request, self.template_name, context)


class CouponDistributorList(generic.ListView):
    """
    View to list all the coupon distributors
    """
    template_name = 'dashboard/offers/coupon_distributor_list.html'
    model = CouponDistributor
    search_form = DistributorSearchForm

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        return super(CouponDistributorList, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(CouponDistributorList, self).get_context_data()
        ctx['object_list'] = self.apply_filter(ctx['object_list'].filter(is_deleted=False))
        ctx['form'] = self.search_form(data=self.request.GET)
        return ctx

    def apply_filter(self, queryset):
        if self.request.GET.get('name'):
            queryset = queryset.filter(full_name__icontains=self.request.GET.get('name'))
        if self.request.GET.get('cdn'):
            queryset = queryset.filter(cdn=self.request.GET.get('cdn'))
        if self.request.GET.get('whatsapp_number'):
            queryset = queryset.filter(whatsapp_number__contains=self.request.GET.get('whatsapp_number'))
        if self.request.GET.get('email_id'):
            queryset = queryset.filter(email_id=self.request.GET.get('email_id'))

        return queryset


class DistributorDeleteView(generic.View):

    """
    View to delete coupon distributor
    """

    template_name = 'dashboard/offers/coupon_distributor_delete.html'

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        context = dict()

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not CouponDistributor.objects.filter(id=pk,is_deleted=False):
            return self.invalid_request('Select valid distributor.')

        distributor = CouponDistributor.objects.get(id=pk)

        context['distributor'] = distributor

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not CouponDistributor.objects.filter(id=pk, is_deleted=False):
            return self.invalid_request('Select valid distributor')

        CouponDistributor.objects.filter(id=pk).update(is_deleted=True)

        messages.success(request, 'Record delete succesfully.')
        return HttpResponseRedirect(reverse('dashboard:coupon-distributors'))


def export_distributors(request):

    """
    View to export coupon distributors.
    :param request: default
    :return: xlsx
    """

    try:
        data = request.GET

        queryset = CouponDistributor.objects.filter(is_deleted= False)

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        if data.get('name'):
            full_name = data.get('name')
            queryset = queryset.filter(full_name__icontains=full_name)

        if data.get('cdn'):
            cdn = data.get('cdn')
            queryset = queryset.filter(cdn=cdn)

        if data.get('whatsapp_number'):
            whatsapp_number = data.get('whatsapp_number')
            queryset = queryset.filter(whatsapp_number__contains=whatsapp_number)

        if data.get('email_id'):
            email_id = data.get('email_id')
            queryset = queryset.filter(email_id=email_id)

        excel_data = [
            [
                'Sr. No', 'Full Name', 'CDN', 'UIN', 'Address',
                'Mobile Number', 'Whatsapp Number', 'Email ID',
                'Aadhar Number', 'PAN Number', 'Account Holder Name',
                'Bank Name', 'Bank Address', 'Account Number', 'Account Type', 'IFSC Code'
            ]
        ]

        counter = 0

        for data in queryset:
            counter = counter + 1
            excel_data.append(
                [
                    str(counter), str(data.full_name), str(data.cdn), str(data.uin), str(strip_tags(data.address)),
                    str(data.mobile_number), str(data.whatsapp_number), str(data.email_id), str(data.aadhar_number),
                    str(data.pan_number), str(data.account_holder_name), str(data.bank_name), str(strip_tags(data.bank_address)),
                    str(data.account_number), str(data.account_type), str(data.ifsc_code)
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'coupon_distributors_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('dashboard:coupon-distributors')


class PriceRangeView(generic.View):
    """
    View to add price range database
    """
    form = PriceRangeForm
    formset = PriceRangeFormsetExtra
    template_name = 'dashboard/offers/price_range_add.html'

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
            'title': 'Add Price Range',
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
                if f.cleaned_data.get('price_rng'):
                    obj_exists = PriceRangeModel.objects.filter(
                        category=category,
                        price_rng=f.cleaned_data.get('price_rng')
                    )
                    if obj_exists:
                        PriceRangeModel.objects.filter(
                            category=category,
                            price_rng=f.cleaned_data.get('price_rng')
                        ).update(
                            discount_type=f.cleaned_data.get('discount_type'),
                            discount=f.cleaned_data.get('discount')
                        )
                    else:
                        PriceRangeModel.objects.create(
                            category=category,
                            price_rng=f.cleaned_data.get('price_rng'),
                            discount_type=f.cleaned_data.get('discount_type'),
                            discount=f.cleaned_data.get('discount')
                        )

            messages.success(request, 'Price Range saved successfully')
            return redirect('dashboard:price-range-list')
        else:
            context = {
                'form': form,
                'title': 'Add Price Range',
                'formset': formset
            }
            messages.error(request, 'Please correct errors')
            return render(request, self.template_name, context)


class PriceRangeList(generic.ListView):
    """
    View to list price range database
    """
    template_name = 'dashboard/offers/price_range_list.html'
    model = PriceRangeModel
    search_form = PriceRangeSearchForm

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        return super(PriceRangeList, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(PriceRangeList, self).get_context_data()
        obj_list = ctx['object_list'].filter(is_deleted=False)
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
            price_rng = PriceRangeModel.objects.filter(category=obj.category)
            data_list.append(
                {
                    'category': obj.category,
                    'data_count': price_rng.count()
                }
            )
        return data_list


class PriceRangeDeleteView(generic.View):

    """
    View to delete price range database
    """

    template_name = 'dashboard/offers/price_range_delete.html'

    def invalid_request(self, message):

        messages.error(self.request, message)
        return redirect('/dashboard/')

    def get(self, request, *args, **kwargs):

        context = dict()

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not PriceRangeModel.objects.filter(category__id=pk, is_deleted=False):
            return self.invalid_request('Select valid Price Range Database')

        price_rng_cat = Category.objects.get(id=pk)

        context['price_rng_cat'] = price_rng_cat

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        user = request.user

        if not user.is_active or user.is_staff is False:
            return self.invalid_request('Invalid request.')

        if not PriceRangeModel.objects.filter(category__id=pk, is_deleted=False):
            return self.invalid_request('Select valid Price Range Database')

        PriceRangeModel.objects.filter(category__id=pk, is_deleted=False).update(is_deleted=True)

        messages.success(request, 'Record delete succesfully.')
        return HttpResponseRedirect(reverse('dashboard:price-range-list'))


def export_price_range_db(request):

    """
    View to export price range database
    :param request: default
    :return: xlsx
    """

    try:
        data = request.GET

        queryset = PriceRangeModel.objects.filter(is_deleted= False)

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
            cnt = PriceRangeModel.objects.filter(category=data.category, is_deleted=False).count()
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


@csrf_exempt
def delete_price_range(request):
    """
    Ajax method to delete product image.FilteredProductListView
    """

    if request.is_ajax():
        price_id = request.GET.get('price_id')

        if not price_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        if not PriceRangeModel.objects.filter(id=price_id):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        PriceRangeModel.objects.filter(id=price_id).delete()
        messages.success(request, 'Price filter deleted successfully.')
        return HttpResponse('200')

    return HttpResponse('503')
