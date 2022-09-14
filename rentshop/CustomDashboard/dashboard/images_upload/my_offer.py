from django.contrib import messages
from django.shortcuts import render, redirect

from django.views import generic
from .my_offer_form import *
Admin_HeaderMenu = get_model('HeaderMenu', 'Admin_HeaderMenu')


class ImagesUploadView(generic.FormView):

    """
    Combo view that can both create and update view.
    """

    template_name = 'dashboard/image-upload/form.html'

    def get(self, request, *args, **kwargs):
        type = kwargs.get('type')
        menu_obj = Admin_HeaderMenu.objects.filter(title_id__title = 'My Offers')
        return render(request, self.template_name,{'menu_obj':menu_obj})


class CustomFlatPagesCreateUpateViewV1(generic.FormView):

    """
    Combo view that can both create and update view.
    """

    template_name = 'dashboard/image-upload/form_v1.html'
    form = MyOfferUploadImages

    def get(self, request, *args, **kwargs):

        form = self.form()
        page_title, page_type = '', ''
        offer_id = request.GET.get('type')
        menu_obj = Admin_HeaderMenu.objects.filter(title_id__title = 'My Offers').values_list('id',flat= True)
        menu_list = list(menu_obj)
        if int(offer_id) not in menu_list:
            messages.error(request, 'Invalid request.')
            return redirect('/dashboard')

        if offer_id:

            if Admin_HeaderMenu.objects.filter(id=int(offer_id)):
                cust_obj = Admin_HeaderMenu.objects.filter(id=int(offer_id))
                cust = cust_obj.last()
                page_title = cust.sub_title
                id = cust.id

                form = self.form(instance=cust)
            else:
                form = self.form()

        return render(request, self.template_name, {'form': form, 'page_title': page_title,'id': id})

    def post(self, request, *args, **kwargs):

        form = self.form(request.POST,request.FILES)
        if not form.is_valid():
            messages.error(request, 'Something went wrong.')
            return redirect('/dashboard')

        offer_id = request.GET.get('type')
        offer_id = int(offer_id)
        data = request.FILES.get('menu_image',False)
        delete_img = request.POST.get('menu_image-clear')
        if offer_id:

            if Admin_HeaderMenu.objects.filter(id =offer_id) and data:
                cust_obj = Admin_HeaderMenu.objects.filter(id = offer_id)
                if cust_obj:
                    cust = cust_obj.last()
                    cust.menu_image =  request.FILES['menu_image']
                    form = self.form(instance=cust, data=request.POST)
                    form.save()
                    return self.success_url()
            elif delete_img:
                cust_obj = Admin_HeaderMenu.objects.filter(id=offer_id)
                if cust_obj:

                    cust = cust_obj.last()
                    cust.menu_image.delete()
                    cust.menu_image = 'image_not_found.jpg'
                    cust.menu_image.save()
                return self.success_url()
            else:
                return redirect('/dashboard/accounts/upload-my-offer-images/')

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')

    def success_url(self):

        messages.success(self.request, 'Image uploaded successfully.')
        return redirect('/dashboard/accounts/upload-my-offer-images/')
