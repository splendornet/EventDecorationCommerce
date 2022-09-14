from .models import *
from django.contrib import admin


class CCavenuePaymentDetailsAdmin(admin.ModelAdmin):

    list_display = ('order', 'transaction_id', 'amount', 'status')
    list_filter = ('order', 'status',)


class OrderAllocatedVendorAdmin(admin.ModelAdmin):

    list_display = ('order', 'order_line', 'vendor')

class CancellationChargesAdmin(admin.ModelAdmin):

    list_display = ('apply_to', 'charges_percentage', )

admin.site.register(CustomBillingAddress)

admin.site.register(CCavenuePaymentDetails, CCavenuePaymentDetailsAdmin)
admin.site.register(OrderAllocatedVendor, OrderAllocatedVendorAdmin)
admin.site.register(CancellationCharges,CancellationChargesAdmin)

from oscar.apps.order.admin import *  # noqa
