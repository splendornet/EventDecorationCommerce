# python imports
from decimal import Decimal as D

# django imports
from django.utils.translation import ugettext_lazy as _

# module imports
from oscar.apps.offer import benefits
from oscar.core.loading import get_class, get_classes, get_model
from oscar.templatetags.currency_filters import currency

# internal imports
Benefit = get_model('offer', 'Benefit')
BasketDiscount, SHIPPING_DISCOUNT, ZERO_DISCOUNT = get_classes('offer.results', ['BasketDiscount', 'SHIPPING_DISCOUNT', 'ZERO_DISCOUNT'])
CoverageCondition, ValueCondition = get_classes('offer.conditions', ['CoverageCondition', 'ValueCondition'])
range_anchor = get_class('offer.utils', 'range_anchor')
CustomizeCouponModel = get_model('offer', 'CustomizeCouponModel')
PriceRangeModel = get_model('offer', 'PriceRangeModel')

__all__ = ['PercentageDiscountBenefit', 'AbsoluteDiscountBenefit', 'FixedPriceBenefit', 'ShippingBenefit', 'MultibuyDiscountBenefit', 'ShippingAbsoluteDiscountBenefit', 'ShippingFixedPriceBenefit', 'ShippingPercentageDiscountBenefit',]


def apply_discount(line, discount, quantity, offer=None):

    """
    Apply a given discount to the passed basket
    :param line: cart
    :param discount: coupon
    :param quantity: 1
    :param offer: coupon session
    :return: discount
    """

    line.discount(discount, quantity, incl_tax=False, offer=offer)


class CustomPercentageDiscountBenefit(benefits.PercentageDiscountBenefit):

    """
    An offer benefit that gives a percentage discount
    """

    _description = _("%(value)s%% discount on %(range)s")

    @property
    def name(self):
        return self._description % {'value': self.value, 'range': self.range.name}

    @property
    def description(self):
        return self._description % {'value': self.value, 'range': range_anchor(self.range)}

    class Meta:
        app_label = 'offer'
        proxy = True
        verbose_name = _("Percentage discount benefit")
        verbose_name_plural = _("Percentage discount benefits")

    def apply(self, basket, condition, offer, discount_percent=None, max_total_discount=None):

        if discount_percent is None:
            discount_percent = self.value

        discount_amount_available = max_total_discount

        line_tuples = self.get_applicable_lines(offer, basket)
        discount_percent = min(discount_percent, D('100.0'))

        discount = D('0.00')

        affected_items = 0
        max_affected_items = self._effective_max_affected_items()
        affected_lines = []
        for price, line in line_tuples:
            result = self.check_voucher_available(offer,line)
            print('res',result)
            if not line.is_package_product and result:
                if affected_items >= max_affected_items:
                    break
                if discount_amount_available == 0:
                    break
                quantity_affected = min(
                    line.quantity_without_offer_discount(offer),
                    max_affected_items - affected_items)
                line_discount = self.round(discount_percent / D('100.0') * price
                                           * int(quantity_affected))
                if discount_amount_available is not None:
                    line_discount = min(line_discount, discount_amount_available)
                    discount_amount_available -= line_discount
                apply_discount(line, line_discount, quantity_affected, offer)

                affected_lines.append((line, line_discount, quantity_affected))
                affected_items += quantity_affected
                discount += line_discount

        print('dis',discount)
        if discount > 0:
            condition.consume_items(offer, basket, affected_lines)
        return BasketDiscount(discount)


    def check_voucher_available(self,offer, line):
        voucher = offer.get_voucher()
        cat_list = []
        status = True
        for category in voucher.benefit.range.included_categories.all():
            id_list = [obj for obj in category.get_descendants_and_self()]
            for element in id_list:
                cat_list.append(element)

        if not line.is_package_product and not line.product.categories.all().last() in cat_list:
            status = False
        print('stat',status)
        return status




from oscar.apps.offer import models
class CustomizeCouponDiscountBenefit(benefits.Benefit):

    """
    An offer benefit that gives a percentage discount
    """

    _description = _("%(value)s%% discount on %(range)s")

    @property
    def name(self):
        return self._description % {'value': self.value, 'range': self.range.name}

    @property
    def description(self):
        return self._description % {'value': self.value, 'range': range_anchor(self.range)}

    class Meta:
        app_label = 'offer'
        proxy = True
        verbose_name = _("Customize Coupon discount benefit")
        verbose_name_plural = _("Customize Coupon discount benefits")

    def apply(self, basket, condition, offer, discount_percent=None, max_total_discount=None):

        if discount_percent is None:
            discount_percent = self.value

        discount_amount_available = max_total_discount

        line_tuples = self.get_applicable_lines(offer, basket)
        discount_percent = min(discount_percent, D('100.0'))

        discount = D('0.00')

        affected_items = 0
        max_affected_items = self._effective_max_affected_items()
        affected_lines = []
        print("tuple", line_tuples)
        for price, line in line_tuples:
            #code for
            d_value, discount_type = self.get_discount_percent(basket,offer,line)
            if d_value:
                discount_percent = d_value

            if affected_items >= max_affected_items:
                break
            if discount_amount_available == 0:
                break

            quantity_affected = min(
                line.quantity_without_offer_discount(offer),
                max_affected_items - affected_items)

            if discount_type:
                if discount_type == "Percentage":

                    line_discount = self.round(discount_percent / D('100.0') * price
                                               * int(quantity_affected))
                    if discount_amount_available is not None:
                        line_discount = min(line_discount, discount_amount_available)
                        discount_amount_available -= line_discount
                elif discount_type == "Absolute":
                    line_discount = D('0.00')
                    value_affected = D('0.00')
                    value_affected = quantity_affected * price
                    if not value_affected < line_discount:
                        line_discount = discount_percent
                    else:
                        line_discount = D('0.00')
                    # discount = max(value_affected-line_discount, D('0.00'))

                apply_discount(line, line_discount, quantity_affected, offer)

                affected_lines.append((line, line_discount, quantity_affected))
                affected_items += quantity_affected
                discount += line_discount

        if discount > 0:
            condition.consume_items(offer, basket, affected_lines)
            # for aff in affected_lines:
            #     CustomizeCouponModel.objects.filter(category= aff.product.categories.all().last())
        return BasketDiscount(discount)

    def get_discount_percent(self, basket, offer, line):
        discount = 0

        if offer and not line.is_package_product:
            voucher = offer.get_voucher()
            cat_list = []
            for category in voucher.benefit.range.included_categories.all():
                id_list = [obj for obj in category.get_descendants_and_self()]
                for element in id_list:
                    cat_list.append(element)

            if line.product.categories.all().last() in cat_list:
                c_obj = CustomizeCouponModel.objects.filter(category=line.product.categories.all().last(),
                                                            voucher=voucher)
                from django.utils import timezone

                test_datetime = timezone.now()
                used_count = 0
                if c_obj.last().used_coupon_count:
                    used_count = c_obj.last().used_coupon_count
                balanced_count =  c_obj.last().coupon_count - used_count
                if c_obj and c_obj.last().start_datetime <= test_datetime <= c_obj.last().end_datetime and balanced_count > 0:
                    # lines = basket.all_lines()
                    # line_cat = []
                    # for l1 in lines:
                    #     if l1.product.categories.all().last() == line.product.categories.all().last() and not l1.is_package_product:
                    #         line_cat.append(l1)
                    # if line_cat:
                    #     price = 0
                    #     for l2 in line_cat:
                    #         price = price + (l2.bind_unit_price * l2.quantity)



                    choice = None

                    #
                    # elif line.bind_unit_price >= 10000 and line.bind_unit_price <= 25000:
                    #     choice = '10000-25000'
                    # elif line.bind_unit_price >= 7000 and line.bind_unit_price <= 10000:
                    #     choice = '7000-10000'
                    # elif line.bind_unit_price >= 5000 and line.bind_unit_price <= 7000:
                    #     choice = '5000-7000'
                    # elif line.bind_unit_price >= 2000 and line.bind_unit_price <= 5000:
                    #     choice = '2000-5000'
                    # elif line.bind_unit_price >= 1 and line.bind_unit_price <= 2000:
                    #     choice = '1-2000'
                    print('bind price',line.bind_unit_price)
                    if line.bind_unit_price >= 200000:
                        choice = '200000-1000000'
                    elif line.bind_unit_price >= 150000 and line.bind_unit_price <= 199999:
                        choice = '150000-199999'
                    elif line.bind_unit_price >= 100000 and line.bind_unit_price <= 149999:
                        choice = '100000-149999'
                    elif line.bind_unit_price >= 80000 and line.bind_unit_price <= 99999:
                        choice = '80000-99999'
                    elif line.bind_unit_price >= 75000 and line.bind_unit_price <= 99999:
                        choice = '75000-99999'
                    elif line.bind_unit_price >= 70000 and line.bind_unit_price <= 99999:
                        choice = '70000-99999'
                    elif line.bind_unit_price >= 50000 and line.bind_unit_price <= 79999:
                        choice = '50000-79999'
                    elif line.bind_unit_price >= 50000 and line.bind_unit_price <= 74999:
                        choice = '50000-74999'
                    elif line.bind_unit_price >= 30000 and line.bind_unit_price <= 69999:
                        choice = '30000-69999'
                    elif line.bind_unit_price >= 20000 and line.bind_unit_price <= 49999:
                        choice = '20000-49999'
                    elif line.bind_unit_price >= 15000 and line.bind_unit_price <= 49999:
                        choice = '15000-49999'

                    elif line.bind_unit_price >= 25000:
                        choice = '25000-1000000'
                    elif line.bind_unit_price >= 10000 and line.bind_unit_price <= 24999:
                        choice = '10000-24999'
                    elif line.bind_unit_price >= 7000 and line.bind_unit_price <= 9999:
                        choice = '7000-9999'
                    elif line.bind_unit_price >= 5000 and line.bind_unit_price <= 6999:
                        choice = '5000-6999'
                    elif line.bind_unit_price >= 2000 and line.bind_unit_price <= 4999:
                        choice = '2000-4999'
                    elif line.bind_unit_price <= 1999:
                        choice = '1-1999'
                    print('choice',choice)
                    
                    if choice:
                        p_obj = PriceRangeModel.objects.all()

                        p_obj1 = p_obj.filter(category=line.product.categories.all().last())
                        if p_obj1:
                            r_obj = p_obj.filter(category=line.product.categories.all().last(), price_rng = choice)
                            if r_obj:
                                discount = r_obj.last().discount
                                print("discount@@", discount, line)
                                return  (discount,r_obj.last().discount_type)
                            else:
                                discount = p_obj1.last().discount
                                print("discount@", discount, line)
                                return (discount, p_obj1.last().discount_type)

                        else:
                            p_obj = PriceRangeModel.objects.filter(category__in=line.product.get_ancestors_and_self())
                            if p_obj:
                                p_obj1 = PriceRangeModel.objects.filter(
                                    category__in=line.product.get_ancestors_and_self(), price_rng = choice)
                                if p_obj:
                                    discount = p_obj1.last().discount
                                    print("discount@", discount, line)
                                    return (discount, p_obj.last().discount_type)
                                else:
                                    discount = p_obj.last().discount
                                    print("discount@", discount, line)
                                    return (discount, p_obj.last().discount_type)
        print("discount", discount, line)

        return (discount,None)








