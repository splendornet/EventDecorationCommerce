# django imports
from django.conf.urls import url

# 3rd party imports
from oscar.core.application import Application
from oscar.core.loading import get_class
from oscar.apps.catalogue.app import BaseCatalogueApplication as CoreBaseCatalogueApplication
from oscar.apps.catalogue.app import ReviewsApplication as CoreReviewsApplication


class BaseCatalogueApplication(CoreBaseCatalogueApplication):

    """
    Oscar catalogue extended methods routers.
    """

    name = 'catalogue'
    catalogue_view = get_class('catalogue.views', 'CustomCatalogueView')
    detail_view = get_class('catalogue.views', 'CustomProductDetailView')
    category_view = get_class('catalogue.views', 'CustomNewCatalogueView')
    wedding_venue = get_class('catalogue.views','ProductWeddingVenueView')
    category_product_view = get_class('catalogue.views','CategoryWiseProductView')
    header_category_product_view = get_class('catalogue.views','HeaderCategoryProductView')
    get_sub_categories = get_class('catalogue.views','GetSubCategoriesView')
    get_menu = get_class('catalogue.views','MenuView')
    header_category_manage_product_view = get_class('catalogue.views','ManageHeaderCategoryProductView')
    all_manage_offer_product = get_class('catalogue.views','MenuOfferProductView')
    header_get_best_quote = get_class('catalogue.views','GetBestQuoteView')
    form_best_quote = get_class('catalogue.views','GetBestQuoteCreateView')



    def get_urls(self):
        urlpatterns = super(BaseCatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^wedding_venue$', self.wedding_venue.as_view(), name='wedding_venue'),
            url(r'^category_product/(?P<pk>\d+)/$', self.category_product_view.as_view(), name='category_product'),
            url(r'^get_subcategory/(?P<pk>\d+)/$', self.get_sub_categories.as_view(), name='get_subcategory'),
            url(r'^header_category_product/(?P<pk>\d+)/$', self.header_category_product_view.as_view(), name='header_category_product'),
            url(r'^menu/$', self.get_menu.as_view(), name='menu'),
            url(r'^header_category_manage_product/(?P<pk>\d+)/$', self.header_category_manage_product_view.as_view(),
                name='header_category_manage_product'),
            url(r'^all_manage_offer_product/(?P<pk>\d+)/$', self.all_manage_offer_product.as_view(),
                name='all_manage_offer_product'),
            url(r'^header_get_best_quote/(?P<pk>\d+)/$', self.header_get_best_quote.as_view(),
                name='header_get_best_quote'),
            url(r'^form_best_quote/$', self.form_best_quote.as_view(),
                name='form_best_quote'),

        ]
        return self.post_process_urls(urlpatterns)


class ReviewsApplication(CoreReviewsApplication):

    """
    Oscar reviews extended methods routers.
    """

    name = None
    reviews_app = get_class('catalogue.review_app', 'review_appication')


class CatalogueApplication(BaseCatalogueApplication, ReviewsApplication):

    """
    Combined routers extended classes.
    """

    pass


# register the rounter class
application = CatalogueApplication()
