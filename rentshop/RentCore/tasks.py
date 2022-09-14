# packages import
import math
from celery import shared_task
from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_classes, get_model

# internal imports
from .email import send_email

User = get_user_model()
OrderAllocatedVendor = get_model('order', 'OrderAllocatedVendor')
Order = get_model('order', 'Order')
Product = get_model('catalogue', 'Product')
Partner = get_model('partner', 'Partner')


@shared_task
def check_cron():

    print('@@@@@@@@@@@@@@@@@@@ IN CRON @@@@@@@@@@@@@@@@@@@@@')

    from django.core.mail import send_mail
    import datetime

    send_mail(
        'TRP : CRON Test',
        'Cron hit at %s' % (str(datetime.datetime.now())),
        'from@example.com',
        ['rmtest08@gmail.com'],
        fail_silently=False,
    )


@shared_task
def trigger_email(**data):

    """
    Method to send system emails
    :param data: email data
    :return: flag
    """

    try:

        mail_type = data.get('mail_type')

        if mail_type == 'ab_cart':
            context = {
                'user': User.objects.get(id=data.get('user_id')),
                'user_x': User.objects.get(id=data.get('user_id')),
                'domain': data.get('domain')
            }
            data['mail_context'] = context

        if mail_type == 'vendor_order_allocation':
            context = {
                'allocated_obj': OrderAllocatedVendor.objects.get(id=data.get('allocated_obj_id')),
                'domain': data.get('domain')
            }
            data['mail_context'] = context

        if mail_type == 'order_placed':
            context = {
                'user': User.objects.get(id=data.get('order_user_id')),
                'order': Order.objects.get(id=data.get('order_id'))
            }
            data['mail_context'] = context

        if mail_type == 'order_placed_advance_payment':
            print("#######in partial##############")
            context = {
                'user': User.objects.get(id=data.get('order_user_id')),
                'order': Order.objects.get(id=data.get('order_id'))
            }
            data['mail_context'] = context
            print("##############partial##########")

        if mail_type == 'order_placed_full_payment':
            print("############in full##########")
            context = {
                'user': User.objects.get(id=data.get('order_user_id')),
                'order': Order.objects.get(id=data.get('order_id'))
            }
            data['mail_context'] = context
            print("#######in full#################")
        if mail_type == 'order_failed':
            context = {
                'user': User.objects.get(id=data.get('order_user_id')),
                'order': Order.objects.get(id=data.get('order_id'))
            }
            data['mail_context'] = context

        if mail_type == 'vendor_order_reallocation':
            context = {
                # 'allocated_obj': OrderAllocatedVendor.objects.get(id=data.get('allocated_obj_id')),
                'order_number': data.get('order_number'),
                'last_allocated_asp': Partner.objects.get(id=data.get('last_allocated_asp')),

                # 'last_allocated_asp': data.get('last_allocated_asp'),
                'domain': data.get('domain')
            }
            data['mail_context'] = context

        if mail_type == 'order_reminder':
            context = {
                'allocated_obj': OrderAllocatedVendor.objects.get(id=data.get('allocated_obj_id')),
                'domain': data.get('domain')
            }
            data['mail_context'] = context

        if mail_type == 'order_full_payment_toasp':
            order = Order.objects.get(id=data.get('order_number'))

            context = {
                'allocated_obj': OrderAllocatedVendor.objects.get(id=data.get('allocated_obj_id')),
                'order': Order.objects.get(id=data.get('order_number')),
                'domain': data.get('domain')
            }
            data['mail_context'] = context



        send_email(**data)
        print("**************** Email sent *****************")

    except Exception as e:
        import os
        import sys
        print('-----------in exception----------')
        print(e.args)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        print(e.args)
        pass

    return True

@shared_task
def updateadvpayperc(**data):
    try:
        apply_to = data.get('apply_to')
        advance_payment_percentage = data.get('advance_payment_percentage')
        sale_advance_payment_percentage = data.get('sale_advance_payment_percentage')
        if apply_to == 1:

            product_obj = Product.objects.filter(product_class__name__in=['Rent','Rent Or Sale'], is_deleted=False)

            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.advance_payment_percentage = advance_payment_percentage
                    price.save()

        elif apply_to == 2:
            product_obj = Product.objects.filter(product_class__name='Sale', is_deleted=False)

            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.advance_payment_percentage = advance_payment_percentage
                    price.save()

            product_obj = Product.objects.filter(product_class__name='Rent Or Sale', is_deleted=False)

            for product in product_obj:

                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.sale_advance_payment_percentage = advance_payment_percentage
                    price.save()

        # elif apply_to == 3:
        #     product_obj = Product.objects.filter(product_class__name='Rent Or Sale', is_deleted=False)
        #
        #     for product in product_obj:
        #
        #         price_obj = product.stockrecords.all()
        #         price = price_obj.last()
        #         if price:
        #             price.advance_payment_percentage = advance_payment_percentage
        #             price.sale_advance_payment_percentage = sale_advance_payment_percentage
        #             price.save()


        elif apply_to == 4:

            product_obj = Product.objects.filter(product_class__name='Professional', is_deleted=False)

            for product in product_obj:
                price_obj = product.stockrecords.all()
                price = price_obj.last()
                if price:
                    price.advance_payment_percentage = advance_payment_percentage
                    price.save()
        print("**************** advanced payment *****************")

    except Exception as e:

        print(e.args)
        pass
    return True

@shared_task
def updatetaxperc(**data):
    try:
        apply_to = data.get('apply_to')
        tax_percentage = data.get('tax_percentage')
        sale_tax = data.get('sale_tax')
        product_tax_type = ''
        from decimal import Decimal
        tax_percentage = Decimal(tax_percentage)

        if sale_tax:
            sale_tax = Decimal(sale_tax)
        print("type of tax", type(tax_percentage), tax_percentage)

        if apply_to == 1:

            product_obj = Product.objects.filter(product_class__name='Rent', is_deleted=False)
            if tax_percentage == 6:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'

            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)

            for product in product_obj:
                try:
                    price_obj = product.stockrecords.all()
                    price = price_obj.last()
                    if price:
                        if price.rent_price:
                            price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                            price.rent_price_with_tax = price_with_tax
                            ceil_price = math.ceil(price_with_tax)
                            diff = ceil_price - price_with_tax
                            if diff <= 0.50:
                                price.rent_round_off_price = diff
                            else:
                                price.rent_round_off_price = diff - 1

                            if price.rent_market_price:
                                price.rent_total_saving = price.rent_market_price - price_with_tax

                        # for artificial flower
                        if price.art_rent_price:
                            art_price_with_tax = (price.art_rent_price * (tax_percentage / 100)) + price.art_rent_price
                            price.art_rent_price_with_tax = art_price_with_tax
                            art_ceil_price = math.ceil(art_price_with_tax)
                            diff = art_ceil_price - art_price_with_tax
                            if diff <= 0.50:
                                price.art_rent_round_off_price = diff
                            else:
                                price.art_rent_round_off_price = diff - 1

                            if price.art_rent_market_price:
                                price.art_rent_total_saving = price.art_rent_market_price - art_price_with_tax


                        # for artificial flower end

                        price.tax_percentage = tax_percentage
                        price.save()
                except Exception as e:
                    print(e.args)
                    continue

        elif apply_to == 2:
            product_obj = Product.objects.filter(product_class__name='Sale', is_deleted=False)
            if tax_percentage == 1:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'

            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)
            for product in product_obj:

                try:

                    price_obj = product.stockrecords.all()
                    price = price_obj.last()
                    if price:
                        if price.price_excl_tax:
                            price_with_tax = (price.price_excl_tax * (tax_percentage / 100)) + price.price_excl_tax
                            price.sale_price_with_tax = price_with_tax
                            ceil_price = math.ceil(price_with_tax)
                            diff = ceil_price - price_with_tax
                            if diff <= 0.50:
                                price.sale_round_off_price = diff
                            else:
                                price.sale_round_off_price = diff - 1

                            if price.sale_market_price:
                                price.sale_total_saving = price.sale_market_price - price_with_tax

                        # for artificial flower
                        if price.art_sale_price:
                            art_price_with_tax = (price.art_sale_price * (tax_percentage / 100)) + price.art_sale_price
                            price.art_sale_price_with_tax = art_price_with_tax
                            art_ceil_price = math.ceil(art_price_with_tax)
                            diff = art_ceil_price - art_price_with_tax
                            if diff <= 0.50:
                                price.art_sale_round_off_price = diff
                            else:
                                price.art_sale_round_off_price = diff - 1

                            if price.art_sale_market_price:
                                price.art_sale_total_saving = price.art_sale_market_price - art_price_with_tax
                        # for artificial flower end

                        price.tax_percentage = tax_percentage

                        price.save()

                except Exception as e:
                    print(e.args)
                    continue

        elif apply_to == 3:
            product_obj = Product.objects.filter(product_class__name='Rent Or Sale', is_deleted=False)
            if tax_percentage == 6 and sale_tax == 1:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18 and sale_tax == 18:
                product_tax_type = 'regular_tax'

            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)
            for product in product_obj:
                try:

                    price_obj = product.stockrecords.all()
                    price = price_obj.last()
                    if price:

                        # Save Sale Price
                        if price.price_excl_tax:
                            price_with_tax = (price.price_excl_tax * (sale_tax / 100)) + price.price_excl_tax
                            price.sale_price_with_tax = price_with_tax
                            ceil_price = math.ceil(price_with_tax)
                            diff = ceil_price - price_with_tax
                            if diff <= 0.50:
                                price.sale_round_off_price = diff
                            else:
                                price.sale_round_off_price = diff - 1

                            if price.sale_market_price:
                                price.sale_total_saving = price.sale_market_price - price_with_tax

                        # for artificial flower
                        if price.art_sale_price:
                            art_price_with_tax = (price.art_sale_price * (sale_tax / 100)) + price.art_sale_price
                            price.art_sale_price_with_tax = art_price_with_tax
                            art_ceil_price = math.ceil(art_price_with_tax)
                            diff = art_ceil_price - art_price_with_tax
                            if diff <= 0.50:
                                price.art_sale_round_off_price = diff
                            else:
                                price.art_sale_round_off_price = diff - 1

                            if price.art_sale_market_price:
                                price.art_sale_total_saving = price.art_sale_market_price - art_price_with_tax

                        # for artificial flower end

                        price.sale_tax_percentage = sale_tax
                        price.save()

                        # Save Rent Price
                        if price.rent_price:
                            price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                            price.rent_price_with_tax = price_with_tax
                            ceil_price = math.ceil(price_with_tax)
                            diff = ceil_price - price_with_tax
                            if diff <= 0.50:
                                price.rent_round_off_price = diff
                            else:
                                price.rent_round_off_price = diff - 1

                            if price.rent_market_price:
                                price.rent_total_saving = price.rent_market_price - price_with_tax

                        # for artificial flower
                        if price.art_rent_price:
                            art_price_with_tax = (price.art_rent_price * (tax_percentage / 100)) + price.art_rent_price
                            price.art_rent_price_with_tax = art_price_with_tax
                            art_ceil_price = math.ceil(art_price_with_tax)
                            diff = art_ceil_price - art_price_with_tax
                            if diff <= 0.50:
                                price.art_rent_round_off_price = diff
                            else:
                                price.art_rent_round_off_price = diff - 1

                            if price.art_rent_market_price:
                                price.art_rent_total_saving = price.art_rent_market_price - art_price_with_tax
                        # for artificial flower end
                        price.tax_percentage = tax_percentage

                        price.save()

                except Exception as e:
                    print(e.args)
                    continue


        elif apply_to == 4:

            product_obj = Product.objects.filter(product_class__name='Professional', is_deleted=False)
            if tax_percentage == 6:
                product_tax_type = 'composition_tax'
            elif tax_percentage == 18:
                product_tax_type = 'regular_tax'

            Product.objects.filter(id__in=product_obj.values('id')).update(product_tax_type=product_tax_type)
            for product in product_obj:
                try:

                    price_obj = product.stockrecords.all()
                    price = price_obj.last()
                    if price:

                        if price.rent_price:
                            price_with_tax = (price.rent_price * (tax_percentage / 100)) + price.rent_price
                            price.rent_price_with_tax = price_with_tax
                            ceil_price = math.ceil(price_with_tax)
                            diff = ceil_price - price_with_tax
                            if diff <= 0.50:
                                price.rent_round_off_price = diff
                            else:
                                price.rent_round_off_price = diff - 1

                            if price.rent_market_price:
                                price.rent_total_saving = price.rent_market_price - price_with_tax

                        # for artificial flower
                        if price.art_rent_price:
                            art_price_with_tax = (price.art_rent_price * (tax_percentage / 100)) + price.art_rent_price
                            price.art_rent_price_with_tax = art_price_with_tax
                            art_ceil_price = math.ceil(art_price_with_tax)
                            diff = art_ceil_price - art_price_with_tax
                            if diff <= 0.50:
                                price.art_rent_round_off_price = diff
                            else:
                                price.art_rent_round_off_price = diff - 1

                            if price.art_rent_market_price:
                                price.art_rent_total_saving = price.art_rent_market_price - art_price_with_tax
                        # for artificial flower end

                        price.tax_percentage = tax_percentage
                        price.save()

                except Exception as e:
                    print(e.args)
                    continue

        print("**************** tax percentage *****************")

    except Exception as e:

        import os
        import sys
        print('-----------in exception----------')
        print(e.args)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return True




