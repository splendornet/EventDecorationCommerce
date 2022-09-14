from .models import *
from django.contrib import admin

class CustomizeCouponModelAdmin(admin.ModelAdmin):

    list_display = ('category', 'voucher','range')


admin.site.register(CustomizeCouponModel,CustomizeCouponModelAdmin)
admin.site.register(PriceRangeModel)
from oscar.apps.offer.admin import *  # noqa
