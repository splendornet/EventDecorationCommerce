from django.db import models
from django.conf import settings
# Create your models here.


class SliderImage(models.Model):
    slider_image = models.ImageField(upload_to=settings.SLIDER_IMAGE_FOLDER)
    is_active = models.BooleanField(default=True)
    is_provide_path_link = models.BooleanField(default=False)
    path_link = models.CharField(max_length=256, blank=True, null=True)
    cta_button_text = models.CharField(max_length=256, blank=True, null=True)
    mobile_view_image = models.FileField(upload_to='slider/mobile_view_slider/', max_length=255,
                             blank=True, null=True, default='image_not_found.jpg')