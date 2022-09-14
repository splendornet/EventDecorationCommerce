# python imports
from decimal import Decimal as D
from datetime import date, datetime, timedelta

# django imports
from django.db import models
from django.utils.translation import gettext as _

# 3rd party imports
from oscar.apps.basket.abstract_models import AbstractLine, AbstractBasket
from oscar.core.loading import get_model
from oscar.apps.partner.strategy import Selector

# internal imports
from .bind import *
StockRecord = get_model('partner', 'stockrecord')
Product = get_model('catalogue', 'Product')


class Line(AbstractLine):

    """
    Oscar extended cart line model.
    """

    advance_payment_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    minimum_qty = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    shipping_charges = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    rent_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    order_type = models.CharField(max_length=100, null=True, blank=True)
    booking_start_date = models.DateTimeField(blank=True, null=True)
    booking_end_date = models.DateTimeField(blank=True, null=True)
    product_attributes = models.TextField(blank=True,null = True)
    flower_type = models.CharField(max_length=100, null=True, blank=True)
    is_package_product = models.BooleanField(default = False)

    def discount(self, discount_value, affected_quantity, incl_tax=True, offer=None):

        """
        Apply a discount to this line.
        :param discount_value: discount value
        :param affected_quantity: cart lines
        :param incl_tax: apply on taxes flag
        :param offer: check for offers
        :return: discount value
        """

        if incl_tax:
            if self._discount_excl_tax > 0:
                raise RuntimeError(
                    "Attempting to discount the tax-inclusive price of a line "
                    "when tax-exclusive discounts are already applied"
                )
            self._discount_incl_tax += discount_value
        else:
            if self._discount_incl_tax > 0:
                raise RuntimeError(
                    "Attempting to discount the tax-exclusive price of a line "
                    "when tax-inclusive discounts are already applied"
                )
            self._discount_excl_tax += discount_value

        self.consume(affected_quantity, offer=offer)

    def consume(self, quantity, offer=None):

        """
        Method to consume quantity from stock.
        :param quantity: order quantity
        :param offer: check for offers
        :return: consume value
        """

        self.consumer.consume(quantity, offer=offer)

    def get_price_breakdown(self):

        """
        Get price.
        :return: price
        """

        if not self.is_tax_known:
            raise RuntimeError(
                "A price breakdown can only be determined when taxes are known"
            )
        prices = []
        if not self.discount_value:
            prices.append((self.unit_price_incl_tax, self.unit_price_excl_tax,
                           self.quantity))
        else:

            item_incl_tax_discount = (
                    self.discount_value / int(self.consumer.consumed()))
            item_excl_tax_discount = item_incl_tax_discount * self._tax_ratio
            item_excl_tax_discount = item_excl_tax_discount.quantize(D('0.01'))
            prices.append((self.unit_price_incl_tax - item_incl_tax_discount,
                           self.unit_price_excl_tax - item_excl_tax_discount,
                           self.consumer.consumed()))
            if self.quantity_without_discount:
                prices.append((self.unit_price_incl_tax,
                               self.unit_price_excl_tax,
                               self.quantity_without_discount))

        return prices

    def has_offer_discount(self, offer):

        """
        Check weather offer has discount.
        :param offer: offers
        :return: discount flag
        """

        return self.consumer.consumed(offer) > 0

    def quantity_with_offer_discount(self, offer):

        """
        Method to check quantity with offer.
        :param offer: offer
        :return: flag
        """

        return self.consumer.consumed(offer)

    def quantity_without_offer_discount(self, offer):

        """
        Method to check quantity without offer.
        :param offer: offer
        :return: flag
        """

        return self.consumer.available(offer)

    def is_available_for_offer_discount(self, offer):

        """
        Method to check offer is valid/available
        :param offer: offer
        :return: flag
        """

        return self.consumer.available(offer) > 0

    @property
    def discount_value(self):

        """
        Method to get discount value
        :return: discount value
        """
        try:
            return max(self._discount_incl_tax, self._discount_excl_tax)
        except Exception as e:
            pass
            return 0


    @property
    def line_price_excl_tax_incl_discounts(self):

        """
        Method to get price with tax discount
        :return: discount value
        """
        try:
            if self._discount_excl_tax and self.line_price_excl_tax is not None:

                return self.line_price_excl_tax - self._discount_excl_tax
            if self._discount_incl_tax and self.line_price_incl_tax is not None:

                return self.line_price_excl_tax \
                       - self._tax_ratio * self._discount_incl_tax
            return self.line_price_excl_tax
        except Exception as e:
            print(e.args)

    @property
    def unit_effective_price(self):

        """
        Method to get unit price eff.
        :return: price
        """
        try:
            if self.order_type == 'Sale':
                return self.pre_total * 1
            else:
                return self.price_excl_tax * self.booking_days
        except Exception as e:
            print(e.args)
            return 0

    @property
    def purchase_info(self):

        """
        Method to get purchase information.
        :return: information.
        """
        try:
            if not hasattr(self, '_info'):
                self._info = self.basket.strategy.fetch_for_line(
                    self, self.stockrecord)

            return self._info
        except Exception as e:
            print(e.args)
            return 0

    @property
    def unit_price_excl_tax(self):

        """
        Method to get unit price without tax.
        :return: price
        """
        try:
            return self.purchase_info.price.excl_tax
        except Exception as e:
            print(e.args)
            return 0

    @property
    def unit_price_incl_tax(self):

        """
        Method to get price with tax
        :return: price
        """
        try:
            return self.purchase_info.price.incl_tax
        except Exception as e:
            print(e.args)
            return 0

    @property
    def line_price_excl_tax(self):

        """
        Method to get cart line without tax.
        :return: line price
        """
        try:

            start_date = self.booking_start_date
            end_date = self.booking_end_date

            if start_date and end_date is not None:
                date_1 = start_date
                date_2 = end_date
                total_days = date_2 - date_1
                total_days = total_days

            final_amount = 0
            if self.unit_price_excl_tax is not None:
                if self.order_type == 'Sale':
                    total_price = self.quantity * self.unit_price_excl_tax
                    tax_amount = (total_price * self.tax_percentage) / 100
                    final_amount = D(self.advance_payment_calculation) + D(tax_amount)
                    return final_amount
                elif self.order_type == 'Rent':
                    total_price = self.quantity * self.unit_price_excl_tax
                    tax_amount = (total_price * self.tax_percentage) / 100
                    final_amount = D(self.advance_payment_calculation) + D(tax_amount)
                    return final_amount
                else:
                    return 0
            return final_amount
        except Exception as e:
            print(e.args)
            return 0

    @property
    def line_price_incl_tax(self):

        """
        Method to get line price with tax
        :return: line price.
        """
        try:
            if self.unit_price_incl_tax is not None:
                if self.order_type == 'Sale':
                    total_price = self.pre_total
                    tax_amount = (total_price * self.tax_percentage) / 100
                    final_amount = D(self.advance_payment_calculation) + D(0)
                    return final_amount
                elif self.order_type == 'Rent':
                    total_price = self.pre_total
                    tax_amount = (total_price * self.tax_percentage) / 100
                    final_amount = D(self.advance_payment_calculation) + D(0)
                    return final_amount
                elif self.order_type == 'Professional':
                    total_price = self.pre_total
                    tax_amount = (total_price * self.tax_percentage) / 100
                    final_amount = D(self.advance_payment_calculation) + D(0)
                    return final_amount
                else:
                    return 0
        except Exception as e:
            print(e.args)
            return 0

    @property
    def line_price_incl_discount(self):

        """
        Method to get line price with discount
        :return: line price
        """
        try:
            if self.discount_value:
                if self.order_type == 'Sale':

                    total_price_with_discount = self.pre_total - self.discount_value
                    tax_amount = (total_price_with_discount * self.tax_percentage) / 100
                    total_price_with_discount = total_price_with_discount + tax_amount
                    return total_price_with_discount
                elif self.order_type == 'Rent':

                    total_price = self.pre_total - self.discount_value
                    tax_amount = (total_price * self.tax_percentage) / 100
                    final_amount = total_price + tax_amount
                    return final_amount
                elif self.order_type == 'Professional':

                    total_price = self.pre_total - self.discount_value
                    tax_amount = (total_price * self.tax_percentage) / 100
                    final_amount = total_price + tax_amount
                    return final_amount
                else:
                    return 0
        except Exception as e:
            print(e.args)
            return 0

    @property
    def booking_days(self):

        """
        Model propery to retrun booking days.
        :return: days
        """
        try:
            start_date = self.booking_start_date
            end_date = self.booking_end_date

            if start_date and end_date is not None:
                date_1 = start_date
                date_2 = end_date
                total_days = date_2 - date_1
                total_booking_days = total_days.days + 1
                if total_booking_days == 0:
                    return 1
                else:
                    return total_booking_days
        except Exception as e:
            print(e.args)
            return 0

    @property
    def bind_unit_price(self):

        try:
            price_obj = self.product.stockrecords.all()
            price = price_obj.last()

            if self.order_type in ['Rent', 'Professional']:
                rent_price = get_product_price(price, 'Rent', self.quantity, self.booking_days, self.flower_type, self.is_package_product)
                return rent_price

            if self.order_type == 'Sale':
                sale_price = get_product_price(price, 'Sale', self.quantity, 1,self.flower_type, self.is_package_product)
                return sale_price

            return 0
        except Exception as e:
            print(e.args)
            return 0

    @property
    def pre_total(self):

        """
        Model property to return pre total
        :return: pre-total.
        """
        try:
            if self.is_package_product:
                return 0

            rent_shipping, sale_shipping = 0, 0

            start_date = self.booking_start_date
            end_date = self.booking_end_date

            price_obj = self.product.stockrecords.all()
            price = price_obj.last()

            if self.product.product_cost_type != 'Multiple':

                if self.order_type in ['Rent', 'Professional']:

                    total_days_obj = end_date - start_date
                    total_days = total_days_obj.days + 1

                    rent_price = get_product_price(price, 'Rent', self.quantity, self.booking_days, self.flower_type, self.is_package_product)
                    _rent_shipping = get_product_shipping(price, 'Rent', self.quantity, total_days, self.flower_type, self.is_package_product)

                    if _rent_shipping:
                        rent_shipping = _rent_shipping
                    # return round(rent_price * total_days * self.quantity + rent_shipping)
                    return round(rent_price * total_days * self.quantity)

                if self.order_type == 'Sale':

                    sale_price = get_product_price(price, 'Sale', self.quantity, 1, self.flower_type, self.is_package_product)
                    _sale_shipping = get_product_shipping(price, 'Sale', self.quantity, 1, self.flower_type, self.is_package_product)

                    if _sale_shipping:
                        sale_shipping = _sale_shipping
                    # return round(sale_price * self.quantity + sale_shipping)
                    return round(sale_price * self.quantity)
            else:
                if self.order_type in ['Rent', 'Professional']:

                    total_days_obj = end_date - start_date
                    total_days = total_days_obj.days + 1

                    rent_price = get_product_price(price, 'Rent', self.quantity, self.booking_days, self.flower_type, self.is_package_product)
                    _rent_shipping = get_product_shipping(price, 'Rent', self.quantity, total_days,self.flower_type, self.is_package_product)
                    print('rent ship', _rent_shipping)
                    if _rent_shipping:
                        rent_shipping = _rent_shipping
                    # return round(rent_price * total_days * self.quantity + rent_shipping)
                    return round(rent_price * total_days * self.quantity)

                if self.order_type == 'Sale':

                    sale_price = get_product_price(price, 'Sale', self.quantity, 1, self.flower_type, self.is_package_product)
                    _sale_shipping = get_product_shipping(price, 'Sale', self.quantity, 1, self.flower_type, self.is_package_product)

                    if _sale_shipping:
                        sale_shipping = _sale_shipping

                    # return round(sale_price * self.quantity + sale_shipping)
                    return round(sale_price * self.quantity)

        except:
            pass
        return 0

    @property
    def get_shipping(self):

        """
        Model property to return pre total
        :return: pre-total.
        """
        try:
            rent_shipping, sale_shipping = 0, 0

            start_date = self.booking_start_date
            end_date = self.booking_end_date

            price_obj = self.product.stockrecords.all()
            price = price_obj.last()
            if self.order_type in ['Rent', 'Professional']:

                total_days_obj = end_date - start_date
                total_days = total_days_obj.days + 1

                # rent_price = get_product_price(price, 'Rent', self.quantity)
                _rent_shipping = get_product_shipping(price, 'Rent', self.quantity, total_days, self.flower_type, self.is_package_product)

                if _rent_shipping:
                    rent_shipping = _rent_shipping

                    return rent_shipping

            if self.order_type == 'Sale':

                _sale_shipping = get_product_shipping(price, 'Sale', self.quantity, 1, self.flower_type, self.is_package_product)

                if _sale_shipping:
                    sale_shipping = _sale_shipping
                return sale_shipping
        except:
            pass
        return 0

    @property
    def advance_payment_calculation(self):

        """
        Model property to calcuate advance payment.
        :return: ad. payment
        """
        try:

            if self.order_type == 'Sale':
                advance_percentage = self.purchase_info.price.advance_payment_percentage
            else:
                advance_percentage = self.purchase_info.price.advance_payment_percentage
            actual_price = self.pre_total
            if not advance_percentage:
                advance_percentage = 100
            advance_pay = (actual_price * advance_percentage) / 100 + self.get_shipping

            return advance_pay
        except Exception as e:
            print(e.args)
            return 0

    @property
    def total_incl_tax(self):

        """
        Model property to return total incl tax
        :return: total (incl tax)
        """
        try:
            return self._get_total('line_price_excl_tax')
        except Exception as e:
            print(e.args)
            return 0

    @property
    def pre_total_with_tax(self):

        try:
            tax_amount = (self.pre_total * self.tax_percentage) / 100
            tax_total = self.pre_total + tax_amount
            return tax_total
        except Exception as e:
            print(e.args)
            return 0

    @property
    def line_payable_amount(self):

        try:

            if self.order_type in ['Rent', 'Professional']:

                pre_total = self.pre_total
                tax_amount = (pre_total * self.tax_percentage) / 100
                advance_price = self.advance_payment_calculation
                payable_line_price = advance_price + tax_amount

                return payable_line_price

            elif self.order_type in ['Sale']:

                pre_total = self.pre_total
                tax_amount = (pre_total * self.tax_percentage) / 100
                advance_price = self.advance_payment_calculation
                payable_line_price = advance_price + tax_amount

                return payable_line_price

            else:

                return 0
        except Exception as e:
            print(e.args)
            return 0

    @property
    def patch_total(self):

        """
        Method to return total patch wise
        :return: total
        """
        try:
            if self.order_type in ['Rent', 'Professional']:

                pre_total = self.pre_total
                line_payable_amount = self.line_payable_amount
                patch_amount = self.pre_total_with_tax - line_payable_amount
                return patch_amount

            else:

                return 0
        except Exception as e:
            print(e.args)
            return 0


from oscar.core.loading import get_class
CustomOfferApplications = get_class('offer.results', 'CustomOfferApplications')


class Basket(AbstractBasket):

    """
    Oscar extended basket model
    """

    customized_basket = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Basket, self).__init__(*args, **kwargs)

        # We keep a cached copy of the basket lines as we refer to them often
        # within the same request cycle.  Also, applying offers will append
        # discount data to the basket lines which isn't persisted to the DB and
        # so we want to avoid reloading them as this would drop the discount
        # information.
        self._lines = None
        self.offer_applications = CustomOfferApplications()

    def __str__(self):
        return _(
            "%(status)s basket (owner: %(owner)s, lines: %(num_lines)d)") \
               % {'status': self.status,
                  'owner': self.owner,
                  'num_lines': self.num_lines}

    def add_product(self, product, quantity, order_type=None, booking_start_date=None, booking_end_date=None, product_attributes=None, options=None, flower_type = None):

        """
        Add product method
        :param product: product
        :param quantity: product qty
        :param order_type: order type
        :param options: default
        :return: objects
        """

        if options is None:
            options = []
        if not self.id:
            self.save()

        # Ensure that all lines are the same currency
        price_currency = self.currency
        stock_info = self.get_stock_info(product, options)
        if not stock_info.price.exists:
            raise ValueError("Strategy hasn't found a price for product %s" % product)

        if price_currency and stock_info.price.currency != price_currency:
            raise ValueError(("Basket lines must all have the same currency. Proposed line has currency %s, while basket has currency %s")% (stock_info.price.currency, price_currency))

        if stock_info.stockrecord is None:
            raise ValueError(("Basket lines must all have stock records. Strategy hasn't found any stock record for product %s") % product)

        line_ref = self._create_line_reference(product, stock_info.stockrecord, options)

        start_date, end_date = datetime.now(), datetime.now()
        product_price, product_rent_price = 0, 0
        # create product for sale
        if order_type == 'Sale':

            # set current date by default
            # start_date, end_date = datetime.now(), datetime.now()
            # start_date, end_date = datetime.now(), datetime.now()
            start_date = datetime.strptime(booking_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(booking_end_date, '%Y-%m-%d')

            product_price = get_product_price(stock_info.stockrecord, 'Sale', quantity,1,flower_type)
            product_rent_price = stock_info.price.rent_price

        if order_type in ['Rent', 'Professional']:
            if order_type == 'Rent':
                start_date = datetime.strptime(booking_start_date, '%Y-%m-%d')
                end_date = datetime.strptime(booking_end_date, '%Y-%m-%d')

            if order_type == 'Professional':
                start_date = datetime.strptime(booking_start_date, '%Y-%m-%d %I:%M %p')
                end_date = datetime.strptime(booking_end_date, '%Y-%m-%d %I:%M %p')

            total_days_obj = end_date - start_date
            total_days = total_days_obj.days + 1

            product_price = get_product_price(stock_info.stockrecord, 'Rent', quantity, total_days, flower_type)
            product_rent_price = product_price

        if order_type == 'Rent':
            start_date = booking_start_date
            end_date = booking_end_date

        if order_type == 'Professional':
            start_date = datetime.strptime(booking_start_date, '%Y-%m-%d %I:%M %p')
            end_date = datetime.strptime(booking_end_date, '%Y-%m-%d %I:%M %p')

        if order_type == 'Sale' and product.product_class.name =='Rent Or Sale':
            advance_payment_percentage = stock_info.stockrecord.sale_advance_payment_percentage
        else:
            advance_payment_percentage = stock_info.price.advance_payment_percentage


        defaults = {
            'quantity': quantity,
            'price_excl_tax': product_price,
            'price_currency': stock_info.price.currency,
            'advance_payment_percentage': advance_payment_percentage,
            'minimum_qty': stock_info.price.minimum_qty,
            'tax_percentage': stock_info.price.tax_percentage,
            'shipping_charges': stock_info.price.shipping_charges,
            'rent_price': product_rent_price,
            'order_type': order_type,
            'booking_start_date': start_date,
            'booking_end_date': end_date,
            'product_attributes': product_attributes,
            'flower_type' : flower_type
        }
        line, created = self.lines.get_or_create(
            line_reference=line_ref,
            product=product,
            stockrecord=stock_info.stockrecord,
            defaults=defaults
        )
        if created:
            for option_dict in options:
                line.attributes.create(option=option_dict['option'], value=option_dict['value'])
        else:
            line.quantity = max(0, line.quantity + quantity)
            line.save()
        self.reset_offer_applications()
        print('here', product.is_package )

        if product.is_package and product.product_package.all().count() > 0:
            print('here',product.product_package.all(),)
            line_obj = Line.objects.filter(basket=self, product__in=product.product_package.all())
            line_obj.delete()
            for prod in product.product_package.all():
                status = False
                prod_stockrecord = StockRecord.objects.get(product=prod)
                if prod.product_class.name in [ "Rent", "Professional"] and prod.is_approved == "Approved":
                    status = True
                elif prod.is_approved == "Approved":

                    if prod_stockrecord.num_in_stock and prod_stockrecord.num_allocated:
                        if prod_stockrecord.num_in_stock > prod_stockrecord.num_allocated:
                            status = True
                        else:
                            status = False
                    if prod_stockrecord.num_in_stock and not prod_stockrecord.num_allocated:
                        status = True
                print("status",status,prod)
                if status:
                    line_reference = self._create_line_reference(prod, stock_info.stockrecord, options)
                    prod_stockrecord = StockRecord.objects.get(product=prod)
                    prod_stock_info = StockRecord.objects.get(product=prod)
                    if not prod.product_class.name == 'Rent Or Sale':
                        if prod.product_class.name in ['Rent', 'Professional']:
                            order_type = 'Rent'
                        if prod.product_class.name == 'Sale':
                            order_type = 'Sale'

                    if order_type in ['Rent', 'Professional']:
                        product_price = get_product_price(prod_stock_info, 'Rent', quantity, total_days,
                                                          flower_type)
                    else:
                        product_price = get_product_price(prod_stock_info, 'Sale', quantity, total_days,
                                                          flower_type)
                    prod_product_rent_price = product_price
                    product_price1 = 0
                    Line.objects.create(
                        basket=self, line_reference=line_reference,
                        product=prod, stockrecord=prod_stockrecord,
                        quantity=1,
                        price_excl_tax=product_price1,
                        price_currency=prod_stock_info.price_currency,
                        advance_payment_percentage=prod_stock_info.advance_payment_percentage,
                        minimum_qty=prod_stock_info.minimum_qty, tax_percentage=prod_stock_info.tax_percentage,
                        shipping_charges=prod_stock_info.shipping_charges, rent_price=prod_product_rent_price,
                        order_type=order_type, booking_start_date=start_date, booking_end_date=end_date,
                        is_package_product=True
                    )

        return line, created


    add_product.alters_data = True
    add = add_product

    @property
    def advance_payment_price(self):

        """
        Method to calculate advance payment
        :return:
        """
        try:

            cost = 0

            cart_lines = self.all_lines()

            if not cart_lines:
                return 0
            for line in cart_lines:

                if line.order_type in ['Rent', 'Professional'] and line.stockrecord.advance_payment_percentage:
                    cost = cost + round((line.pre_total * (line.stockrecord.advance_payment_percentage/100)), 2) + line.get_shipping
                if line.order_type == 'Sale' and line.stockrecord.advance_payment_percentage:
                    if line.product.product_class.name == 'Rent Or Sale':
                        if line.stockrecord.sale_advance_payment_percentage:
                            cost = cost + round((line.pre_total * (line.stockrecord.sale_advance_payment_percentage / 100)), 2) + line.get_shipping
                    else:
                        cost = cost + round((line.pre_total * (line.stockrecord.advance_payment_percentage/100)), 2)  + line.get_shipping
            if cost:
                cost = cost +  self.cart_deposit
            print(cost)
            # if self.total_discount:
            #     cost = (self.cart_total_without_tax_for_discount * cost) / self.cart_total_without_tax

            return round(cost,0)
        except Exception as e:
            print(e.args)
            return 0

    @property
    def balance_amount_price(self):

        try:
            advance_price = self.advance_payment_price

            # cart_total = self.cart_total_without_tax
            cart_total = self.cart_total_without_tax

            balance_amount = cart_total - advance_price

            # if self.total_discount:
            #     balance_amount = self.cart_total_without_tax_for_discount - advance_price

            cost = 0

            cart_lines = self.all_lines()

            if not cart_lines:
                return 0
            for line in cart_lines:

                if line.order_type in ['Rent', 'Professional'] and line.stockrecord.advance_payment_percentage:
                    cost = cost + (line.pre_total -round((line.pre_total * (line.stockrecord.advance_payment_percentage / 100)),
                                        2))
                if line.order_type == 'Sale' and line.stockrecord.advance_payment_percentage:
                    if line.product.product_class.name == 'Rent Or Sale':
                        if line.stockrecord.sale_advance_payment_percentage:
                            cost = cost + (line.pre_total-round((line.pre_total * (line.stockrecord.sale_advance_payment_percentage / 100)),
                                                2) )
                    else:
                        cost = cost + (line.pre_total -round((line.pre_total * (line.stockrecord.advance_payment_percentage / 100)),
                                            2) )

            if self.total_discount:
                cost = cost - self.total_discount

            return round(cost,0)
        except Exception as e:
            print(e.args)
            return 0

    @property
    def cart_deposit(self):

        try:
            cost = 0

            cart_lines = self.all_lines()

            if not cart_lines:
                return 0

            for line in cart_lines:

                if line.order_type in ['Rent', 'Professional'] and line.product.deposite_amount and not line.is_package_product:
                    cost = cost + line.product.deposite_amount
            return cost
        except Exception as e:
            print(e.args)
            return 0

    @property
    def payable_amount(self):
        try:

            # final_amount = self.advance_payment_price + self.cart_deposit
            final_amount = self.advance_payment_price
            # final_amount = self.balance_amount_price
            discount = 0

            # if self.total_discount:
            #     discount = self.total_discount

            return round(final_amount - discount,0)
        except Exception as e:
            print(e.args)
            return 0

    @property
    def cart_total_with_tax(self):
        try:
            cart_total = 0
            cart_line = self.all_lines()
            if not cart_line:
                return 0

            for line in cart_line:

                cart_total = cart_total + line.pre_total_with_tax

            return cart_total
        except Exception as e:
            print(e.args)
            return 0

    @property
    def cart_total_without_tax(self):
        try:
            cart_total = 0

            cart_line = self.all_lines()
            if not cart_line:
                return 0

            for line in cart_line:
                cart_total = cart_total + line.pre_total + line.get_shipping

            return cart_total
        except Exception as e:
            print(e.args)
            return 0


    @property
    def cart_total_without_tax_for_discount(self):
        try:
            cart_total = 0

            cart_line = self.all_lines()
            if not cart_line:
                return 0

            for line in cart_line:
                cart_total = cart_total + line.pre_total

            if self.total_discount:
                discount = self.total_discount
                cart_total = cart_total - discount
            return cart_total
        except Exception as e:
            print(e.args)
            return 0


    @property
    def balance_amount(self):

        """
        Method to return balance amount
        :return: balance
        """
        try:
            balance_amount = 0
            cart_line = self.all_lines()
            if not cart_line:
                return 0

            for line in cart_line:
                balance_amount = balance_amount + line.patch_total
            return balance_amount
        except Exception as e:
            print(e.args)
            return 0

    @property
    def grouped_voucher_discounts(self):

        """
        Model to fetch grouped voucher discount
        :return: voucher
        """
        try:
            return self.offer_applications.grouped_voucher_discounts
        except Exception as e:
            print(e.args)
            return 0

    def clean_quantity(self):

        """
        Method to validate quantity
        :return: quantity
        """
        try:
            qty = self.cleaned_data['quantity']
            if qty > 0:
                self.check_max_allowed_quantity(qty)
                self.check_permission(qty)
            return qty
        except Exception as e:
            print(e.args)
            return 0

    @property
    def is_empty(self):

        """
        Test if this basket is empty
        :return: flag
        """
        try:
            return self.id is None or self.num_lines == 0
        except Exception as e:
            print(e.args)
            return 0

    @property
    def is_tax_known(self):

        """
        Test if tax values are known for this basket
        :return: tax
        """
        try:
            return all([line.is_tax_known for line in self.all_lines()])
        except Exception as e:
            print(e.args)
            return 0

    @property
    def total_excl_tax(self):

        """
        Return total line price excluding tax
        :return: total line price
        """
        try:
            return self._get_total('line_price_excl_tax_incl_discounts')
        except Exception as e:
            print(e.args)
            return 0

    @property
    def total_tax(self):

        """
        Return total tax for a line
        :return:  total tax
        """
        try:
            return self._get_total('line_tax')
        except Exception as e:
            print(e.args)
            return 0


    @property
    def total_incl_tax(self):

        """
        Return total price inclusive of tax and discounts
        :return: total incl tax
        """
        try:
            discount = 0
            total = self._get_total('line_price_incl_tax_incl_discounts')

            if self.total_discount:
                discount = self.total_discount

            return total
        except Exception as e:
            print(e.args)
            return 0

    @property
    def total_incl_tax_excl_discounts(self):

        """
        Return total price inclusive of tax but exclusive discounts
        :return: total excl discount
        """
        try:
            return self._get_total('line_price_incl_tax')
        except Exception as e:
            print(e.args)
            return 0

    @property
    def total_discount(self):

        """
        Return total discount
        :return: discount
        """
        try:
            return self._get_total('discount_value')
        except Exception as e:
            print(e.args)

    @property
    def offer_discounts(self):

        """
        Return basket discounts from non-voucher sources.  Does not include
        shipping discounts.
        :return: offer discount
        """
        try:
            return self.offer_applications.offer_discounts
        except Exception as e:
            print(e.args)
            return 0

    @property
    def voucher_discounts(self):

        """
        Return discounts from vouchers
        :return: discount voucher
        """
        try:
            return self.offer_applications.voucher_discounts
        except Exception as e:
            print(e.args)
            return 0

    @property
    def get_shipping_total(self):

        """
        Return discounts from vouchers
        :return: discount voucher
        """
        try:
            total = 0
            cart_line = self.all_lines()
            if not cart_line:
                return 0
            for line in cart_line:
                if not line.is_package_product:
                    total = total+ line.get_shipping
            return  total

            return 0
        except Exception as e:
            print(e.args)
            return 0


from oscar.apps.basket.models import *
# noqa isort:skip
