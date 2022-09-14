from django.shortcuts import render
import datetime
import json
from django.contrib import messages
from django.db.models import QuerySet, Q
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.datetime_safe import date
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.views.generic import TemplateView, View, FormView
from .models import *
from .forms import *


class Slider(View):

    slider_form_obj = SliderImageForm

    def get_template_names(self):
        return ['FrontendSite/index.html']

    def get(self, request, *args, **kwargs):
        slider_form = self.slider_form_obj(initial='')
        slider_obj = SliderImage.objects.all()

        form_data = {
            'slider_form':slider_form,
            'slider_obj': slider_obj,
        }
        return render(request, 'FrontendSite/index.html', form_data)

    def post(self, request, *args, **kwargs):

        slider_obj_form = self.slider_form_obj(request.POST, request.FILES)
        if slider_obj_form.is_valid():
            slider_img_obj = slider_obj_form.save(commit=False)
            slider_obj_form.save()
            return HttpResponseRedirect('/slider/')
        else:
            slider_obj = SliderImage.objects.all()
            form_data = {
                'slider_form': slider_obj_form,
                'slider_obj': slider_obj,
            }
            return render(request, 'FrontendSite/index.html', form_data)

    def update_slider(request, pk):
        try:
            slider_form_obj = SliderImageForm
            slider_form = slider_form_obj(initial='')
            slider_obj = SliderImage.objects.all().order_by('-id')

            if request.method == 'POST':
                instance = get_object_or_404(SliderImage, pk=pk)
                form = SliderImageForm(request.POST, request.FILES, instance=instance)

                if form.is_valid():
                    form_obj = form.save(commit=False)
                    if request.FILES.get('slider_img_update1',False):
                        form_obj.slider_image = request.FILES['slider_img_update1']
                    if not request.POST.get('is_provide_path_link', False):
                        form_obj.path_link = None
                        form_obj.cta_button_text = None
                    form.save()

                    form_data = {
                        'slider_form': slider_form,
                        'slider_obj': slider_obj,
                    }
                    return HttpResponseRedirect('/slider/')
                else:
                    slider_obj = SliderImage.objects.all()
                    form_data = {
                        'slider_form': form,
                        'slider_obj': slider_obj,
                    }
                    return render(request, 'FrontendSite/index.html', form_data)
            else:
                obj = SliderImage.objects.filter(id = pk)
                slider_form = slider_form_obj(instance = obj.last())
                form_data = {
                    'slider_form': slider_form,
                    'slider_obj': slider_obj,
                    'upload_id': 1,
                }
                return render(request, 'FrontendSite/index.html', form_data)
        except Exception as e:

            import os
            import sys
            print('-----------in exception----------')
            print(e.args)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            return HttpResponseRedirect('/slider/')


    def delete_slider(request, pk):
        try:
            img = SliderImage.objects.get(id=pk)
            img.delete()
            return HttpResponseRedirect('/slider')
        except:
            return HttpResponseRedirect('/slider')
