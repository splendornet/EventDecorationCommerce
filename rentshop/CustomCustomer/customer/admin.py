from .models import *
from django.contrib import admin


class CustomProfileAdmin(admin.ModelAdmin):

    list_display = ('get_users', 'mobile_number',)

    def get_users(self, obj):

        return obj.user.email


class EnquiryAdmin(admin.ModelAdmin):

    list_display = ('id', 'organization_name', 'person_name', 'basket_instance', 'created_by',)


class OTPClassAdmin(admin.ModelAdmin):

        list_display = ('mobile_number', 'otp', 'otp_sent_count','otp_attempt_count')
        ordering = ('-id',)


admin.site.register(ContactUs)
admin.site.register(CustomProfile, CustomProfileAdmin)
admin.site.register(Notes)
admin.site.register(Enquiry, EnquiryAdmin)
admin.site.register(OTPModel, OTPClassAdmin)


from oscar.apps.customer.admin import *  # noqa
