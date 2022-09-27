# python imports
import datetime
import random
import math

# django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.http import JsonResponse
from django.db.models import F
from django.utils import timezone

from .forms import *
# 3rd party imports
from oscar.apps.customer.wishlists.views import *
from oscar.apps.customer.views import AccountAuthView, ProfileUpdateView, OrderDetailView, ProfileView, ChangePasswordView
from oscar.core.compat import get_user_model
from oscar.core.loading import (get_class, get_classes, get_model)
from oscar.apps.customer.utils import get_password_reset_url
from oscar.apps.customer import signals
from oscar.apps.voucher.abstract_models import AbstractVoucherApplication

# internal imports
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.shortcuts import render
from .forms import CustomEmailAuthenticationForm


PageTitleMixin, RegisterUserMixin = get_classes('customer.mixins', ['PageTitleMixin', 'RegisterUserMixin'])
Dispatcher = get_class('customer.utils', 'Dispatcher')
EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes(
    'customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm', 'OrderSearchForm']
)
PasswordChangeForm = get_class('customer.forms', 'PasswordChangeForm')
ProfileForm, ConfirmPasswordForm = get_classes(
    'customer.forms', ['ProfileForm', 'ConfirmPasswordForm']
)

Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')

Line = get_model('basket', 'Line')
Basket = get_model('basket', 'Basket')

Product = get_model('catalogue', 'Product')

UserAddressForm = get_class('address.forms', 'UserAddressForm')
UserAddress = get_model('address', 'UserAddress')
User = get_user_model()

Enquiry = get_model('customer', 'Enquiry')
OTPModel = get_model('customer', 'OTPModel')
CommunicationEventType = get_model('customer', 'CommunicationEventType')
EmailUserCreationForm_C = get_class('customer.forms','CustomEmailUserCreationForm')
Email = get_model('customer', 'Email')
custom_profile = get_model('customer', 'CustomProfile')
ProductAlert = get_model('customer', 'ProductAlert')
CustomProfileForm = get_class('customer.forms','CustomUserUpdateForm')
CustomPasswordChangeForm = get_class('customer.forms','CustomPasswordChangeForm')
CustomProfileUpdateForm = get_class('customer.forms','CustomUserUpdate')
CustomProfile = get_model('customer', 'CustomProfile')
Partner = get_model('partner', 'Partner')
Voucher = get_model('voucher', 'Voucher')

SiteMessages = get_class('RentCore.utils', 'SiteMessages')
send_email = get_class('RentCore.email', 'send_email')
trigger_email = get_class('RentCore.tasks', 'trigger_email')
send_sms = get_class('RentCore.email', 'send_sms')
CustomizeCouponModel = get_model('offer', 'CustomizeCouponModel')


class CustomWishListListView(WishListListView):
    template_name = 'new_design/customer/wishlists/wishlists_list.html'

    def get_queryset(self):
        return self.request.user.wishlists.filter(lines__product__is_deleted=False, lines__product__is_approved = 'Approved' )


class CustomChangePasswordView(ChangePasswordView):
    form_class = CustomPasswordChangeForm
    template_name = 'new_design/customer/profile/change_password.html'


class CustomAccountLoginView(AccountAuthView, SiteMessages):

    """
    Oscar extended login page view
    """

    # template_name = 'customer/user_login.html'
    template_name = 'new_design/customer/user_login.html'
    login_form_class = CustomEmailAuthenticationForm

    def validate_login_form(self):

        form = self.get_login_form(bind_data=True)
        print('form',form.is_valid(), form.errors)
        if form.is_valid():
            user = form.get_user()
            old_session_key = self.request.session.session_key
            auth_login(self.request, form.get_user())

            signals.user_logged_in.send_robust(
                sender=self, request=self.request, user=user,
                old_session_key=old_session_key)

            msg = self.get_login_success_message(form)
            if msg:
                messages.success(self.request, msg)
            if self.request.GET.get('next'):
                return redirect(self.request.GET.get('next'))
            else:
                return redirect(self.get_login_success_url(form))

        ctx = self.get_context_data(login_form=form)
        return self.render_to_response(ctx)


class CustomAccountRegistrationView(AccountAuthView, SiteMessages):

    """
    Customer register view.
    """

    # template_name = 'customer/user_register.html'
    template_name = 'new_design/customer/user_register.html'
    registration_form_class = EmailUserCreationForm_C

    def get_registration_form(self, bind_data=False):

        return self.registration_form_class(
            **self.get_registration_form_kwargs(bind_data)
        )

    def get_registration_form_kwargs(self, bind_data=False):

        kwargs = {}
        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.registration_prefix
        kwargs['initial'] = {'redirect_url': self.request.GET.get(self.redirect_field_name, ''),}

        if bind_data and self.request.method in ('POST', 'PUT'):
            kwargs.update({'data': self.request.POST, 'files': self.request.FILES,})

        return kwargs

    def validate_registration_form(self):

        kwargs = {}

        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.registration_prefix
        kwargs.update({'data': self.request.POST, 'files': self.request.FILES,})

        form = self.get_registration_form(bind_data=True)
        print('error', form.errors,)
        if form.is_valid():

            form.save()
            msg = self.get_registration_success_message(form)

            message_type = {
                'message_type': 'customer_after_register'
            }

            success_message = self.customer_messages(**message_type)
            messages.success(self.request, success_message)

            return redirect(self.get_registration_success_url( form))

        ctx = self.get_context_data(registration_form=form)
        return self.render_to_response(ctx)

    def get_registration_success_url(self, form):

        redirect_url = form.cleaned_data['redirect_url']

        password = form.cleaned_data['password1']
        try:

            email = form.cleaned_data['email']
            number = form.cleaned_data['mobile_number']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user_id = User.objects.get(email=email)
            User.objects.filter(email=email).update(is_active = True)
            custom_profile.objects.create(user_id=user_id.id,mobile_number=number)
            current_site = Site.objects.get_current()

            user_email_data = {
                'mail_subject': 'TakeRentPe - Account Verification',
                'mail_template': 'customer/emails/email_confirmation.html',
                'mail_to': [form.cleaned_data['email']],
                'mail_context': {
                    'first_name': first_name, 'last_name': last_name,
                    'email_id': email, 'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user_id.id)).decode(),
                    'token': account_activation_token.make_token(user_id),
                }
            }
            trigger_email.delay(**user_email_data)

            # email to admin after customer register
            admin_email_list = []
            admin_list = User.objects.filter(is_superuser=True, is_staff=True).values_list('email', flat=True)
            for i in admin_list:
                admin_email_list += [i]

            admin_email_data = {
                'mail_subject': 'TakeRentPe - New User Registered',
                'mail_template': 'customer/emails/user_registration_admin_email.html',
                'mail_to': admin_email_list,
                'mail_context': {
                    'user_obj': user_id,
                    'custom_profile': form.cleaned_data['mobile_number']
                }
            }

            trigger_email.delay(**admin_email_data)

            # user=authenticate(username=user_id.username, password=password)
            # if user is not None and user.is_active:
            #     auth_login(self.request, user)
            return settings.LOGIN_REDIRECT_URL

        except Exception as e:
            user=authenticate(username=user_id.username, password=password)
            if user is not None and user.is_active:
                auth_login(self.request, user)
                if self.request.GET.get('next'):
                    return self.request.GET.get('next')
            return settings.LOGIN_REDIRECT_URL


def email_activate(request, uidb64, token):

    """
    Method to active user via email activation link.

    To Do :
    Replace redirect coded url with proper django standard

    """

    try:

        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print("in email activate")

        if user is not None and account_activation_token.check_token(user, token):

            user.is_active = True
            user.save()


            welcome_email_data = {
                'mail_subject': 'TakeRentPe - Welcome',
                'mail_template': 'customer/email/user_welcome_email.html',
                'mail_to': [user.email],
                'mail_context': {
                    'first_name': user.first_name
                }
            }
            send_email(**welcome_email_data)

            # sms send to client for WELCOME SMS
            message = 'Welcome to the family! We are giving you 5 primary offers worth Rs.5000 to get you started. So hurry up!!  Happy Celebranto,Take Rent Pe.'
            msg_kwargs = {
                'message': message,
                'mobile_number': user.profile_user.mobile_number,
            }
            send_sms(**msg_kwargs)
            print('in welcome sms')
            messages.success(request, 'Your account has been activated successfully.')
            
            return redirect('/accounts/login/')

        else:
            return redirect('/accounts/login/')
    except Exception as e:
        print(e.args)
        return redirect('/accounts/login/')


class OrderHistoryView(PageTitleMixin, generic.ListView):

    """
    Customer order history
    """

    context_object_name = "orders"
    template_name = 'new_design/customer/order/order_list.html'
    paginate_by = settings.OSCAR_ORDERS_PER_PAGE
    model = Order
    form_class = OrderSearchForm
    page_title = _('Order History')
    active_tab = 'orders'

    def get(self, request, *args, **kwargs):

        if 'date_from' in request.GET:

            self.form = self.form_class(self.request.GET)

            if not self.form.is_valid():
                self.object_list = self.get_queryset()
                ctx = self.get_context_data(object_list=self.object_list)
                return self.render_to_response(ctx)

            data = self.form.cleaned_data

            if data['order_number'] and not (data['date_to'] or data['date_from']):

                try:
                    order = Order.objects.get(number=data['order_number'], user=self.request.user)
                except Order.DoesNotExist:
                    pass
                else:
                    return redirect('customer:order', order_number=order.number)
        else:
            self.form = self.form_class()
        return super(OrderHistoryView, self).get(request, *args, **kwargs)

    def get_queryset(self):

        qs = self.model._default_manager.filter(user=self.request.user)

        if self.form.is_bound and self.form.is_valid():
            qs = qs.filter(**self.form.get_filters())

        return qs

    def get_context_data(self, *args, **kwargs):

        ctx = super(OrderHistoryView, self).get_context_data(*args, **kwargs)
        ctx['form'] = self.form

        return ctx


class CustomProfileUpdateView(ProfileUpdateView):

    """
    Method to update customer profile.
    """

    form_class = CustomProfileForm
    template_name = 'new_design/customer/profile/profile_form.html'

    def get_form_kwargs(self):

        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):

        try:
            old_user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            old_user = None

        # to update end-user mobile number
        if form.data.get('mobile_number'):

            try:
                # CustomProfile.objects.get(user=self.request.user)

                obj = CustomProfile.objects.filter(user=self.request.user).update(
                    mobile_number=form.data.get('mobile_number')
                )
                if obj:
                    obj.last().mobile_number = form.data.get('mobile_number')
                    obj.save()
                else:
                    obj = CustomProfile.objects.create(
                        user=self.request.user,
                        mobile_number=form.data.get('mobile_number'),
                    )
                    obj.save()

            except Exception as e:
                print(':::::::::::::::::::::::::::::::::::::::;;')
                print(e.args)
                print(':::::::::::::::::::::::::::::::::::::::;;')
                pass

        form.save()

        new_email = form.cleaned_data.get('email')
        if new_email and old_user and new_email != old_user.email:

            ctx = {
                'user': self.request.user,
                'site': get_current_site(self.request),
                'reset_url': get_password_reset_url(old_user),
                'new_email': new_email,
            }
            msgs = CommunicationEventType.objects.get_and_render(
                code=self.communication_type_code, context=ctx)
            Dispatcher().dispatch_user_messages(old_user, msgs)

        messages.success(self.request, _("Profile updated"))
        return redirect(self.get_success_url())


class OrderSingleProductView(generic.View):

    """
    Method to view order details.
    """

    template_name = 'customer/order/order_single.html'

    def get(self, request, *args, **kwargs):

        order_id = kwargs.get('order_id')
        product_id = kwargs.get('product_id')
        line_id = kwargs.get('line_id')

        if not order_id and not product_id and not line_id:
            messages.error(self.request, 'Something went wrong.')
            return redirect('/')

        # get order details and line details
        try:

            order = Order.objects.get(id=order_id)
            line = OrderLine.objects.get(id=line_id)
            product = Product.objects.get(id=product_id)

        except:

            messages.error(self.request, 'Something went wrong.')
            return redirect('/')

        context = {
            'order': order,
            'product': product,
            'line': line
        }

        return render(self.request, self.template_name, context=context)


class FAQView(generic.TemplateView):

    """
    Method to view faq
    """

    template_name = 'new_design/customer/other/faq.html'


class UserCouponView(generic.View):

    """
    Method to view customer coupons.
    """

    template_name = 'new_design/customer/other/my_coupon.html'

    def get(self, request, *args, **kwargs):
        vouchers = Voucher.objects.all()

        context = {
            'active_vouchers': self.get_active_voucher_details(vouchers),
            'used_user_vouchers': self.get_user_voucher_details(vouchers),
            'vendor_vouchers': self.get_active_vendor_voucher_details(vouchers),
            'vendor_used_vouchers': self.get_vendor_voucher_details(vouchers),
            'categorywise_vouchers': self.get_categorywisevendor_voucher_details(vouchers),

        }
        print(type(context['active_vouchers']))
        return render(self.request, self.template_name, context=context)

    def get_active_voucher_details(self, queryset):
        voucher_list = []
        for voucher in queryset:
            if not voucher.is_active():
                continue

            voucher_code = voucher.code
            offer = voucher.offers.last().benefit
            offer_details = ''
            category_list = []
            if offer.range:
                offer_details = offer
                category_list = offer.range.included_categories.values_list('name', flat=True)
            voucher_list.append(
                {
                    'code': voucher_code,
                    'start_date': voucher.start_datetime.date(),
                    'end_date': voucher.end_datetime.date(),
                    'offer_details': offer_details,
                    'categories': category_list
                }
            )

            print("**************")
        print('get_active_voucher_details',voucher_list)

        return voucher_list

    def get_user_voucher_details(self, queryset):
        voucher_list = []
        for voucher in queryset:
            if not voucher.is_active():
                continue

            if voucher.applications.filter(voucher = voucher,user = self.request.user):
                print('voucher',voucher)
                voucher_code = voucher.code
                offer = voucher.offers.last().benefit
                offer_details = ''
                category_list = []
                if offer.range:
                    offer_details = offer
                    category_list = offer.range.included_categories.values_list('name', flat=True)
                v_obj = voucher.applications.filter(voucher=voucher, user=self.request.user).last()
                lines = OrderLine.objects.filter(order_id = v_obj.order_id)
                v_cat = []
                upc_list = []
                print('lines',lines, )
                cat_list = []
                for category in voucher.benefit.range.included_categories.all():
                    id_list = [obj for obj in category.get_descendants_and_self()]
                    for element in id_list:
                        cat_list.append(element)

                for line in lines:
                    print('lines cat',line.product.categories.all().last())
                    if not line.is_line_package_product and line.product.categories.all().last() and line.product.categories.all().last() in cat_list:
                        v_cat.append(line.product.categories.all().last().name)
                        upc_list.append(line.product.upc)

                voucher_list.append(
                    {
                        'code': voucher_code,
                        'used_date': voucher.applications.filter(voucher = voucher,user = self.request.user).last().date_created.date(),
                        'end_date': voucher.end_datetime.date(),
                        'offer_details': offer_details,
                        'categories': category_list,
                        'redeemded':v_cat,
                        'upc_list' : upc_list,
                    }
                )
            print("**************")
        print('get_user_voucher_details',voucher_list)

        return voucher_list

    def get_active_vendor_voucher_details(self, queryset):
        voucher_list = []
        for voucher in queryset:
            if not voucher.is_active():
                continue

            if voucher.benefit.range.coupon_distibutor and voucher.benefit.range.coupon_distibutor.email_id == self.request.user.email:
                print('voucher',voucher)
                voucher_code = voucher.code
                offer = voucher.offers.last().benefit
                offer_details = ''
                category_list = []
                if offer.range:
                    offer_details = offer
                    category_list = offer.range.included_categories.values_list('name', flat=True)
                voucher_list.append(
                    {
                        'code': voucher_code,
                        'start_date': voucher.start_datetime.date(),
                        'end_date': voucher.end_datetime.date(),
                        'offer_details': offer_details,
                        'categories': category_list
                    }
                )
            print("**************")
        print('get_active_vendor_voucher_details',voucher_list)

        return voucher_list

    def get_vendor_voucher_details(self, queryset):
        voucher_list = []
        for voucher in queryset:
            if not voucher.is_active():
                continue

            if voucher.benefit.range.coupon_distibutor and voucher.benefit.range.coupon_distibutor.email_id == self.request.user.email and voucher.applications.filter(voucher = voucher,user = self.request.user):
                print('voucher',voucher)
                voucher_code = voucher.code
                offer = voucher.offers.last().benefit
                offer_details = ''
                category_list = []
                if offer.range:
                    offer_details = offer
                    category_list = offer.range.included_categories.values_list('name', flat=True)

                v_obj = voucher.applications.filter(voucher=voucher, user=self.request.user).last()
                lines = OrderLine.objects.filter(order_id=v_obj.order_id)
                v_cat = []
                upc_list = []
                print('lines', lines, )
                cat_list = []
                for category in voucher.benefit.range.included_categories.all():
                    id_list = [obj for obj in category.get_descendants_and_self()]
                    for element in id_list:
                        cat_list.append(element)

                for line in lines:
                    print('lines cat', line.product.categories.all().last(),
                          line.product.categories.all().last().name in category_list)
                    if not line.is_line_package_product and line.product.categories.all().last() in cat_list:
                        v_cat.append(line.product.categories.all().last().name)
                        upc_list.append(line.product.upc)

                voucher_list.append(
                    {
                        'code': voucher_code,
                        'used_date': voucher.applications.filter(voucher = voucher,user = self.request.user).last().date_created.date(),
                        'end_date': voucher.end_datetime.date(),
                        'offer_details': offer_details,
                        'categories': category_list,
                        'redeemded': v_cat,
                        'upc_list': upc_list,
                    }
                )
            print("**************")
        print('get_vendor_voucher_details',voucher_list)

        return voucher_list

    def get_categorywisevendor_voucher_details(self, queryset):

        voucher_list = []
        for voucher in queryset:
            if not voucher.is_active():
                continue

            if voucher.benefit.range.coupon_distibutor and voucher.benefit.range.coupon_distibutor.email_id == self.request.user.email:
                print('voucher', voucher)
                voucher_code = voucher.code
                offer = voucher.offers.last().benefit
                offer_details = ''
                category_list = []
                if offer.range:
                    offer_details = offer
                    category_list = offer.range.included_categories.values_list('id', flat=True)

                c_obj = CustomizeCouponModel.objects.filter(category__id__in =category_list,voucher=voucher)

                for category in c_obj:
                    balanced_coupon = category.coupon_count
                    used_coupon = 0
                    if category.used_coupon_count:
                        balanced_coupon = category.coupon_count - category.used_coupon_count
                        used_coupon = category.used_coupon_count
                    voucher_list.append(
                        {
                            'category': category.category.name,
                            'coupon_count' : category.coupon_count,
                            'used_coupon' : used_coupon,
                            'balanced_coupon' : balanced_coupon
                        }
                    )

            print("**************")
        print('get_categorywisevendor_voucher_details', voucher_list)

        return voucher_list

class CustomOrderListView(View):

    template_name = 'new_design/customer/order/custom_order_list.html'

    def get(self, request, *args, **kwargs):

        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        context = dict()

        user = request.user

        if not user.is_active:
            return redirect('/')

        context['user'] = user
        enquiry = Enquiry.objects.filter(created_by=user, basket_instance__isnull=False, basket_instance__status='Frozen')

        context['enquiry'] = enquiry
        context['page_title'] = 'My Custom Order'

        return render(request, self.template_name, context=context)


class PlaceCustomOrder(View):

    def get(self, request, *args, **kwargs):

        try:

            basket_id = request.GET.get('basket_id')

            if not basket_id:
                return redirect('/')

            if not Basket.objects.filter(id=basket_id, customized_basket=True):
                return redirect('/')

            Basket.objects.filter(owner=request.user, customized_basket=False, status='Open').delete()
            basket = Basket.objects.get(id=basket_id, customized_basket=True)
            basket.status = 'Open'
            basket.save()

            return redirect('/basket/')

        except Exception as e:

            return redirect('/')


class CustomOrderDetailView(OrderDetailView):

    def get_template_names(self):
        return ["new_design/customer/order/order_detail.html"]


class CustomProfileView(ProfileView):
    template_name = 'new_design/customer/profile/profile.html'
    form1 = CustomPasswordChangeForm

    def get_context_data(self, **kwargs):
        ctx = super(ProfileView, self).get_context_data(**kwargs)
        ctx['profile_fields'] = self.get_profile_fields(self.request.user)
        ctx['form1'] = self.form1
        return ctx


def get_otp(request):
    print('get',request.GET)
    mobile_number = request.GET.get('mobile_number')
    email = request.GET.get('email')
    password = request.GET.get('password')
    confirm_password = request.GET.get('confirm_password')
    form = request.GET.get('form')
    form = EmailUserCreationForm_C(form)

    if User._default_manager.filter(email__iexact=email).exists():
        status = "email exist"
    elif custom_profile.objects.filter(mobile_number__iexact=mobile_number).exists():
        status = "already exist"
    elif confirm_password != password:
        status = "password not matching"
    else:
        responce = ''
        digits = [i for i in range(0, 10)]
        random_str = ""
        for i in range(6):
            index = math.floor(random.random() * 10)
            random_str += str(digits[index])

        # integrate SMS Gateway

        message = "Otp is sent on your mobile number."
        sms_message = str(random_str) + " is One-Time Password for your Take Rent Pe account, valid for 10 minutes only. Please do not share your OTP with anyone. Take Rent Pe"
        sms_kwargs = {
            'message': sms_message,
            'mobile_number': mobile_number
        }

        otp_obj = OTPModel.objects.filter(mobile_number=mobile_number)
        if otp_obj:
            if not otp_obj.last().otp_sent_count > 4:
                try:
                    responce = send_sms(**sms_kwargs)
                    print('res', responce)
                except Exception as e:
                    print(e.args)
                otp_obj = OTPModel.objects.filter(mobile_number=mobile_number).update(
                    otp_sent_count=F('otp_sent_count') + 1, otp=random_str, sms_response=responce,
                    date_update=datetime.datetime.now())
                status = "sms-send"
            else:
                status = "exceed"
        else:
            try:
                responce = send_sms(**sms_kwargs)
                print('res', responce)
            except Exception as e:
                print(e.args)
            OTPModel.objects.create(mobile_number=mobile_number, otp=random_str, otp_sent_count=1,
                                    sms_response=responce)
            status ="sms-send"

    context = {
        'status': status,
    }
    print("context",context)
    return JsonResponse(context)


def verify_otp(request):
    print('in verify otp')
    responce = ''
    otp = ''
    mobile_number = request.GET.get('mobile_number')
    digit_1 = request.GET.get('digit_1')
    digit_2 = request.GET.get('digit_2')
    digit_3 = request.GET.get('digit_3')
    digit_4 = request.GET.get('digit_4')
    digit_5 = request.GET.get('digit_5')
    digit_6 = request.GET.get('digit_6')


    try:
        OTPModel.objects.filter(mobile_number=mobile_number).update(otp_attempt_count = F('otp_attempt_count') + 1)
        if digit_1 and digit_2 and digit_3 and digit_4 and digit_5 and digit_6:
            otp = str(digit_1) + str(digit_2) + str(digit_3) + str(digit_4) + str(digit_5) + str(digit_6)
        if otp:
            otp_obj = OTPModel.objects.filter(mobile_number=mobile_number, otp=otp)

            if otp_obj:
                if otp_obj.last().otp_attempt_count > 4:
                    status = "501"
                else:
                    status = "200"
                    OTPModel.objects.filter(mobile_number=mobile_number, otp=otp).delete()

                # elif otp_obj.last().date_update + datetime.timedelta(seconds=60)  < datetime.datetime.now():
                #     status ="502"

                # status = 200

            else:
                status = "400"
        else :
            status = "401"
        context = {
            'status': status
        }
        print('res1 ', context)
        return JsonResponse(context)
    except:
        status = "400"
        context = {
            'status': status
        }
        print('res2 ', context)
        return JsonResponse(context)


def get_vendor_otp(request):


    mobile_number = request.GET.get('mobile_number')
    email = request.GET.get('email')
    id_alternate_mobile_number = request.GET.get('id_alternate_mobile_number')

    if Partner.objects.filter(telephone_number__iexact=mobile_number).exists():
        status = "already exist"
    elif User.objects.filter(email=email):
        status = "email exist"
    elif Partner.objects.filter(alternate_mobile_number__iexact=id_alternate_mobile_number).exists():
        status = "already exist"
    else:
        responce = ''
        digits = [i for i in range(0, 10)]
        random_str = ""
        for i in range(6):
            index = math.floor(random.random() * 10)
            random_str += str(digits[index])

        # integrate SMS Gateway

        message = "Otp is sent on your mobile number."
        sms_message = str(random_str) + " is One-Time Password for your Take Rent Pe account, valid for 10 minutes only. Please do not share your OTP with anyone."
        sms_kwargs = {
            'message': sms_message,
            'mobile_number': mobile_number
        }

        otp_obj = OTPModel.objects.filter(mobile_number=mobile_number)
        if otp_obj:
            print("data", otp_obj.last().otp_sent_count > 4)
            print("data11", otp_obj.last().otp_sent_count)
            if not otp_obj.last().otp_sent_count > 4:
                try:
                    responce = send_sms(**sms_kwargs)
                except Exception as e:
                    print(e.args)
                otp_obj = OTPModel.objects.filter(mobile_number=mobile_number).update(
                    otp_sent_count=F('otp_sent_count') + 1, otp=random_str, sms_response=responce,
                    date_update=datetime.datetime.now())
                status = "sms-send"
            else:
                status = "exceed"
        else:
            try:
                responce = send_sms(**sms_kwargs)
            except Exception as e:
                print(e.args)
            OTPModel.objects.create(mobile_number=mobile_number, otp=random_str, otp_sent_count=1,
                                    sms_response=responce)
            status ="sms-send"

    context = {
        'status': status,
    }

    print("context",context)
    return JsonResponse(context)


from django.views.generic import View
# PasswordChangeForm = get_class('dashboard.forms', 'CustomVoucherForm')
from django.contrib.sites.shortcuts import get_current_site
from oscar.apps.customer.utils import get_password_reset_url
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse, reverse_lazy


Dispatcher = get_class('customer.utils', 'Dispatcher')
CommunicationEventType = get_model('customer', 'CommunicationEventType')


class ClientChangePassword(generic.FormView):
    form_class = CustomPasswordChangeForm
    # template_name = 'FrontendSite/password_change.html'
    template_name = 'new_design/customer/profile/profile.html'
    communication_type_code = 'PASSWORD_CHANGED'

    success_url = reverse_lazy('customer:profile-view')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['form1'] = self.form_class
        print('here')
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, _("Password updated"))

        ctx = {
            'user': self.request.user,
            'site': get_current_site(self.request),
            'reset_url': get_password_reset_url(self.request.user),
        }
        msgs = CommunicationEventType.objects.get_and_render(
            code=self.communication_type_code, context=ctx)
        Dispatcher().dispatch_user_messages(self.request.user, msgs)

        return redirect(self.get_success_url())

    def form_invalid(self, form):

        """
        Handel form invalid.
        :param form: form instance
        :return: invalid form
        """
        print('in invalid@')
        msgs = []

        for error in form.errors.values():
            msgs.append(error.as_text())
        clean_msgs = [m.replace('* ', '') for m in msgs if m.startswith('* ')]

        messages.error(self.request, ",".join(clean_msgs), extra_tags='basket_error')
        print('error', clean_msgs)
        return redirect('/accounts/profile/')


    def post(self, request, *args, **kwargs):

        print('in post', request.POST)

        form = self.form_class(data=request.POST, user=request.user)
        print('form',form)
        if form.is_valid():
            return self.is_valid(form)
        else:
            return self.is_invalid(form)

    def is_valid(self, form):

        base_form = form.save(commit=False)
        base_form.save()

        update_session_auth_hash(self.request, self.request.user)
        ctx = {
            'user': self.request.user,
            'site': get_current_site(self.request),
            'reset_url': get_password_reset_url(self.request.user),
        }
        msgs = CommunicationEventType.objects.get_and_render(
            code=self.communication_type_code, context=ctx)
        Dispatcher().dispatch_user_messages(self.request.user, msgs)

        messages.success(self.request, 'Password updated.')
        return redirect(self.get_success_url())

    def is_invalid(self, form):

        context = dict()
        context['form1'] = form
        print('in invalid')
        return render(self.request, self.template_name, context=context)








