from oscar.apps.promotions.app import PromotionsApplication as CorePromotionsApplication
from oscar.core.loading import get_class, get_model


class PromotionsApplication(CorePromotionsApplication):
    home_view = get_class('promotions.views', 'CustomHomeView')


application = PromotionsApplication()