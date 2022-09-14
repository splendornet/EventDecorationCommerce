from django.conf.urls import url, include
from django.views.generic import TemplateView
from .views import *

urlpatterns = [
    url(r'^slider/', Slider.as_view(), name='slider'),
    #url(r'^slider_update/(?P<pk>\d+)/', update, name='update')
    url(r'^update_slider/(?P<pk>\d+)/', Slider.update_slider, name='update_slider'),
    url(r'^delete_slider/(?P<pk>\d+)/', Slider.delete_slider, name='update_slider'),
]