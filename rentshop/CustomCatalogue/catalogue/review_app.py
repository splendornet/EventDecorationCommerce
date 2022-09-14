# django imports
from django.conf import settings

# 3rd party imports
from oscar.core.loading import get_class
from oscar.apps.catalogue.reviews.app import ProductReviewsApplication as CoreProductReviewsApplication


class ProductReviewsApplication(CoreProductReviewsApplication):

    """
    Product review oscar extended app.
    """

    create_view = get_class('catalogue.views', 'CustomCreateProductReview')


# app registered.
review_appication = ProductReviewsApplication()
