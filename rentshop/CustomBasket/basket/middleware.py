from django.conf import settings
from django.contrib import messages
from django.core.signing import BadSignature, Signer
from django.utils.functional import SimpleLazyObject, empty
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class, get_model
from oscar.apps.basket.middleware import BasketMiddleware

Applicator = get_class('offer.applicator', 'Applicator')
Basket = get_model('basket', 'basket')
Selector = get_class('partner.strategy', 'Selector')

selector = Selector()


class CustomBasketMiddleware(BasketMiddleware):

    def __call__(self, request):
        # Keep track of cookies that need to be deleted (which can only be done
        # when we're processing the response instance).
        request.cookies_to_delete = []

        # Load stock/price strategy and assign to request (it will later be
        # assigned to the basket too).
        strategy = selector.strategy(request=request, user=request.user)
        request.strategy = strategy

        # We lazily load the basket so use a private variable to hold the
        # cached instance.
        request._basket_cache = None

        def load_full_basket():
            """
            Return the basket after applying offers.
            """
            basket = self.get_basket(request)
            basket.strategy = request.strategy
            self.apply_offers_to_basket(request, basket)

            return basket

        def load_basket_hash():
            """
            Load the basket and return the basket hash

            Note that we don't apply offers or check that every line has a
            stockrecord here.
            """
            basket = self.get_basket(request)
            if basket.id:
                return self.get_basket_hash(basket.id)

        # Use Django's SimpleLazyObject to only perform the loading work
        # when the attribute is accessed.
        request.basket = SimpleLazyObject(load_full_basket)
        request.basket_hash = SimpleLazyObject(load_basket_hash)

        response = self.get_response(request)

        return self.process_response(request, response)

    # Helper methods

    def get_basket(self, request):
        """
        Return the open basket for this request
        """
        if request._basket_cache is not None:
            return request._basket_cache

        num_baskets_merged = 0
        manager = Basket.open
        cookie_key = self.get_cookie_key(request)
        cookie_basket = self.get_cookie_basket(cookie_key, request, manager)

        if hasattr(request, 'user') and request.user.is_authenticated:
            # Signed-in user: if they have a cookie basket too, it means
            # that they have just signed in and we need to merge their cookie
            # basket into their user basket, then delete the cookie.
            status = False
            if 'HTTP_REFERER' in request.META:
                status = True

            # if (status and "catalogue" in request.META['HTTP_REFERER']) or ("catalogue" in request.META['PATH_INFO']):
            #     basket = Basket.objects.filter(owner=request.user, status="Open").order_by('-date_created')
            #     if basket:
            #         return basket.first()
            if "basket" in request.META['PATH_INFO']:
                Basket.objects.filter(owner=request.user, status="Frozen").update(status='Open')

            if status and "basket" not in request.META['HTTP_REFERER'] and "checkout" in request.path:

                basket = Basket.objects.filter(owner=request.user, status="Frozen").order_by('-date_created')
                if basket:
                    return basket.first()
            try:
                basket, __ = manager.get_or_create(owner=request.user)

            except Basket.MultipleObjectsReturned:
                # Not sure quite how we end up here with multiple baskets.
                # We merge them and create a fresh one
                old_baskets = list(manager.filter(owner=request.user).order_by('-date_created'))
                basket = old_baskets[0]
                if "add-new" not in request.path:
                    for other_basket in old_baskets[1:]:
                        self.merge_baskets(basket, other_basket)
                        num_baskets_merged += 1

            # Assign user onto basket to prevent further SQL queries when
            # basket.owner is accessed.
            basket.owner = request.user

            if cookie_basket:
                self.merge_baskets(basket, cookie_basket)
                num_baskets_merged += 1
                request.cookies_to_delete.append(cookie_key)

        elif cookie_basket:
            # Anonymous user with a basket tied to the cookie
            basket = cookie_basket
        else:
            # Anonymous user with no basket - instantiate a new basket
            # instance.  No need to save yet.
            basket = Basket()

        # Cache basket instance for the during of this request
        request._basket_cache = basket

        if num_baskets_merged > 0:
            messages.add_message(request, messages.WARNING,
                                 _("We have merged a basket from a previous session. Its contents "
                                   "might have changed."))

        return basket

    def merge_baskets(self, master, slave):
        """
        Merge one basket into another.

        This is its own method to allow it to be overridden
        """
        master.merge(slave, add_quantities=True)