# python imports
from datetime import datetime

# django imports
from django.db.models import Sum
from django.views.generic import TemplateView, View
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt

# 3rd party imports
from oscar.core.loading import get_class, get_model
from oscar.apps.promotions.views import HomeView
from oscar.core.compat import get_user_model
from oscar.apps.promotions import views

# internal imports
from .forms import *

# model imports

CustomProfile = get_model('customer', 'CustomProfile')
StockRecord = get_model('partner', 'StockRecord')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
Coupon = get_model('voucher', 'Voucher')
Vouchers = get_model('voucher', 'Voucher')
Benefits = get_model('offer', 'Benefit')
Partner = get_model('partner', 'Partner')
Offers = get_model('offer','Condition')
CustomFlatPages = get_model('RentCore', 'CustomFlatPages')
SliderImage = get_model('FrontendSite', 'SliderImage')
Admin_HeaderMenu = get_model('HeaderMenu','Admin_HeaderMenu')
Admin_HeaderSubMenu = get_model('HeaderMenu','Admin_HeaderSubMenu')
Admin_Header = get_model('HeaderMenu','Admin_Header')
User = get_user_model()


# class CustomHomeView(HomeView):
#
#     """
#     Index page view.
#     """
#
#     template_name = 'promotions/home.html'
#
#     def get_product(self):
#
#         pro_qs = Product.objects.filter(is_approved='Approved', is_deleted=False)
#
#         cat_obj = Category.objects.filter(show_on_frontside=True, depth=1)
#         cat_list = []
#         for category in cat_obj:
#             id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
#             for element in id_list:
#                 cat_list.append(element)
#
#         recent_product = Product.objects.filter(is_approved='Approved', is_deleted=False, categories__in = cat_list).exclude(product_class_id=4, stockrecords=None).order_by('-id')[:5]
#         recent_service_provider = Product.objects.filter(is_approved='Approved',product_class_id=4, is_deleted=False).exclude(stockrecords=None).order_by('-id')[:4]
#         top_rated_service_provider = Product.objects.all().exclude(reviews__score=None, stockrecords=None).annotate(sum_score=Sum('reviews__score')).order_by('-sum_score')[:4]
#
#         all_categories_product = Product.objects.filter(is_approved='Approved', is_deleted=False).exclude(stockrecords=None)
#         all_categories_product_id = Product.objects.filter(is_approved='Approved', is_deleted=False).exclude(stockrecords=None)
#
#         is_approved_cat = Category.objects.filter(product__in=all_categories_product_id, depth=1, show_on_frontside = True).distinct()
#
#         offers_category_obj = Category.objects.filter(slug='offers',show_on_frontside = True).last()
#         approved_offer_category= None
#         offers_product = None
#         if offers_category_obj:
#             offers_category_decent = offers_category_obj.get_descendants()
#
#             offer_category_id = []
#             for master_offer in offers_category_decent:
#                 if master_offer.product_set.filter(is_approved='Approved').exclude(stockrecords=None):
#                     offer_category_id.append(master_offer.id)
#
#             approved_offer_category = Category.objects.filter(id__in=offer_category_id)
#
#         # offer category
#             offers_category = Category.objects.filter(slug='offers')
#
#             offers_product = pro_qs.filter(categories__in=offers_category.values_list('id', flat=True)).exclude(stockrecords=None).order_by('id')[:10]
#
#         codes = []
#         home_offers = Vouchers.objects.all()
#         for offer in home_offers:
#
#             if not offer.is_active():
#                 codes.append(
#                     {
#                         'id': offer.id,
#                         'code': offer.code,
#                         'name': offer.name
#                     }
#                 )
#
#         slider_images = SliderImage.objects.all()
#         is_index_page = 1
#
#         label_color = 'red'
#         product_dict = {
#             'offers_category_decent': approved_offer_category,
#             'home_offers': codes,
#             'recent_product': recent_product,
#             'all_categories_product': all_categories_product,
#             'all_categories': is_approved_cat,
#             'label_color': label_color,
#             'slider_images': slider_images,
#             'is_index_page': is_index_page,
#             'recent_service_provider': recent_service_provider,
#             'top_rated_service_provider': top_rated_service_provider,
#             'offers_product': offers_product
#         }
#
#         return product_dict
#
#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         ctx.update(self.get_product())
#         return ctx


class CouponsView(TemplateView):

    """
    List of coupons template view
    """

    template_name = 'promotions/coupon_list.html'

    def coupon_list(self):

        coupon = Coupon.objects.filter(end_datetime__gte=datetime.now())

        coupon_dict = {
            'coupon': coupon,
        }

        return coupon_dict

    def get_context_data(self, **kwargs):
        # return cntext to template
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.coupon_list())
        return ctx


class AboutUs(TemplateView):

    """
    Template view to display about us page
    """

    template_name = "promotions/about_us.html"

    def get(self, request, *args, **kwargs):

        obj = CustomFlatPages.objects.filter(page_type=4).last()

        return render(self.request, self.template_name, {'obj': obj})



class FQAView(View):

    """
    View to display FAQ's
    """

    template_name = 'promotions/faq.html'

    def get(self, request, *args, **kwargs):

        """
        Method to return template
        :param request: default
        :param args: default
        :param kwargs: default
        :return: template
        """

        obj = CustomFlatPages.objects.filter(page_type=3).last()
        return render(self.request, self.template_name, {'obj': obj})


class PoliciesView(View):

    """
    View to display Policies.
    """

    template_name = 'promotions/policies.html'

    def get(self, request, *args, **kwargs):
        """
        Method to return template
        :param request: default
        :param args: default
        :param kwargs: default
        :return: template
        """

        obj = CustomFlatPages.objects.filter(page_type=1).last()

        return render(self.request, self.template_name, {'obj': obj})


class HWorksView(View):

    """
    View to display How it works.
    """

    template_name = 'promotions/how_it_works.html'

    def get(self, request, *args, **kwargs):
        """
        Method to return template
        :param request: default
        :param args: default
        :param kwargs: default
        :return: template
        """

        obj = CustomFlatPages.objects.filter(page_type=5).last()

        return render(self.request, self.template_name, {'obj': obj})


class ContactUsView(View):

    """
    Contact us post/get view
    """

    template_name = 'promotions/contact_us.html'
    form_class = ContactUsForm

    def get(self, request, *args, **kwargs):

        context = {
            'form': self.form_class
        }

        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        if form.is_valid() is False:

            context = {
                'form': form
            }

            return render(self.request, self.template_name, context=context)

        form.save()

        pr_details = {
            'name': form.cleaned_data['name'],
            'email': form.cleaned_data['email'],
            'phone': form.cleaned_data['phone'],
            'message': form.cleaned_data['message'],
        }

        return self.contact_us(form, **pr_details)

    def contact_us(self, form, **pr_details):

        try:

            name = form.cleaned_data['name']

            self.contact_email(form, **pr_details)

            success_message = 'Thanks %s for reaching out. We will get in touch shortly!' %(name)

            messages.success(self.request, success_message)
            return redirect('contact-us')

        except:
            messages.error(self.request, settings.ERROR_MESSAGE)
            return redirect('contact-us')

    def contact_email(self, form, **pr_details):

        try:

            message_user = render_to_string(
                'customer/email/contact_us_admin.html', {
                    'pr_details': pr_details,
                }
            )

            subject = 'Contact Us'
            from_email = settings.FROM_EMAIL_ADDRESS
            to_email = settings.CONTACT_ADMIN_EMAIL

            email = EmailMessage(subject, message_user, from_email, to_email)
            email.content_subtype = "html"
            email.send()

            return True

        except:
            return False


class TermsPageView(TemplateView):

    template_name = 'promotions/terms.html'

    def get(self, request, *args, **kwargs):

        obj = CustomFlatPages.objects.filter(page_type=2).last()

        return render(self.request, self.template_name, {'obj': obj})


@csrf_exempt
def update_first_login(request):

    """
    Method to update flag after user login for 1st time.
    :param request:
    :return:
    """

    if request.is_ajax():

        user_id = request.GET.get('user_id')

        if not user_id:
            return HttpResponse('503')

        user = User.objects.get(id=user_id)
        CustomProfile.objects.filter(user=user).update(is_first_login=False)
        return HttpResponse('200')

    return HttpResponse('503')


def test_email(request):

    mail_subject = 'TRP || TEST MAIL'
    mail_template = 'customer/email/contact_us_admin.html'
    mail_to = ['rmtest@yopmail.com']
    mail_context = {}

    message = render_to_string(
        mail_template, mail_context
    )

    to_email = mail_to
    from_email = settings.FROM_EMAIL_ADDRESS
    email = EmailMessage(mail_subject, message, from_email, to_email)
    email.content_subtype = "html"
    email.send()

    return HttpResponse('DONE')

class CustomHomeView(HomeView):

    """
    Index page view.
    """

    template_name = 'new_design/home.html'

    def get_product(self):


        cat_obj = Category.objects.filter(show_on_frontside=True, depth=1)
        cat_list = []
        for category in cat_obj:
            id_list = [obj.id for obj in category.get_descendants_and_self() if obj.show_on_frontside]
            for element in id_list:
                cat_list.append(element)



        slider_images = SliderImage.objects.filter(is_active = True,)
        is_index_page = 1

        best_deals = Category.objects.filter(show_on_frontside=True, show_in='1', sequence__isnull= False).order_by('sequence')
        what_we_offer = Category.objects.filter(show_on_frontside=True, show_in='2', sequence__isnull= False).order_by('sequence')
        featured_prod_obj = Product.objects.filter(is_approved='Approved', is_deleted=False, is_featured_product=True, categories__in= cat_list)

        header_menu_obj = Admin_Header.objects.get(title = "My Offers")
        header_submenu_obj = Admin_HeaderMenu.objects.filter(title_id=header_menu_obj.id)

        label_color = 'red'
        product_dict = {

            'slider_images': slider_images,
            'best_deals' : best_deals,
            'what_we_offer' : what_we_offer[:12],
            'featured_prod_obj' : featured_prod_obj,
            'my_offer' : header_submenu_obj,
        }

        return product_dict

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.get_product())
        return ctx


