from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from oscar.core.loading import get_class, get_model
from oscar.apps.dashboard.vouchers.views import VoucherCreateView, VoucherUpdateView, VoucherListView, VoucherDeleteView, VoucherStatsView
from oscar.apps.dashboard.vouchers.forms import VoucherForm, VoucherSetForm, VoucherSearchForm
from oscar.views import sort_queryset

from django.views import generic
from django.contrib import messages
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.utils.html import strip_tags
from ... import utils

import datetime
VoucherSearchForm = get_class('dashboard.forms', 'CustomVoucherSearchForm')
Category = get_model('catalogue', 'Category')
Voucher = get_model('voucher', 'Voucher')

ConditionalOffer = get_model('offer', 'ConditionalOffer')
Condition = get_model('offer', 'Condition')
CouponDistributor = get_model('offer', 'CouponDistributor')


from .forms import *

class CustomizeCouponListView1(VoucherListView):

    """
    Oscar extended voucher list view
    """

    form_class = CustomizeVoucherSearchForm
    template_name = 'dashboard/vouchers/customize_coupon/voucher_list.html'

    def get_queryset(self):

        """
        method to return queryset.
        :return: queryset
        """
        r_obj = Range.objects.filter(coupon_distibutor__isnull = False)
        c_obj = CustomizeCouponModel.objects.distinct('voucher').values('voucher__id')
        qs = self.model.objects.filter(id__in = c_obj ).order_by('-date_created')
        qs = sort_queryset(
            qs, self.request,
            ['num_basket_additions', 'num_orders', 'date_created'], '-date_created'
        )

        self.description_ctx = {
            'main_filter': _('All vouchers'),
            'name_filter': '',
            'code_filter': ''
        }

        # If form not submitted, return early
        is_form_submitted = 'name' in self.request.GET
        if not is_form_submitted:
            self.form = self.form_class()
            return qs.filter(voucher_set__isnull=True)

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data
        if data['name']:
            c_obj = c_obj.filter(range__coupon_distibutor__full_name__icontains=data['name'])
            qs = qs.filter(id__in = c_obj)

        if data['cdn']:
            c_obj = c_obj.filter(range__coupon_distibutor__cdn__icontains=data['cdn'])
            qs = qs.filter(id__in = c_obj)

        if data['uin']:
            c_obj = c_obj.filter(range__coupon_distibutor__uin__icontains=data['uin'])
            qs = qs.filter(id__in = c_obj)

        if data['code']:
            qs = qs.filter(code__icontains=data['code'])


        return qs


# Ajax Calls
def get_coupondist(request):
    coupondist = request.GET.get('coupon_id')
    if coupondist:
        c_obj = CouponDistributor.objects.filter(id= coupondist)
        if c_obj:
            c_obj = c_obj.last()
            context = {
                'name' : c_obj.full_name,
                'cdn' : c_obj.cdn,
                'status' : 500
            }
        else:
            context = {
                'status': 400
            }
    else:
        context = {
            'status': 400
        }
    return JsonResponse(context)

class CustomizeCouponCreateView1(generic.View):
    """
    View to add price range database
    """

    form_class = CustomizeVoucherForm
    custom_range_form = CustomizeCouponRangeForm
    formset = CustomizeCouponModelFormsetExtra
    template_name = 'dashboard/vouchers/customize_coupon/voucher_form1.html'

    def get(self, request, *args, **kwargs):
        try:
            pr_id = kwargs.get('pk')
            voucher = Voucher.objects.get(id = pr_id)
            offer = voucher.offers.all()[0]
            benefit = offer.benefit
            range = benefit.range
            cust_obj = CustomizeCouponModel.objects.filter(voucher= voucher, range = range)
            action_done = 'update'
        except Exception as e:
            print(e.args)
            voucher = None
            range = None
            cust_obj = None
            action_done = 'add'

        form = self.form_class(instance=voucher)
        form1 = self.custom_range_form(instance= range)
        formset = self.formset(instance = range)
        context = {
            'form': form,
            'form1': form1,
            'title': 'Customize Coupon',
            'formset': formset,
            'action': action_done,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            pr_id = kwargs.get('pk')
            if pr_id:
                voucher = Voucher.objects.get(id=pr_id)
            elif self.request.POST['code']:
                voucher = Voucher.objects.get(code=self.request.POST['code'])
            offer = voucher.offers.all()[0]
            benefit = offer.benefit
            range = benefit.range
            cust_obj = CustomizeCouponModel.objects.filter(voucher=voucher, range=range)
        except Exception as e:
            print(e.args)
            voucher = None
            range = None
            cust_obj = None

        import datetime
        context = {}
        custom_form = self.custom_range_form(self.request.POST,instance= range)
        form = self.form_class(self.request.POST, instance= voucher)
        formset = self.formset(self.request.POST, queryset = cust_obj)

        date_list = []
        if formset.is_valid():
            for f in formset:
                if f.is_valid() and f.cleaned_data.get('category',False):
                    date_list.append(f.cleaned_data['start_datetime'])
                    date_list.append(f.cleaned_data['end_datetime'])

        if date_list:
            max_date = max(*date_list)
            min_date = min(*date_list)

        if date_list and form.is_valid() and formset.is_valid():
            try:
                form.start_datetime = min_date
                form.end_datetime = max_date
                coupon_distibutor = self.request.POST['coupon_distibutor']
                coupon_obj = CouponDistributor.objects.filter(id = coupon_distibutor)
                coupon_obj = coupon_obj.last()
                name = 'customize_%s' % (coupon_obj.uin)
                vobj_exists = Voucher.objects.filter(name=name)
                cat_list = []
                context = {}
                if voucher or (Range.objects.filter(coupon_distibutor = coupon_obj) and vobj_exists):

                    if voucher:
                        voucher.name = name
                        voucher.code = form.cleaned_data['code']
                        voucher.usage = form.cleaned_data['usage']
                        voucher.start_datetime = min_date
                        voucher.end_datetime = max_date
                        voucher.save()
                        benefit = voucher.benefit
                        benefit.range.description = self.request.POST['description']
                        benefit.range.name = voucher.name
                        benefit.range.coupon_distibutor= coupon_obj
                        benefit.range.save()
                        benefit.type = 'Customizeprice'
                        benefit.value = 100
                        benefit.save()

                    elif Range.objects.filter(coupon_distibutor = coupon_obj) and vobj_exists:
                        Range.objects.filter(coupon_distibutor=coupon_obj).update(
                            name='range_%s' % (coupon_obj.uin),
                            is_public=True,
                            includes_all_products=True,
                            description=self.request.POST['description'],
                            coupon_distibutor=coupon_obj
                        )

                        voucher = Voucher.objects.filter(name=name)
                        voucher = voucher.last()
                        voucher.name = name
                        voucher.code = form.cleaned_data['code']
                        voucher.usage = form.cleaned_data['usage']
                        voucher.start_datetime = min_date
                        voucher.end_datetime = max_date
                        voucher.save()
                        benefit = voucher.benefit
                        print('error', formset.errors, )


                    if formset.is_valid():
                        for f in formset:
                            if f.is_valid() and f.cleaned_data.get('category',False):
                                cust_obj = CustomizeCouponModel.objects.filter(
                                    category=f.cleaned_data['category'],
                                    voucher=voucher,
                                    range=benefit.range,
                                )
                                start_datetime = f.cleaned_data['start_datetime']
                                end_datetime = f.cleaned_data['end_datetime']
                                if cust_obj:
                                    cust_obj = CustomizeCouponModel.objects.filter(
                                        category=f.cleaned_data['category'],
                                        voucher=voucher,
                                        range=benefit.range,
                                    ).update(
                                        start_datetime=start_datetime,
                                        end_datetime=end_datetime,
                                        coupon_count = f.cleaned_data['coupon_count'],
                                    )
                                else:
                                    CustomizeCouponModel.objects.create(
                                    category=f.cleaned_data['category'],
                                    start_datetime=start_datetime,
                                    end_datetime=end_datetime,
                                    voucher=voucher,
                                    range=benefit.range,
                                    coupon_count = f.cleaned_data['coupon_count'],
                                )
                                cat_list.append(f.cleaned_data['category'])
                        if cat_list:
                            benefit.range.included_categories.set(cat_list)
                            benefit.range.save()
                    else:
                        context = {
                            'form': form,
                            'form1': custom_form,
                            'title': 'Customize Coupon',
                            'formset': formset
                        }
                        messages.error(request, 'Please correct errors')
                        return render(request, self.template_name, context)


                else:
                    a = Range.objects.create(
                        name = 'range_%s'%(coupon_obj.uin),
                        is_public = True,
                        includes_all_products = True,
                        description = self.request.POST['description'],
                        coupon_distibutor = coupon_obj
                    )

                    condition = Condition.objects.create(
                        range=a,
                        type=Condition.COUNT,
                        value=1
                    )
                    benefit = Benefit.objects.create(
                        range=a,
                        type='Customizeprice',
                        value=100
                    )
                    name = 'customize_%s'%(coupon_obj.uin)
                    offer = ConditionalOffer.objects.create(
                        name=_("Offer for voucher '%s'") % name,
                        offer_type=ConditionalOffer.VOUCHER,
                        benefit=benefit,
                        condition=condition,
                        exclusive=False,
                    )
                    voucher = Voucher.objects.create(
                        name=name,
                        code=form.cleaned_data['code'],
                        usage=form.cleaned_data['usage'],
                        start_datetime=min_date,
                        end_datetime=max_date,
                    )
                    cat_list = []
                    if formset.is_valid():
                        for f in formset:

                            if f.is_valid() and f.cleaned_data.get('category',False):
                                cust_obj = CustomizeCouponModel.objects.filter(
                                    category=f.cleaned_data['category'],
                                    voucher=voucher,
                                    range=benefit.range,
                                )
                                start_datetime = f.cleaned_data['start_datetime']
                                end_datetime = f.cleaned_data['end_datetime']
                                if cust_obj:
                                    CustomizeCouponModel.objects.filter(
                                        category=f.cleaned_data['category'],
                                        voucher=voucher,
                                        range=benefit.range,
                                    ).update(
                                        start_datetime=start_datetime,
                                        end_datetime=end_datetime,
                                        coupon_count = f.cleaned_data['coupon_count'],
                                    )
                                else:

                                    CustomizeCouponModel.objects.create(
                                        category=f.cleaned_data['category'],
                                        start_datetime=start_datetime,
                                        end_datetime=end_datetime,
                                        voucher=voucher,
                                        range=a,
                                        coupon_count = f.cleaned_data['coupon_count'],
                                    )
                                cat_list.append(f.cleaned_data['category'])
                        if cat_list:
                            a.included_categories.add(*cat_list)
                            a.save()
                        voucher.offers.add(offer)
                    else:
                        context = {
                            'form': form,
                            'form1': custom_form,
                            'title': 'Customize Coupon',
                            'formset': formset
                        }
                        messages.error(request, 'Please correct errors')
                        return render(request, self.template_name, context)

                messages.success(request, 'Custom coupon saved successfully')
                return redirect('dashboard:customize-voucher-list1')
            except Exception as e:
                context = {
                    'form': form,
                    'form1': custom_form,
                    'title': 'Customize Coupon',
                    'formset': formset
                }
                import os
                import sys
                print('-----------in exception----------')
                print(e.args)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)



        else:
            context = {
                'form': form,
                'form1': custom_form,
                'title': 'Customize Coupon',
                'formset': formset
            }
            if not date_list:
                messages.error(request,'Please add atleast on category.')

        messages.error(request, 'Please correct errors')
        return render(request, self.template_name, context)


def export_customcoupon_data(request):

    """
    Method to export coupon
    :param request: default
    :return: xlsx
    """

    try:

        data = request.GET
        c_obj = CustomizeCouponModel.objects.distinct('voucher').values('voucher__id')
        qs = Voucher.objects.filter(id__in=c_obj).order_by('-date_created')
        if data.get('checked_id'):

            checked_list = data.get('checked_id').split(',')
            qs = qs.filter(id__in=checked_list)

        if data.get('name'):
            c_obj = c_obj.filter(range__coupon_distibutor__full_name__icontains=data.get('name'))
            qs = qs.filter(id__in=c_obj)

        if data.get('cdn'):
            c_obj = c_obj.filter(range__coupon_distibutor__cdn__icontains=data.get('cdn'))
            qs = qs.filter(id__in=c_obj)

        if data.get('uin'):
            c_obj = c_obj.filter(range__coupon_distibutor__uin__icontains=data.get('uin'))
            qs = qs.filter(id__in=c_obj)

        if data.get('code'):
            qs = qs.filter(code__icontains=data.get('code'))

        excel_data = [
            [
                'Sr. No', 'CDN','UIN','Name', 'Code', 'Total Coupon Count', 'Categories', 'Category wise Live Coupon Count', 'Category wise Used Coupon Count', 'Date created'
            ]
        ]
        counter = 0
        is_active = '-'

        for voucher in qs:
            counter = counter + 1
            cat_names = ''
            if voucher.benefit.range.included_categories.all().count() > 0:
                cat_names = voucher.benefit.range.get_cat


            excel_data.append(
                [
                    str(counter),str(voucher.benefit.range.coupon_distibutor.cdn), str(voucher.benefit.range.coupon_distibutor.uin), str(voucher.benefit.range.coupon_distibutor.full_name), str(voucher.code), str(voucher.benefit.range.get_total_coupon_count),
                    str(cat_names), str(is_active),str(is_active),
                    str(voucher.date_created.date())
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'coupon_%s' % (str(datetime.datetime.now())),
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
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


class CustomizeVoucherDeleteView(VoucherDeleteView):
    """
    Oscar extended voucher delete view.
    """

    def get_success_url(self):
        messages.warning(self.request, _("Customize Coupon deleted"))
        return reverse('dashboard:customize-voucher-list1')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        c_obj = CustomizeCouponModel.objects.filter(voucher=self.object).values_list('range__id', flat=True)
        r_obj = Range.objects.filter(id__in=c_obj).values_list('id', flat=True)
        r_obj1 = Range.objects.filter(id__in=c_obj)
        Range.objects.filter(id__in=r_obj1).delete()
        Benefit.objects.filter(range__id__in=r_obj).delete()
        CustomizeCouponModel.objects.filter(voucher=self.object).delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)

class CustomizeVoucherStatsView(VoucherStatsView):
    template_name = 'dashboard/vouchers/customize_coupon/voucher_detail.html'


@csrf_exempt
def delete_customize_category(request):
    """
    Ajax method to delete product image.FilteredProductListView
    """

    if request.is_ajax():
        price_id = request.GET.get('price_id')

        if not price_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        if not CustomizeCouponModel.objects.filter(id=price_id):
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')

        CustomizeCouponModel.objects.filter(id=price_id).delete()
        messages.success(request, 'Price filter deleted successfully.')
        return HttpResponse('200')

    return HttpResponse('503')


@csrf_exempt
def get_coupondetails(request):
    """
    Ajax method to delete product image.FilteredProductListView
    """
    print('code',request.GET.get('coupon_id'))
    if request.is_ajax():
        coupon_id = request.GET.get('coupon_id')
        voucher_list = {}
        if not coupon_id:
            print('here')
            messages.error(request, 'Something went wrong....')
            return HttpResponse('503')

        if not Voucher.objects.filter(code=coupon_id):
            print('there')
            messages.error(request, 'Something went wrong.')
            return HttpResponse('503')
        voucher = Voucher.objects.filter(code=coupon_id)
        if not voucher.last().is_active():
            messages.error(request, 'Coupon is not active')
            pass
        voucher = voucher.last()
        voucher_code = voucher.code
        offer = voucher.offers.last().benefit
        offer_details = ''
        description = ''
        offer_mesaage = ''
        category_list = []

        if offer.range:
            # offer_details = offer.description
            category_list = offer.range.included_categories.values_list('name', flat=True)
            description = offer.range.description

            if offer.range.coupon_distibutor:
                p_obj = PriceRangeModel.objects.filter(category__in=offer.range.included_categories.all())
                if p_obj:
                    if p_obj.last().discount_type == 'Percentage':
                        offer_mesaage = 'You will save upto ' + str(p_obj.last().discount) + '% with this code'
                        offer_details = 'Upto ' + str(p_obj.last().discount) + '% discount'

                    if p_obj.last().discount_type == 'Absolute':
                        offer_mesaage = 'You will save upto ₹' + str(p_obj.last().discount) + " with this code"
                        offer_details = 'Upto ₹' + str(p_obj.last().discount) + ' discount'
                # offer_mesaage = 'You will save upto ₹5000(Highest discounted amount of allotted categories for the concerned coupon code) with this code'
            else:
                if offer.type == 'Percentage':
                    offer_mesaage = 'You will save ' + str(offer.value) + '% with this code'
                    offer_details = str(offer.value) + '% discount'
                if offer.type == 'Absolute':
                    offer_mesaage = 'You will save ₹' + str(offer.value) + " with this code"
                    offer_details = '₹' + str(offer.value) + ' discount'

        voucher_list = {
                'code': voucher_code,
                'start_date': voucher.start_datetime.date(),
                'end_date': voucher.end_datetime.date(),
                'offer_details': offer_details,
                # 'categories': category_list,
                'description': description,
                'offer_mesaage': offer_mesaage,
                'status': 500
            }

        print('context', voucher_list)
    return JsonResponse(voucher_list)

