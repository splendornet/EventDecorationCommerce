# django imports
from django.contrib import admin

# internal imports
from .models import *


class VendorCalenderAdmin(admin.ModelAdmin):

    """
    Admin class to register vendor calender
    """

    list_filter = ('vendor', 'product',)
    search_fields = ('from_date',)


# admin sites registers
admin.site.register(VendorCalender, VendorCalenderAdmin)
admin.site.register(ProductUnit)
admin.site.register(MultiDB)
admin.site.register(IndividualDB)
admin.site.register(VendorProductStatus)

# oscar admin extender
from oscar.apps.partner.admin import *  # noqa
