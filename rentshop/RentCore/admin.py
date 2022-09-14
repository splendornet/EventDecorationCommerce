# django import
from django.contrib import admin

# internal imports
from . import models as core_model

from .models import CustomFlatPages
class SiteMessageAdmin(admin.ModelAdmin):

    pass

admin.site.register(CustomFlatPages)

admin.site.register(core_model.SiteMessage, SiteMessageAdmin)
