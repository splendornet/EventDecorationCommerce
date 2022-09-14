# python imports
import datetime
from decimal import Decimal as D

# django imports
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages

# 3rd party imports
from oscar.apps.order.signals import order_placed
from oscar.core.loading import get_model, get_class
from oscar.core.compat import get_user_model

# internal imports
from . import exceptions

get_product_price = get_class('basket.bind', 'get_product_price')
get_product_shipping = get_class('basket.bind', 'get_product_shipping')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
CustomBillingAddress = get_model('order', 'CustomBillingAddress')
OrderDiscount = get_model('order', 'OrderDiscount')
StockRecord = get_model('partner', 'StockRecord')
Product = get_model('catalogue', 'Product')
StockAlert = get_model('partner', 'StockAlert')
User = get_user_model()
CustomizeCouponModel = get_model('offer', 'CustomizeCouponModel')


class OrderNumberGenerator(object):

    """
    Simple object for generating order numbers.

    We need this as the order number is often required for payment
    which takes place before the order model has been created.
    """

    def order_number(self, basket):
        """
        Return an order number for a given basket
        """
        return 100000 + basket.id


class OrderCreator(object):

    """
    Places the order by writing out the various models
    """

    def place_order(self, basket, total,  # noqa (too complex (12))
                    shipping_method, shipping_charge, user=None,
                    shipping_address=None, billing_address=None,
                    order_number=None, status=None, request=None, **kwargs):
        """
        Placing an order involves creating all the relevant models based on the
        basket and session data.
        """

        if basket.is_empty:
            raise ValueError(_("Empty baskets cannot be submitted"))
        if not order_number:
            generator = OrderNumberGenerator()
            order_number = generator.order_number(basket)
        if not status and hasattr(settings, 'OSCAR_INITIAL_ORDER_STATUS'):
            status = getattr(settings, 'OSCAR_INITIAL_ORDER_STATUS')

        if Order._default_manager.filter(number=order_number).exists():
            raise ValueError(_("There is already an order with number %s")
                             % order_number)

        print('------------------------------------------')
        print(user)
        print(basket)
        print(total)
        print(order_number)
        print('------------------------------------------')

        with transaction.atomic():

            # Ok - everything seems to be in order, let's place the order
            order = self.create_order_model(
                user, basket, shipping_address, shipping_method, shipping_charge,
                billing_address, total, order_number, status, request, **kwargs)
            for line in basket.all_lines():
                self.create_line_models(order, line)
                self.update_stock_records(line)

            for voucher in basket.vouchers.select_for_update():
                available_to_user, msg = voucher.is_available_to_user(user=user)
                if not voucher.is_active() or not available_to_user:
                    # messages.error("voucher is not active now")
                    print('here@@##')
                    continue
                    raise ValueError(msg)

            # Record any discounts associated with this order
            for application in basket.offer_applications:
                # Trigger any deferred benefits from offers and capture the
                # resulting message
                application['message'] \
                    = application['offer'].apply_deferred_benefit(basket, order,
                                                                  application)
                # Record offer application results
                if application['result'].affects_shipping:
                    # Skip zero shipping discounts
                    shipping_discount = shipping_method.discount(basket)
                    if shipping_discount <= D('0.00'):
                        continue
                    # If a shipping offer, we need to grab the actual discount off
                    # the shipping method instance, which should be wrapped in an
                    # OfferDiscount instance.
                    application['discount'] = shipping_discount
                self.create_discount_model(order, application)
                self.record_discount(application)

            for voucher in basket.vouchers.all():
                if voucher.benefit.range.coupon_distibutor:
                    all_lines = basket.all_lines()
                    for line in all_lines:
                        c_obj = CustomizeCouponModel.objects.filter(category=line.product.categories.all().last(),
                                                            voucher=voucher)
                        if c_obj.last().used_coupon_count:
                            CustomizeCouponModel.objects.filter(category=line.product.categories.all().last(),
                                                                voucher=voucher).update(used_coupon_count=F('used_coupon_count') + 1)
                        else:
                            CustomizeCouponModel.objects.filter(category=line.product.categories.all().last(),
                                                                voucher=voucher).update(
                                used_coupon_count= 1)
                        print('updated cnt')
                self.record_voucher_usage(order, voucher, user)

        # Send signal for analytics to pick up
        order_placed.send(sender=self, order=order, user=user)

        return order

    def create_order_model(self, user, basket, shipping_address, shipping_method, shipping_charge, billing_address, total, order_number, status, request=None, **extra_order_fields):

        """
        Method to create order record.
        :param user:
        :param basket:
        :param shipping_address:
        :param shipping_method:
        :param shipping_charge:
        :param billing_address:
        :param total:
        :param order_number:
        :param status:
        :param request:
        :param extra_order_fields:
        :return:
        """

        total_incl_tax = None
        sum_total, advance_payment_amount, balance_amount = 0, 0, 0
        order_margin_price = 0

        for line_obj in basket.all_lines():

            unit_price = line_obj.unit_price_excl_tax
            qty = line_obj.quantity
            tax_amount = line_obj.tax_percentage

            booking_days, rent_shipping, sale_shipping = 1, 0, 0

            if line_obj.order_type == 'Sale':

                sale_price = get_product_price(line_obj.stockrecord, 'Sale', line_obj.quantity, 1, line_obj.flower_type, line_obj.is_package_product)
                order_margin_price = order_margin_price + sale_price * (line_obj.stockrecord.product.product_margin / 100)
                _sale_shipping = get_product_shipping(line_obj.stockrecord, 'Sale', line_obj.quantity,1, line_obj.flower_type, line_obj.is_package_product)

                if _sale_shipping:
                    sale_shipping = _sale_shipping

                if line_obj.product.product_cost_type != 'Multiple':
                    total_incl_tax = sale_price * line_obj.quantity + sale_shipping
                else:
                    total_incl_tax = sale_price * line_obj.quantity + sale_shipping

            elif line_obj.order_type == 'Rent':

                start_date = line_obj.booking_start_date
                end_date = line_obj.booking_end_date

                total_days = end_date - start_date
                booking_days = total_days.days + 1

                rent_price = get_product_price(line_obj.stockrecord, 'Rent', line_obj.quantity, booking_days, line_obj.flower_type, line_obj.is_package_product)
                order_margin_price = order_margin_price + rent_price * (line_obj.stockrecord.product.product_margin / 100)
                _rent_shipping = get_product_shipping(line_obj.stockrecord, 'Rent', line_obj.quantity, booking_days,  line_obj.flower_type, line_obj.is_package_product)

                if _rent_shipping:
                    rent_shipping = _rent_shipping

                if line_obj.product.product_cost_type != 'Multiple':
                    total_incl_tax = rent_price * booking_days * line_obj.quantity + rent_shipping
                else:
                    total_incl_tax = rent_price * booking_days * line_obj.quantity + rent_shipping

            elif line_obj.order_type == 'Professional':

                start_date = line_obj.booking_start_date
                end_date = line_obj.booking_end_date
                total_days = end_date - start_date
                booking_days = total_days.days + 1

                professional_price = get_product_price(line_obj.stockrecord, 'Rent', line_obj.quantity, booking_days, line_obj.flower_type, line_obj.is_package_product)
                order_margin_price = order_margin_price + professional_price * (line_obj.stockrecord.product.product_margin / 100)
                _rent_shipping = get_product_shipping(line_obj.stockrecord, 'Rent', line_obj.quantity, booking_days,  line_obj.flower_type, line_obj.is_package_product)

                if _rent_shipping:
                    rent_shipping = _rent_shipping

                if line_obj.product.product_cost_type != 'Multiple':
                    total_incl_tax = professional_price * booking_days * line_obj.quantity + rent_shipping
                else:
                    total_incl_tax = professional_price * booking_days * line_obj.quantity + rent_shipping

            else:
                total_incl_tax=0
            if not line_obj.is_package_product:
                sum_total += total_incl_tax

        advance_payment_amount = basket.advance_payment_price
        balance_amount = basket.balance_amount_price

        if advance_payment_amount:
            order_type = 'partial'
        else:
            order_type = 'full'

        user_billing_id, user_billing_address = None, None

        billing_address_record = CustomBillingAddress.objects.filter(user=user)

        if billing_address_record:
            user_billing_address = billing_address_record.last()
            user_billing_id = billing_address_record.last().id


        order_data = {
            'basket': basket, 'number': order_number,
            'currency': total.currency,
            'total_incl_tax': sum_total,
            'total_excl_tax': sum_total,
            'shipping_incl_tax': shipping_charge.incl_tax,
            'shipping_excl_tax': shipping_charge.excl_tax,
            'shipping_method': shipping_method.name,
            'shipping_code': shipping_method.code,
            'total_amount_incl_tax': sum_total,
            'paid_amount': basket.payable_amount,
            'total_deposit_amount': basket.cart_deposit,
            'advance_payment_amount': advance_payment_amount,
            'balance_amount': balance_amount,
            'order_margin_price': order_margin_price,
            'user_billing_address': user_billing_address,
            'user_billing_id': user_billing_id,
            'order_type' : order_type,
        }

        if shipping_address:
            order_data['shipping_address'] = shipping_address
        if billing_address:
            order_data['billing_address'] = billing_address
        if user and user.is_authenticated:
            order_data['user_id'] = user.id
        if status:
            order_data['status'] = status
        if extra_order_fields:
            order_data.update(extra_order_fields)
        if 'site' not in order_data:
            order_data['site'] = Site._default_manager.get_current(request)

        order = Order(**order_data)
        order.save()

        return order

    def create_line_models(self, order, basket_line, extra_line_fields=None):

        """
        Create the batch line model.

        You can set extra fields by passing a dictionary as the
        extra_line_fields value
        """

        product = basket_line.product
        stockrecord = basket_line.stockrecord

        if not stockrecord:
            raise exceptions.UnableToPlaceOrder("Basket line #%d has no stockrecord" % basket_line.id)

        tax_percentage = stockrecord.tax_percentage
        
        if product.product_class.name == 'Rent Or Sale' and basket_line.order_type == 'Sale':
            tax_percentage = stockrecord.sale_tax_percentage

        partner = stockrecord.partner

        booking_days, shipping_charges = 1, 0
        product_unit_price, product_margin_price = 0, 0

        try:
            if not basket_line.order_type == 'Sale':
                start_date = basket_line.booking_start_date
                end_date = basket_line.booking_end_date
                total_days = end_date - start_date
                booking_days = total_days.days + 1
            else:
                booking_days = 1
        except Exception as e:

            booking_days = 1

        if basket_line.order_type == 'Sale':

            sale_price = get_product_price(basket_line.stockrecord, 'Sale', basket_line.quantity, 1,  basket_line.flower_type, basket_line.is_package_product)
            product_margin_price = sale_price * (product.product_margin/100)
            _sale_shipping = get_product_shipping(basket_line.stockrecord, 'Sale', basket_line.quantity, 1, basket_line.flower_type, basket_line.is_package_product)

            if _sale_shipping:
                shipping_charges = _sale_shipping

            product_unit_price = sale_price
            if basket_line.product.product_cost_type != 'Multiple':
                total_price_incl_tax = sale_price * basket_line.quantity
            else:
                total_price_incl_tax = sale_price * basket_line.quantity

        elif basket_line.order_type == 'Rent':

            rent_price = get_product_price(basket_line.stockrecord, 'Rent', basket_line.quantity, booking_days, basket_line.flower_type, basket_line.is_package_product)
            product_margin_price = rent_price * (product.product_margin / 100)
            _rent_shipping = get_product_shipping(basket_line.stockrecord, 'Rent', basket_line.quantity, booking_days, basket_line.flower_type, basket_line.is_package_product)

            if _rent_shipping:
                shipping_charges = _rent_shipping

            product_unit_price = rent_price
            if basket_line.product.product_cost_type != 'Multiple':
                total_price_incl_tax = rent_price * booking_days * basket_line.quantity
            else:
                total_price_incl_tax = rent_price * booking_days * basket_line.quantity

        elif basket_line.order_type == 'Professional':

            pro_price = get_product_price(basket_line.stockrecord, 'Rent', basket_line.quantity, booking_days, basket_line.flower_type, basket_line.is_package_product)
            product_margin_price = pro_price * (product.product_margin / 100)
            _rent_shipping = get_product_shipping(basket_line.stockrecord, 'Rent', basket_line.quantity, booking_days, basket_line.flower_type, basket_line.is_package_product)

            if _rent_shipping:
                shipping_charges = _rent_shipping

            product_unit_price = pro_price
            if basket_line.product.product_cost_type != 'Multiple':
                total_price_incl_tax = pro_price * booking_days * basket_line.quantity
            else:
                total_price_incl_tax = pro_price * booking_days * basket_line.quantity
        else:
            total_price_incl_tax = basket_line.unit_price_excl_tax
            product_unit_price = basket_line.unit_price_excl_tax

        if basket_line.order_type == 'Sale' and basket_line.product.product_class.name == 'Rent Or Sale':
            advance_payment_percentage = stockrecord.sale_advance_payment_percentage
        else:
            advance_payment_percentage = stockrecord.advance_payment_percentage

        line_data = {
            'order': order,

            # Partner details
            'partner': partner,
            'partner_name': partner.name,
            'partner_sku': stockrecord.partner_sku,
            'stockrecord': stockrecord,

            # Product details
            'product': product,
            'title': product.get_title(),
            'upc': product.upc,
            'quantity': basket_line.quantity,

            # Price details
            'line_price_excl_tax': total_price_incl_tax,
            'line_price_incl_tax': total_price_incl_tax,
            'line_price_before_discounts_excl_tax': basket_line.line_price_excl_tax,
            'line_price_before_discounts_incl_tax': basket_line.line_price_incl_tax,

            # Reporting details
            'unit_cost_price': product_unit_price,
            'unit_price_incl_tax': product_unit_price,
            'unit_price_excl_tax': product_unit_price,
            'unit_retail_price': product_unit_price,

            # Shipping details
            'est_dispatch_date': basket_line.purchase_info.availability.dispatch_date,
            'advance_payment_percentage': advance_payment_percentage,
            'minimum_qty': stockrecord.minimum_qty,
            'tax_percentage': tax_percentage,
            'shipping_charges': shipping_charges,
            'rent_price': stockrecord.rent_price,
            'order_type': basket_line.order_type,
            'booking_start_date': basket_line.booking_start_date,
            'booking_end_date': basket_line.booking_end_date,
            'total_amount_incl_tax': total_price_incl_tax,

            'product_margin_percentage': product.product_margin,
            'product_margin_price': product_margin_price,
            'is_line_package_product': basket_line.is_package_product

        }

        extra_line_fields = extra_line_fields or {}
        if hasattr(settings, 'OSCAR_INITIAL_LINE_STATUS'):
            if not (extra_line_fields and 'status' in extra_line_fields):
                extra_line_fields['status'] = getattr(
                    settings, 'OSCAR_INITIAL_LINE_STATUS')
        if extra_line_fields:
            line_data.update(extra_line_fields)

        order_line = Line._default_manager.create(**line_data)
        self.create_line_price_models(order, order_line, basket_line)
        self.create_line_attributes(order, order_line, basket_line)
        self.create_additional_line_models(order, order_line, basket_line)

        return order_line

    def update_stock_records(self, line):
        try:
            line_obj = line.product.id

            if line.product.get_product_class().track_stock:

                line.stockrecord.allocate(line.quantity)

                stock_record = StockRecord.objects.filter(product_id__in=[line_obj])
                stock_record_ids = StockRecord.objects.filter(product_id__in=[line_obj]).values_list('id', flat=True)

                net_stock = 0
                total_stock = 0
                allocated = 0
                threshold = 0
                vendor_email = None
                product_name = None
                for i in stock_record:
                    total_stock = i.num_in_stock
                    allocated = i.num_allocated
                    threshold = i.low_stock_threshold
                    vendor_email= i.partner.email_id
                    product_name = i.product

                net_stock = total_stock - allocated
                stock_alter_time = StockAlert.objects.filter(stockrecord_id__in=stock_record_ids, status='Open')

                stock_alert_data = None
                for x in stock_alter_time:
                    stock_alert_data = x.date_created


                stock_date = stock_alert_data
                current_date = datetime.datetime.utcnow()
                stock_date_truncated = datetime.datetime(stock_date.year, stock_date.month, stock_date.day, stock_date.hour, stock_date.minute)
                current_date_truncated = datetime.datetime(current_date.year, current_date.month, current_date.day, current_date.hour, current_date.minute)

                admin_email_list = []
                admin_list = User.objects.filter(is_superuser=True, is_staff=True).values_list('email', flat=True)
                for i in admin_list:
                    admin_email_list += [i]

                if stock_date_truncated == current_date_truncated:
                    mail_subject = 'Low stock alert %s' % (product_name)
                    message = render_to_string('customer/emails/product_low_stock_alert_email.html',
                                               {'product': product_name, 'net_stock': net_stock, 'threshold': threshold})

                    from_email = settings.FROM_EMAIL_ADDRESS
                    to_email = [vendor_email]
                    email_admin = EmailMessage(mail_subject, message, from_email, to_email, bcc=admin_email_list)
                    email_admin.content_subtype = "html"
                    email_admin.send()
                else:
                    pass
        except:
            line.stockrecord.allocate(line.quantity)


    def create_additional_line_models(self, order, order_line, basket_line):
        """
        Empty method designed to be overridden.

        Some applications require additional information about lines, this
        method provides a clean place to create additional models that
        relate to a given line.
        """
        pass

    def create_line_price_models(self, order, order_line, basket_line):
        """
        Creates the batch line price models
        """
        breakdown = basket_line.get_price_breakdown()
        for price_incl_tax, price_excl_tax, quantity in breakdown:
            order_line.prices.create(
                order=order,
                quantity=quantity,
                price_incl_tax=price_incl_tax,
                price_excl_tax=price_excl_tax)

    def create_line_attributes(self, order, order_line, basket_line):
        """
        Creates the batch line attributes.
        """
        for attr in basket_line.attributes.all():
            order_line.attributes.create(
                option=attr.option,
                type=attr.option.code,
                value=attr.value)

    def create_discount_model(self, order, discount):

        """
        Create an order discount model for each offer application attached to
        the basket.
        """
        order_discount = OrderDiscount(
            order=order,
            message=discount['message'] or '',
            offer_id=discount['offer'].id,
            frequency=discount['freq'],
            amount=discount['discount'])
        result = discount['result']
        if result.affects_shipping:
            order_discount.category = OrderDiscount.SHIPPING
        elif result.affects_post_order:
            order_discount.category = OrderDiscount.DEFERRED
        voucher = discount.get('voucher', None)
        if voucher:
            order_discount.voucher_id = voucher.id
            order_discount.voucher_code = voucher.code
        order_discount.save()

    def record_discount(self, discount):
        discount['offer'].record_usage(discount)
        if 'voucher' in discount and discount['voucher']:
            discount['voucher'].record_discount(discount)

    def record_voucher_usage(self, order, voucher, user):
        """
        Updates the models that care about this voucher.
        """
        voucher.record_usage(order, user)
