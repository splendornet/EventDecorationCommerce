# django imports
from django.contrib import admin

# internal imports
from .models import *


class AdminHeaderSite(admin.ModelAdmin):

    """
    Header site admin class
    """

    list_display = ('title', 'sequence_number', 'id',)


class AdminHeaderMenuSite(admin.ModelAdmin):

    """
    Header menu site admin class
    """

    list_display = ('sub_title', 'title_id',)
    list_per_page = 10
    list_filter = ('title_id',)


class AdminHeaderSubMenuSite(admin.ModelAdmin):

    """
    Header sub menu site admin class
    """

    list_display = ('sub_menu_title', 'url','header_menu_id',)
    list_per_page = 10
    list_filter = ('header_menu_id',)


admin.site.register(Admin_Header, AdminHeaderSite)
admin.site.register(Admin_HeaderMenu, AdminHeaderMenuSite)
admin.site.register(Admin_HeaderSubMenu, AdminHeaderSubMenuSite)
admin.site.register(Manage_Menu)
admin.site.register(ManageMenuMasterProducts)
admin.site.register(ExhibitionOffers)
admin.site.register(ExhibitionOffersCategory)

