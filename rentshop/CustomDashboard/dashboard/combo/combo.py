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


class CreateComboV1(generic.View):

    """
    To create combo offer.
    """

    template = 'dashboard/combo/v1/form_v1.html'
    form_class = ComboProductsMasterV1ModelForm
    formset = ComboFormsetExtra

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

        context['combo_form'] = form
        context['combo_form_set'] = self.formset(form_kwargs={'product_user': request.user})

        return render(self.request, self.template, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)
        formset = self.formset(request.POST, form_kwargs={'product_user': request.user})

        user = request.user
        vendor = Partner.objects.filter(users=user)

        is_vendor = False
        if user.is_staff and not user.is_superuser and vendor:
            is_vendor = True

        if not formset.is_valid() or not form.is_valid():
            return self.is_invalid(form, formset)

        formset_product_id = []
        formset_product = []

        if formset.is_valid():

            # validate vendor products
            for fx in formset:
                if fx.cleaned_data.get('combo_product'):
                    formset_product_id.append(fx.cleaned_data.get('combo_product').id)
                    formset_product.append(fx.cleaned_data.get('combo_product'))

        if len(formset_product) == 0:
            return self.is_invalid(form, formset)

        if len(formset_product_id) != len(set(formset_product_id)):
            return self.is_invalid(form, formset)

        if is_vendor:
            vendor_stock = StockRecord.objects.filter(partner=vendor.last(), product__in=formset_product)
            if len(formset_product) != vendor_stock.count():
                messages.error(request, 'Something went wrong. Please select authorized products.')
                return redirect('/dashboard/')

        # save.
        title = form.cleaned_data.get('title')
        upc = form.cleaned_data.get('upc')
        description = form.cleaned_data.get('description')
        combo_price = form.cleaned_data.get('combo_price')
        is_active = form.cleaned_data.get('is_active')

        # create combo product
        combo_data = {
            'title': title, 'upc': upc, 'description': description,
            'combo_price': combo_price, 'is_active': is_active
        }

        combo_obj = ComboProductsMaster.objects.create(**combo_data)

        for product in formset_product:
            ComboProductsMasterProducts.objects.create(
                combo_offer=combo_obj, combo_product=product
            )

        messages.success(request, 'Combo offer successfully.')
        return redirect(reverse('dashboard:combo-index'))

    def is_invalid(self, form, formset):

        messages.error(self.request, 'Please correct below errors.')

        context = dict()
        context['combo_form'] = form
        context['combo_form_set'] = formset

        return render(self.request, self.template, context=context)


class UpdateComboV1(generic.View):

    """
    To create combo offer.
    """

    template = 'dashboard/combo/v1/form_v1.html'
    form_class = ComboProductsMasterV1ModelForm
    formset = ComboFormsetExtra

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

        if not pk or not ComboProductsMaster.objects.filter(id=pk):
            return self.invalid_request()

        combo_obj = ComboProductsMaster.objects.get(id=pk)

        context = dict()
        form = self.form_class(instance=combo_obj)

        context['combo_form'] = form
        context['type'] = 'update'
        context['combo_form_set'] = self.formset(
            instance=combo_obj,
            form_kwargs={'product_user': request.user},
        )

        return render(self.request, self.template, context=context)

    def post(self, request, *args, **kwargs):

        user = request.user
        pk = kwargs.get('pk')
        combo_obj = ComboProductsMaster.objects.get(id=pk)

        form = self.form_class(data=request.POST, instance=combo_obj)
        formset = self.formset(request.POST, form_kwargs={'product_user': request.user})

        user = request.user
        vendor = Partner.objects.filter(users=user)

        is_vendor = False
        if user.is_staff and not user.is_superuser and vendor:
            is_vendor = True

        if not formset.is_valid() or not form.is_valid():
            return self.is_invalid(form, formset)

        formset_product_id = []
        formset_product = []
        if formset.is_valid():

            # validate vendor products
            for fx in formset:
                if fx.cleaned_data.get('combo_product'):
                    formset_product_id.append(fx.cleaned_data.get('combo_product').id)
                    formset_product.append(fx.cleaned_data.get('combo_product'))

        if len(formset_product) == 0:
            return self.is_invalid(form, formset)

        if len(formset_product_id) != len(set(formset_product_id)):
            return self.is_invalid(form, formset)

        if is_vendor:
            vendor_stock = StockRecord.objects.filter(partner=vendor.last(), product__in=formset_product)
            if len(formset_product) != vendor_stock.count():
                messages.error(request, 'Something went wrong. Please select authorized products.')
                return redirect('/dashboard/')

        # create combo product
        base_form = form.save(commit=True)
        base_form.save()

        for products in formset_product:
            ComboProductsMasterProducts.objects.get_or_create(
                combo_offer=base_form, combo_product=products
            )

        messages.success(request, 'Combo offer successfully.')
        return redirect(reverse('dashboard:combo-index'))

    def is_invalid(self, form, formset):

        messages.error(self.request, 'Please correct below errors.')

        context = dict()
        context['combo_form'] = form
        context['type'] = 'update'
        context['combo_form_set'] = formset

        return render(self.request, self.template, context=context)


class ComboOfferIndexView(generic.ListView):

    """
    Combo offer index page view.
    """

    template_name = 'dashboard/combo/v1/index.html'
    model = ComboProductsMaster
    context_object_name = 'combo_offer'
    paginate_by = 20
    form_class = ComboSearchForm

    def get(self, request, *args, **kwargs):

        if request.user.is_active and request.user.is_superuser:
            return super(ComboOfferIndexView, self).get(request, *args, **kwargs)

        messages.error(request, 'Invalid request')
        return redirect('/dashboard')

    def get_queryset(self):

        try:

            if not self.request.user.is_staff or not self.request.user.is_active:
                messages.error(self.request, 'Something went wrong.')
                return redirect('/dashboard')

            queryset = self.model.objects.all()

            if self.request.user.is_staff and not self.request.user.is_superuser:
                partner = Partner.objects.get(users=self.request.user)
                stock = StockRecord.objects.filter(partner=partner).values_list('product', flat=True)
                queryset = queryset.filter(product__in=stock)

            data = self.request.GET

            if data.get('upc'):
                queryset = queryset.filter(upc__icontains=data.get('upc'))

            if data.get('product_title'):
                queryset = queryset.filter(product__title__icontains=data.get('product_title'))

            if data.get('offer_title'):
                queryset = queryset.filter(title__icontains=data.get('offer_title'))

            if data.get('vendor_name'):
                partner = Partner.objects.filter(name__icontains=data.get('vendor_name'))
                stock_record = StockRecord.objects.filter(partner__id__in=partner.values_list('id', flat=True))
                queryset = queryset.filter(id__in=stock_record.values_list('product', flat=True))

            return queryset

        except Exception as e:

            return []

    def get_context_data(self, **kwargs):

        ctx = super(ComboOfferIndexView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class(self.request.GET)

        return ctx


class DeleteCombo(generic.View):

    """
    method to delete
    """

    template_name = 'dashboard/combo/combo_product_delete.html'

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
        context['combo'] = ComboProductsMaster.objects.get(id=pk)

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:
            pk = kwargs.get('pk')

            comb_title = ''
            comb = ComboProductsMaster.objects.get(id=pk)
            comb_title = comb.title

            comb.delete()

            messages.success(self.request, '%s delete successfully' % (comb_title))

        except:

            messages.error(self.request, 'Something went wrong.')

        return redirect(reverse('dashboard:combo-index'))


def export_combo(request):

    """

    :param request:
    :return:
    """

    try:

        data = request.GET

        queryset = ComboProductsMaster.objects.all()

        if request.user.is_staff and not request.user.is_superuser:
            partner = Partner.objects.get(users=request.user)
            stock = StockRecord.objects.filter(partner=partner).values_list('product', flat=True)
            queryset = queryset.filter(product__in=stock)

        if data.get('product_title'):
            queryset = queryset.filter(product__title__icontains=data.get('product_title'))

        if data.get('offer_title'):
            queryset = queryset.filter(title__icontains=data.get('offer_title'))

        if data.get('upc'):
            queryset = queryset.filter(upc__icontains=data.get('upc'))

        if data.get('checked_id'):
            checked_list = data.get('checked_id').split(',')
            queryset = queryset.filter(id__in=checked_list)

        excel_data = [
            [
                'Sr. No', 'Offer Title', 'UPC', 'Offer Price',
                'No. Of Products', 'Active',
                'Date Created', 'Products'
            ]
        ]

        counter = 0

        for obj in queryset:

            list_pr = list(obj.combo_offers.all().values_list('combo_product__title', flat=True))
            list_pr = ','.join(list_pr)
            counter = counter + 1

            excel_data.append(
                [
                    str(counter), str(obj.title),
                    str(obj.upc),
                    str(obj.combo_offers.all().count()),
                    str(obj.combo_price),
                    str(obj.is_active),
                    str(obj.date_created.date()),
                    list_pr
                ]
            )

        prms = {
            'type': 'excel',
            'filename': 'combo_product_%s' % (str(datetime.datetime.now())),
            'excel_data': excel_data
        }

        return utils.generate_excel(request, **prms)

    except Exception as e:
        print(e.args)
        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')


@csrf_exempt
def delete_bulk_combo_data(request):

    """
    Ajax method to delete bulk combo.
    :param request: ajax data
    :return: ajax response
    """

    if request.is_ajax():

        combo_id = request.GET.get('combo_id')

        if not combo_id:
            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')

        combo_list = combo_id.split(',')

        ComboProductsMaster.objects.filter(id__in=combo_list).delete()

        _pr_str = 'combo'
        if len(combo_list) > 1:
            _pr_str = 'combos'

        success_str = 'Total %s %s deleted successfully.' % (len(combo_list), _pr_str)

        messages.success(request, success_str)
        return HttpResponse('TRUE')

    messages.error(request, 'Something went wrong.')
    return HttpResponse('IN_SERVER')


class CreateCombo(generic.View):

    template = 'dashboard/combo/v1/form.html'
    form_class = ComboProductsMasterModelForm

    def invalid_request(self):

        messages.error(self.request, 'Invalid request')
        return redirect('/dashboard')

    def get(self, request, *args, **kwargs):

        context = dict()
        user = request.user

        if not user.is_staff:
            return self.invalid_request()

        if not kwargs.get('pk'):
            return self.invalid_request()

        if not Product.objects.filter(id=kwargs.get('pk'),is_deleted=False):
            return self.invalid_request()

        product = Product.objects.filter(id=kwargs.get('pk'),is_deleted=False).last()

        instance = None

        if ComboProductsMaster.objects.filter(product=product):
            instance = ComboProductsMaster.objects.filter(product=product).last()

        context['combo_form'] = self.form_class(
            self_product=product.id, product_user=request.user, instance=instance
        )
        context['product'] = product
        context['instance'] = instance

        return render(request, self.template, context=context)

    def post(self, request, *args, **kwargs):

        product = Product.objects.filter(id=kwargs.get('pk'),is_deleted=False).last()

        instance = None

        if ComboProductsMaster.objects.filter(product=product):
            instance = ComboProductsMaster.objects.filter(product=product).last()

        combo_form = self.form_class(
            request.POST, self_product=product.id, product_user=request.user,
            instance=instance
        )

        if combo_form.is_valid():
            return self.is_valid(combo_form)
        else:
            return self.is_invalid(combo_form)

    def is_valid(self, combo_form):

        base_form = combo_form.save(commit=False)
        base_form.save()
        combo_form.save_m2m()

        if self.request.POST.get('action') == 'continue':
            messages.success(self.request, 'Combo data saved successfully. Continue editing.')
            return redirect(reverse('dashboard:create-combo', kwargs={'pk': self.kwargs.get('pk')}))

        messages.success(self.request, 'Combo data saved successfully.')
        return redirect('/dashboard')

    def is_invalid(self, combo_form):

        context = dict()
        context['combo_form'] = combo_form
        context['product'] = Product.objects.filter(id=self.kwargs.get('pk'),is_deleted=False).last()

        instance = None
        product = Product.objects.filter(id=self.kwargs.get('pk'),is_deleted=False).last()

        if ComboProductsMaster.objects.filter(product=product):
            instance = ComboProductsMaster.objects.filter(product=product).last()

        context['instance'] = instance

        return render(self.request, self.template, context=context)
