# django imports
from django import http
from django import shortcuts
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import is_safe_url
from django.utils.translation import gettext_lazy as _
from django.urls import resolve
from django.contrib.sites.models import Site

# 3rd party imports
from oscar.apps.basket.views import BasketView, BasketAddView
from oscar.apps.basket.signals import (basket_addition, voucher_addition, voucher_removal)
from oscar.core import ajax
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.utils import redirect_to_referrer, safe_referrer
from oscar.apps.basket.views import VoucherAddView
from oscar.core.compat import get_user_model

# internal imports
Applicator = get_class('offer.applicator', 'Applicator')
(BasketLineForm, AddToBasketForm, BasketVoucherForm, SavedLineForm) = get_classes('basket.forms', ('BasketLineForm', 'AddToBasketForm', 'BasketVoucherForm', 'SavedLineForm'))
BasketLineFormSet, SavedLineFormSet = get_classes('basket.formsets', ('BasketLineFormSet', 'SavedLineFormSet'))
Repository = get_class('shipping.repository', 'Repository')

OrderTotalCalculator = get_class('checkout.calculators', 'OrderTotalCalculator')
BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')
get_product_blocked_date = get_class('catalogue.bind', 'get_product_blocked_date')
WishList = get_model('wishlists', 'WishList')
AbandonedCartLogs = get_model('RentCore', 'AbandonedCartLogs')
trigger_email = get_class('RentCore.tasks', 'trigger_email')
send_sms = get_class('RentCore.email', 'send_sms')
Basket = get_model('basket', 'Basket')
Basket_Line = get_model('basket', 'Line')
PriceRangeModel = get_model('offer', 'PriceRangeModel')
CouponDistributor = get_model('offer', 'CouponDistributor')
Voucher = get_model('voucher', 'Voucher')
User = get_user_model()

class CustomBasketAddView(BasketAddView):

    """
    Handles the add-to-basket submissions view.
    """

    form_class = AddToBasketForm
    product_model = get_model('catalogue', 'product')
    add_signal = basket_addition
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        """
        Post method to add product to cart.
        :param request: default
        :param args: default
        :param kwargs: default
        :return: instance
        """
        self.product = shortcuts.get_object_or_404(self.product_model, pk=kwargs['pk'])
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):

        """
        Method to fetch url parms.
        :return: keywords parms.
        """

        kwargs = super().get_form_kwargs()
        kwargs['basket'] = self.request.basket
        kwargs['product'] = self.product

        return kwargs

    def form_invalid(self, form):

        """
        Handel form invalid.
        :param form: form instance
        :return: invalid form
        """

        msgs = []
        for error in form.errors.values():
            msgs.append(error.as_text())
        clean_msgs = [m.replace('* ', '') for m in msgs if m.startswith('* ')]

        messages.error(self.request, ",".join(clean_msgs), extra_tags='basket_error')
        print('error')
        return redirect('/catalogue/'+str(self.product.slug)+'_'+str(self.product.id))

    def form_valid(self, form):

        """
        Handel form valid.
        :param form: form instance
        :return: data
        """
        print('in valid')
        product_list = []
        if form.product.is_package and form.product.product_package.all().count() > 0:
            line_obj = Basket_Line.objects.filter(basket=self.request.basket, product__in=form.product.product_package.all())
            if line_obj:
                product_list = line_obj.values_list('product')

        offers_before = self.request.basket.applied_offers()
        print(form.cleaned_data)
        if form.cleaned_data.get('order_type'):
            order_type = form.cleaned_data['order_type']
        else:
            order_type = form.cleaned_data['add_to_cart']
        self.request.basket.add_product(
            form.product, form.cleaned_data['quantity'],
            order_type,
            form.cleaned_data['booking_start_date'],
            form.cleaned_data['booking_end_date'],
            form.cleaned_data.get('product_attributes'),
            form.cleaned_options(),
            form.cleaned_data['flower_type']
        )

        # messages.success(self.request, self.get_success_message(form))

        # Check for additional offer messages
        # BasketMessageGenerator().apply_messages(self.request, offers_before)

        # Send signal for basket addition
        if product_list:
            success_msg = "%s Product Package has been added to your basket. Also removed product under that which you already added" % (form.product.get_title())
        else:
            success_msg = "%s Product has been added to your basket."% (form.product.get_title())
        messages.success(
            self.request, success_msg)

        self.add_signal.send(sender=self, product=form.product, user=self.request.user, request=self.request)
        if self.request.POST.get("order_type"):
            return redirect('basket:summary')
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_message(self, form):

        """
        return success message
        :param form: form instance
        :return: message
        """

        return render_to_string(
            'basket/messages/addition.html',
            {
                'product': form.product,
                'quantity': form.cleaned_data['quantity']
            }
        )

    def get_success_url(self):

        """
        return success url
        :return: url
        """

        post_url = self.request.POST.get('next')
        referrer = self.request.META.get('HTTP_REFERER')

        # post_url = None
        if post_url and is_safe_url(post_url, self.request.get_host()):
            return safe_referrer(self.request, 'basket:summary')
        return referrer


class CustomBasketView(BasketView):

    """
    Basket view method.
    """

    model = get_model('basket', 'Line')
    basket_model = get_model('basket', 'Basket')
    formset_class = BasketLineFormSet
    form_class = BasketLineForm
    factory_kwargs = {
        'extra': 0,
        'can_delete': True
    }
    # template_name = 'basket/basket.html'
    template_name = 'new_design/basket/basket.html'

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs['strategy'] = self.request.strategy
        return kwargs

    def get_queryset(self, * kwargs):
        return self.request.basket.all_lines()

    def get_shipping_methods(self, basket):
        return Repository().get_shipping_methods(
            basket=self.request.basket,
            user=self.request.user,
            request=self.request
        )

    def get_default_shipping_address(self):
        if self.request.user.is_authenticated:
            return self.request.user.addresses.filter(is_default_for_shipping=True).first()

    def get_default_shipping_method(self, basket):
        return Repository().get_default_shipping_method(
            basket=self.request.basket, user=self.request.user,
            request=self.request, shipping_addr=self.get_default_shipping_address()
        )

    def get_basket_warnings(self, basket):

        warnings = []
        for line in basket.all_lines():
            warning = line.get_warning()
            if warning:
                warnings.append(warning)
        return warnings

    def get_upsell_messages(self, basket):
        offers = Applicator().get_offers(basket, self.request.user, self.request)
        applied_offers = list(basket.offer_applications.offers.values())
        msgs = []
        for offer in offers:
            if offer.is_condition_partially_satisfied(basket) \
                    and offer not in applied_offers:
                data = {
                    'message': offer.get_upsell_message(basket),
                    'offer': offer
                }
                msgs.append(data)
        return msgs

    def get_basket_voucher_form(self):
        return BasketVoucherForm()

    def get_order_obj(self):

        event_obj = None
        result = []

        data = self.request.basket.all_lines().values_list('order_type', flat=True)

        for i in data:
            if i == 'Professional':
                event_obj = 'Professional'

        order_obj_list = list(data)
        seen = set()

        for i in order_obj_list:
            if i not in seen:
                seen.add(i)
                result.append(i)

        data_dict = {'data':result,'event_obj':event_obj}

        return data_dict

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['voucher_form'] = self.get_basket_voucher_form()
        context['data_dict'] = self.get_order_obj()

        # Shipping information is included to give an idea of the total order
        # cost.  It is also important for PayPal Express where the customer
        # gets redirected away from the basket page and needs to see what the
        # estimated order total is beforehand.
        context['shipping_methods'] = self.get_shipping_methods(self.request.basket)
        method = self.get_default_shipping_method(self.request.basket)
        context['shipping_method'] = method
        shipping_charge = method.calculate(self.request.basket)
        context['shipping_charge'] = shipping_charge
        if method.is_discounted:
            excl_discount = method.calculate_excl_discount(self.request.basket)
            context['shipping_charge_excl_discount'] = excl_discount

        context['order_total'] = OrderTotalCalculator().calculate(self.request.basket, shipping_charge)
        context['basket_warnings'] = self.get_basket_warnings(self.request.basket)
        context['upsell_messages'] = self.get_upsell_messages(self.request.basket)
        vouchers = Voucher.objects.all()
        context['voucher_list'] = self.get_active_voucher_details(vouchers)

        if self.request.user.is_authenticated:
            try:
                saved_basket = self.basket_model.saved.get(owner=self.request.user)
            except self.basket_model.DoesNotExist:
                pass
            else:
                saved_basket.strategy = self.request.basket.strategy
                if not saved_basket.is_empty:
                    saved_queryset = saved_basket.all_lines()
                    formset = SavedLineFormSet(strategy=self.request.strategy,
                                               basket=self.request.basket,
                                               queryset=saved_queryset,
                                               prefix='saved'
                                               )
                    context['saved_formset'] = formset
        return context

    def get_success_url(self):
        return safe_referrer(self.request, 'basket:summary')

    def get_active_voucher_details(self, queryset):
        voucher_list = []
        for voucher in queryset:
            if not voucher.is_active():
                continue

            voucher_code = voucher.code
            offer = voucher.offers.last().benefit
            offer_details = ''
            description = ''
            offer_mesaage = ''
            category_list = []

            if offer.range and not offer.range.coupon_distibutor:
                # offer_details = offer
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
                else:
                    if offer.type == 'Percentage':
                        offer_mesaage = 'You will save ' + str(offer.value) + '% with this code'
                        offer_details = str(offer.value) + '% discount'
                    if offer.type == 'Absolute':
                        offer_mesaage = 'You will save ₹' + str(offer.value) + " with this code"
                        offer_details = '₹' + str(offer.value) + ' discount'


                voucher_list.append(
                    {
                        'title': voucher.name,
                        'code': voucher_code,
                        'start_date': voucher.start_datetime.date(),
                        'end_date': voucher.end_datetime.date(),
                        'offer_details': offer_details,
                        'categories': category_list,
                        'description': description,
                        'offer_mesaage' : offer_mesaage
                    }
                )

            print("**************")
        print('get_active_voucher_details', type(voucher_list))

        return voucher_list

    def formset_valid(self, formset):
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$form")
        # Store offers before any changes are made so we can inform the user of
        # any changes
        offers_before = self.request.basket.applied_offers()
        save_for_later = False

        # Keep a list of messages - we don't immediately call
        # django.contrib.messages as we may be returning an AJAX response in
        # which case we pass the messages back in a JSON payload.
        flash_messages = ajax.FlashMessages()

        form_list = []
        for form in formset:
            if form.cleaned_data['DELETE']:
                line_obj = Basket_Line.objects.filter(id=form.cleaned_data['line_id'])
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
                print(offers_before.keys())
                print(self.request.basket.vouchers.all().values('id'))

                from django.core.exceptions import ObjectDoesNotExist
                for coupon in offers_before.keys():

                    try:
                        voucher = self.request.basket.vouchers.get(id=coupon)
                        if voucher.benefit.range.included_categories.all().count() > 0:
                            if self.request.basket.all_lines().count() > 0:
                                all_line = self.request.basket.all_lines()
                                status = False
                                for l1 in all_line:
                                    cat_list = []
                                    for category in voucher.benefit.range.included_categories.all():
                                        id_list = [obj for obj in category.get_descendants_and_self()]
                                        for element in id_list:
                                            cat_list.append(element)
                                    if not l1.is_package_product and not l1 == line_obj.last() and l1.product.categories.all().last() in cat_list:
                                        status = True
                                        break
                                if not status:
                                    self.request.basket.vouchers.remove(voucher)
                                    remove_signal = voucher_removal
                                    remove_signal.send(
                                        sender=self, basket=self.request.basket, voucher=voucher)
                                    messages.info(
                                        self.request, _("Voucher '%s' removed from basket") % voucher.code)

                            else:

                                self.request.basket.vouchers.remove(voucher)
                                remove_signal = voucher_removal
                                remove_signal.send(
                                    sender=self, basket=self.request.basket, voucher=voucher)
                                messages.info(
                                    self.request, _("Voucher '%s' removed from basket") % voucher.code)


                    except ObjectDoesNotExist:
                        messages.error(
                            self.request, _("No voucher found with id '%s'") % coupon)

                print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
                if line_obj and line_obj.last().product.is_package:
                    form_list.extend(line_obj.last().product.product_package.all().values_list('id', flat= True))

        for form in formset:
            if int(form.cleaned_data['prod_id']) in form_list:
                form.instance.delete()
            if (hasattr(form, 'cleaned_data') and
                    form.cleaned_data['save_for_later']):
                line = form.instance
                if self.request.user.is_authenticated:
                    self.move_line_to_saved_basket(line)

                    msg = render_to_string(
                        'basket/messages/line_saved.html',
                        {'line': line})
                    flash_messages.info(msg)

                    save_for_later = True
                else:
                    msg = _("You can't save an item for later if you're "
                            "not logged in!")
                    flash_messages.error(msg)
                    return redirect(self.get_success_url())


        if save_for_later:
            # No need to call super if we're moving lines to the saved basket
            response = redirect(self.get_success_url())
        else:
            # Save changes to basket as per normal

            response = super().formset_valid(formset)

        # If AJAX submission, don't redirect but reload the basket content HTML
        if self.request.is_ajax():
            # Reload basket and apply offers again
            self.request.basket = get_model('basket', 'Basket').objects.get(
                id=self.request.basket.id)
            self.request.basket.strategy = self.request.strategy
            Applicator().apply(self.request.basket, self.request.user,
                               self.request)
            offers_after = self.request.basket.applied_offers()


            for level, msg in BasketMessageGenerator().get_messages(
                    self.request.basket, offers_before, offers_after, include_buttons=False):
                flash_messages.add_message(level, msg)

            # Reload formset - we have to remove the POST fields from the
            # kwargs as, if they are left in, the formset won't construct
            # correctly as there will be a state mismatch between the
            # management form and the database.
            kwargs = self.get_formset_kwargs()

            del kwargs['data']
            del kwargs['files']
            if 'queryset' in kwargs:

                del kwargs['queryset']
            formset = self.get_formset()(queryset=self.get_queryset(),
                                         **kwargs)
            ctx = self.get_context_data(formset=formset,
                                        basket=self.request.basket)

            return self.json_response(ctx, flash_messages)

        BasketMessageGenerator().apply_messages(self.request, offers_before)

        return response

    def json_response(self, ctx, flash_messages):

        basket_html = render_to_string(
            'new_design/basket/basket_content.html',
            context=ctx, request=self.request)

        return JsonResponse({
            'content_html': basket_html,
            'messages': flash_messages.as_dict()
        })

    def move_line_to_saved_basket(self, line):
        saved_basket, _ = get_model('basket', 'basket').saved.get_or_create(
            owner=self.request.user)
        saved_basket.merge_line(line)

    def formset_invalid(self, formset):
        print("invalid",formset.errors, formset )
        flash_messages = ajax.FlashMessages()
        flash_messages.warning(_(
            "Your basket couldn't be updated. "
            "Please correct any validation errors below."))

        if self.request.is_ajax():
            ctx = self.get_context_data(formset=formset,
                                        basket=self.request.basket)
            return self.json_response(ctx, flash_messages)

        flash_messages.apply_to_request(self.request)
        return super().formset_invalid(formset)


class CustomVoucherAddView(VoucherAddView):

    """
    Apply coupon oscar extended class.
    """

    def get(self, request, *args, **kwargs):
        return redirect('basket:summary')

    def apply_voucher_to_basket(self, voucher):
        if voucher.is_expired():
            messages.error(
                self.request,
                _("The '%(code)s' voucher has expired") % {
                    'code': voucher.code},
                extra_tags='coupon_invalid'
            )
            return

        if not voucher.is_active():
            messages.error(
                self.request,
                _("The '%(code)s' voucher is not active") % {
                    'code': voucher.code},
                extra_tags='coupon_invalid'
            )
            return

        is_available, message = voucher.is_available_to_user(self.request.user)
        if not is_available:
            messages.error(self.request, message)
            return

        if voucher.benefit.range.included_categories.all().count() > 0 and not voucher.benefit.range.coupon_distibutor:
            print("range@@")
            lines = self.request.basket.all_lines()
            print("range##",lines)
            status = False
            for line in lines:
                cat_list = []
                for category in voucher.benefit.range.included_categories.all():
                    id_list = [obj for obj in category.get_descendants_and_self() ]
                    for element in id_list:
                        cat_list.append(element)


                if not line.is_package_product and line.product.categories.all().last() in cat_list:
                    status = True
                    break
            if not status:
                messages.error(
                    self.request,
                    _("The '%(code)s' voucher is not available") % {
                        'code': voucher.code},
                    extra_tags='coupon_invalid'
                )
                print("range**")
                return

        if voucher.benefit.range.min_billing_amount:
            print("range@@$")
            amount = 0
            amount = self.request.basket.cart_total_without_tax
            if not amount >= voucher.benefit.range.min_billing_amount:
                messages.error(
                    self.request,
                    _("The '%(code)s' voucher is not applicable because of minimum billing amount ") % {
                        'code': voucher.code},
                    extra_tags='coupon_invalid'
                )
                print("range**$")
                return


        print("range",voucher.benefit.range.included_categories.all())
        self.request.basket.vouchers.add(voucher)

        # Raise signal
        self.add_signal.send(
            sender=self, basket=self.request.basket, voucher=voucher)

        # Recalculate discounts to see if the voucher gives any
        Applicator().apply(self.request.basket, self.request.user,
                           self.request)
        discounts_after = self.request.basket.offer_applications
        print("discount",discounts_after)
        # Look for discounts from this new voucher
        found_discount = False
        for discount in discounts_after:
            print("disco",discount)
            if discount['voucher'] and discount['voucher'] == voucher:
                print("voucher", discount["voucher"], voucher)
                found_discount = True
                break
        if not found_discount:
            messages.warning(
                self.request,
                _("This coupon code is not applicable for this category"),
                extra_tags='coupon_invalid'
            )
            self.request.basket.vouchers.remove(voucher)
        else:
            messages.info(
                self.request,
                _("Voucher '%(code)s' added to basket") % {
                    'code': voucher.code},
                extra_tags='coupon_valid'
            )

    def form_valid(self, form):

        code = form.cleaned_data['code']
        if not self.request.basket.id:
            return redirect_to_referrer(self.request, 'basket:summary')
        if self.request.basket.contains_voucher(code):
            messages.error(
                self.request,
                _("You have already added the '%(code)s' voucher to "
                  "your basket") % {'code': code},
                extra_tags='coupon_invalid'
            )
        else:
            try:
                voucher = self.voucher_model._default_manager.get(code=code)
            except self.voucher_model.DoesNotExist:
                messages.error(
                    self.request,
                    _("No voucher found with code '%(code)s'") % {'code': code},
                    extra_tags='coupon_invalid'
                )
            else:
                self.apply_voucher_to_basket(voucher)
        return redirect_to_referrer(self.request, 'basket:summary')

    def form_invalid(self, form):
        messages.error(self.request, _("Please enter a voucher code"), extra_tags='coupon_invalid')
        return redirect(reverse('basket:summary') + '#voucher')


def abandoned_carts(request):

    import datetime
    today_date = datetime.datetime.now().date()

    wishlists = WishList.objects.all()
    current_site = Site.objects.get_current()

    for wish in wishlists:

        if (today_date - wish.date_created.date()).days > 1 and not AbandonedCartLogs.objects.filter(wishlist=wish):

            if wish.owner and not wish.owner.is_superuser:

                email_data = {
                    'mail_subject': 'TakeRentPe : Abandoned Carts',
                    'mail_template': 'customer/email/cart_reminder_email.html',
                    'mail_to': [wish.owner.email],
                    'mail_type': 'ab_cart',
                    'user_id': wish.owner.id,
                    'domain': current_site.domain
                }

                trigger_email.delay(**email_data)

                #ABONDONED CART REMINDER SMS
                if wish.owner.is_staff:
                    active_user = User.objects.filter(id=wish.owner.id).values_list('id')
                    active_partner = Partner.objects.filter(users__in=active_user)
                    mobile_number = active_partner.last().telephone_number
                else:
                    mobile_number = wish.owner.profile_user.mobile_number
                message = 'We noticed you left something in your cart. Complete your order now and get more offers! Hurry up! Take Rent Pe.'
                msg_kwargs = {
                    'message': message,
                    'mobile_number': mobile_number,
                }
                send_sms(**msg_kwargs)

                AbandonedCartLogs.objects.create(user=wish.owner, wishlist=wish)

    return HttpResponse('*************** Abandoned Cron Called ***************')


Basket = get_model('basket', 'Basket')
BasketLine = get_model('basket', 'Line')

Partner = get_model('partner', 'Partner')
Attribute_Mapping = get_model('catalogue', 'Attribute_Mapping')
Attribute = get_model('catalogue', 'Attribute')
StockRecord = get_model('partner', 'StockRecord')
from datetime import date, datetime, timedelta
from .bind import *
from django.views.generic import FormView, View

class CreateNewCart(FormView):

    """
    Handles the add-to-basket submissions view.
    """

    form_class = AddToBasketForm
    product_model = get_model('catalogue', 'product')
    add_signal = basket_addition
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        """
        Post method to add product to cart.
        :param request: default
        :param args: default
        :param kwargs: default
        :return: instance
        """

        self.product = shortcuts.get_object_or_404(self.product_model, pk=kwargs['pk'])
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):

        """
        Method to fetch url parms.
        :return: keywords parms.
        """

        kwargs = super().get_form_kwargs()
        kwargs['basket'] = self.request.basket
        kwargs['product'] = self.product

        return kwargs

    def form_invalid(self, form):

        """
        Handel form invalid.
        :param form: form instance
        :return: invalid form
        """

        msgs = []
        for error in form.errors.values():
            msgs.append(error.as_text())
        clean_msgs = [m.replace('* ', '') for m in msgs if m.startswith('* ')]

        messages.error(self.request, ",".join(clean_msgs), extra_tags='basket_error')

        return redirect('/catalogue/'+str(self.product.slug)+'_'+str(self.product.id))

    def form_valid(self, form):
        """
        Handel form valid.
        :param form: form instance
        :return: data
        """

        offers_before = self.request.basket.applied_offers()

        cart_data = {
            'customized_basket': True,
            'owner': self.request.user
        }
        basket = Basket.objects.create(**cart_data)

        product_price, product_rent_price = 0, 0

        stockrecord = StockRecord.objects.get(product=form.product)
        stock_info = StockRecord.objects.get(product=form.product)
        line_reference = str(form.product.id) + '_' + str(stockrecord.id)
        order_type = form.cleaned_data['order_type']

        start_date, end_date = datetime.now(), datetime.now()
        product_price, product_rent_price = 0, 0
        booking_start_date = form.cleaned_data['booking_start_date']
        booking_end_date = form.cleaned_data['booking_end_date']
        quantity = form.cleaned_data['quantity']
        flower_type = form.cleaned_data['flower_type']
        # create product for sale
        if order_type == 'Sale':
            # set current date by default
            # start_date, end_date = datetime.now(), datetime.now()
            # start_date, end_date = datetime.now(), datetime.now()
            start_date = datetime.strptime(booking_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(booking_end_date, '%Y-%m-%d')

            product_price = get_product_price(stock_info, 'Sale', quantity, 1, flower_type)
            product_rent_price = stock_info.rent_price

        if order_type in ['Rent', 'Professional']:
            if order_type == 'Rent':
                start_date = datetime.strptime(booking_start_date, '%Y-%m-%d')
                end_date = datetime.strptime(booking_end_date, '%Y-%m-%d')

            if order_type == 'Professional':
                start_date = datetime.strptime(booking_start_date, '%Y-%m-%d %I:%M %p')
                end_date = datetime.strptime(booking_end_date, '%Y-%m-%d %I:%M %p')

            total_days_obj = end_date - start_date
            total_days = total_days_obj.days + 1

            product_price = get_product_price(stock_info, 'Rent', quantity, total_days, flower_type)
            product_rent_price = product_price

        if order_type == 'Rent':
            start_date = booking_start_date
            end_date = booking_end_date

        if order_type == 'Professional':
            start_date = datetime.strptime(booking_start_date, '%Y-%m-%d %I:%M %p')
            end_date = datetime.strptime(booking_end_date, '%Y-%m-%d %I:%M %p')

        if order_type == 'Sale' and form.product.product_class.name == 'Rent Or Sale':
            advance_payment_percentage = stock_info.sale_advance_payment_percentage
        else:
            advance_payment_percentage = stock_info.advance_payment_percentage

        BasketLine.objects.create(
            basket=basket, line_reference=line_reference,
            product=form.product, stockrecord=stockrecord,
            quantity=quantity,
            price_excl_tax=product_price,
            price_currency=stock_info.price_currency,
            advance_payment_percentage=advance_payment_percentage,
            minimum_qty=stock_info.minimum_qty, tax_percentage=stock_info.tax_percentage,
            shipping_charges=stock_info.shipping_charges, rent_price=product_rent_price,
            order_type=order_type, booking_start_date=start_date, booking_end_date=end_date, flower_type = flower_type
        )
        # messages.success(self.request, self.get_success_message(form))

        # Check for additional offer messages
        # BasketMessageGenerator().apply_messages(self.request, offers_before)
        if form.product.is_package and form.product.product_package.all().count() > 0:
            for prod in form.product.product_package.all():
                status = False
                prod_stockrecord = StockRecord.objects.get(product=prod)
                if prod.product_class.name == "Rent" and prod.is_approved == "Approved":

                    status = True
                elif prod.is_approved == "Approved":

                    if prod_stockrecord.num_in_stock and prod_stockrecord.num_allocated:
                        if prod_stockrecord.num_in_stock > prod_stockrecord.num_allocated:
                            status = True
                        else:
                            status = False
                    if prod_stockrecord.num_in_stock and not prod_stockrecord.num_allocated:
                        status = True


                if status:
                    line_reference = str(prod.id) + '_' + str(prod_stockrecord.id)
                    prod_stockrecord = StockRecord.objects.get(product=prod)
                    prod_stock_info = StockRecord.objects.get(product=prod)
                    if not prod.product_class.name == 'Rent Or Sale':
                        if prod.product_class.name in ['Rent', 'Professional']:
                            order_type = 'Rent'
                        if prod.product_class.name == 'Sale':
                            order_type = 'Sale'

                    if order_type in ['Rent', 'Professional']:
                        product_price = get_product_price(prod_stock_info, 'Rent', quantity, total_days,
                                                          flower_type)
                    else:
                        product_price = get_product_price(prod_stock_info, 'Sale', quantity, total_days,
                                                          flower_type)
                    prod_product_rent_price = product_price
                    product_price1 = 0
                    BasketLine.objects.create(
                        basket=basket, line_reference=line_reference,
                        product=prod, stockrecord=prod_stockrecord,
                        quantity=1,
                        price_excl_tax=product_price1,
                        price_currency=prod_stock_info.price_currency,
                        advance_payment_percentage=prod_stock_info.advance_payment_percentage,
                        minimum_qty=prod_stock_info.minimum_qty, tax_percentage=prod_stock_info.tax_percentage,
                        shipping_charges=prod_stock_info.shipping_charges, rent_price=prod_product_rent_price,
                        order_type=order_type, booking_start_date=start_date, booking_end_date=end_date,
                        is_package_product=True
                    )

        # Send signal for basket addition
        basket.status = 'Frozen'
        basket.save()


        # Basket.objects.filter(owner=self.request.user, customized_basket=False, status='Open').delete()
        # basket = Basket.objects.get(id=basket.id, customized_basket=True)
        # basket.status = 'Open'
        # basket.save()

        # success_msg =  "%s Product has been added to your basket."% (form.product.get_title())
        # messages.success(
        #     self.request, success_msg)


        self.add_signal.send(sender=self, product=form.product, user=self.request.user, request=self.request)
        return redirect('checkout:index')
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_message(self, form):

        """
        return success message
        :param form: form instance
        :return: message
        """

        return render_to_string(
            'basket/messages/addition.html',
            {
                'product': form.product,
                'quantity': form.cleaned_data['quantity']
            }
        )

    def get_success_url(self):

        """
        return success url
        :return: url
        """

        post_url = self.request.POST.get('next')
        referrer = self.request.META.get('HTTP_REFERER')

        # post_url = None
        if post_url and is_safe_url(post_url, self.request.get_host()):
            return safe_referrer(self.request, 'basket:summary')
        return referrer
