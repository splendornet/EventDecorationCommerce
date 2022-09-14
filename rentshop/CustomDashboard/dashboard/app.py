from oscar.apps.dashboard.app import DashboardApplication as CoreDashboardApplication
from .views import IndexViewCustom
from oscar.core.loading import get_class
from django.conf.urls import url

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

CustomAuthenticationForm = get_class('dashboard.forms', 'CustomAuthenticationForm')


class DashboardApplication(CoreDashboardApplication):

    name = 'dashboard'

    index_view = get_class('dashboard.views', 'IndexViewCustom')
    catalogue_app = get_class('dashboard.catalogue_app', 'application')
    orders_app = get_class('dashboard.catalogue_app', 'order_application')
    reports_app = get_class('dashboard.catalogue_app', 'report_application')
    partners_app = get_class('dashboard.catalogue_app', 'partner_application')
    users_app = get_class('dashboard.catalogue_app', 'user_application')
    ranges_app = get_class('dashboard.catalogue_app', 'range_application')
    vouchers_app = get_class('dashboard.catalogue_app', 'voucher_application')
    reviews_app = get_class('dashboard.catalogue_app', 'review_application')
    accounts_app = get_class('dashboard.catalogue_app', 'accounts_application')
    sales_application = get_class('dashboard.catalogue_app', 'sales_application')
    def get_urls(self):

        urls = [
            url(r'accounts/', self.accounts_app.urls),
            url(r'sales-team/', self.sales_application.urls),
            url(r'^login/$', auth_views.login, {
                'template_name': 'dashboard/login.html',
                'authentication_form': CustomAuthenticationForm,
            }, name='login'),
        ]

        urls = urls + super(DashboardApplication, self).get_urls()

        return urls


application = DashboardApplication()