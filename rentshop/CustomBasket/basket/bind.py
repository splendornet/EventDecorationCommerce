# packages imports
from oscar.core.loading import get_model

# internal imports
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')


def get_product_shipping(price, type, quantity, booking_days, flower_type=None, is_package_product=False):
    # if is_package_product:
    #     return 0

    ship_sale_price, ship_rent_price = 0, 0

    costs_product = ProductCostEntries.objects.filter(product=price.product)

    if price.product.product_cost_type == 'Multiple' and price.product.is_transporation_available:

        if type == 'Sale':
            costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity,
                                         requirement_day__gte=1).order_by('-requirement_day')
            if not costs:
                costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity).order_by(
                    'requirement_day')

            if costs and price.product.is_transporation_available:
                costs = costs.last()
                ship_sale_price = costs.transport_cost

            return round(ship_sale_price)

        if type == 'Rent':

            costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity,
                                         rent_requirement_day__gte=booking_days).order_by('-rent_requirement_day')
            if not costs:
                costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity).order_by(
                    'rent_requirement_day')

            if costs and price.product.is_transporation_available:
                costs = costs.last()
                ship_rent_price = costs.rent_transport_cost

            return round(ship_rent_price)

    elif price.product.product_cost_type == 'Single' and price.product.is_transporation_available:
        if type == 'Sale':
            if price.sale_transportation_price and price.product.is_transporation_available:
                ship_sale_price = price.sale_transportation_price
            return round(ship_sale_price)

        if type == 'Rent':
            if price.rent_transportation_price and price.product.is_transporation_available:
                ship_rent_price = price.rent_transportation_price

            return round(ship_rent_price)

    return 0


def get_product_price(price, type, quantity, booking_days, flower_type=None, is_package_product=False):

    sale_price, rent_price = 0, 0

    costs_product = ProductCostEntries.objects.filter(product=price.product)

    if price.product.product_cost_type == 'Multiple':

        if type == 'Sale':
            costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity,
                                         requirement_day__gte=1).order_by('-requirement_day')
            if not costs:
                costs = costs_product.filter(quantity_from__lte=quantity, quantity_to__gte=quantity).order_by(
                    'requirement_day')

            if costs:
                costs = costs.last()
                if costs.cost_incl_tax:
                    sale_price = round(costs.cost_incl_tax)
            else:
                if price.sale_price_with_tax and price.sale_round_off_price:
                    sale_price = price.sale_price_with_tax + price.sale_round_off_price
                if price.sale_price_with_tax and not price.sale_round_off_price:
                    sale_price = round(price.sale_price_with_tax)
                if not price.sale_price_with_tax and price.price_excl_tax:
                    sale_price = round(price.price_excl_tax)

            return sale_price

        if type == 'Rent':

            costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity,
                                         rent_requirement_day__gte=booking_days).order_by('-rent_requirement_day')
            if not costs:
                costs = costs_product.filter(rent_quantity_from__lte=quantity, rent_quantity_to__gte=quantity).order_by(
                    'rent_requirement_day')

            if costs:
                costs = costs.last()
                rent_price = round(costs.rent_cost_incl_tax)
            else:
                if price.rent_price_with_tax and price.rent_round_off_price:
                    rent_price = price.rent_price_with_tax + price.rent_round_off_price
                if price.rent_price_with_tax and not price.rent_round_off_price:
                    rent_price = round(price.rent_price_with_tax)
                if not price.rent_price_with_tax and price.rent_price:
                    rent_price = round(price.rent_price)

            return rent_price

    else:
        if price.product.is_real_flower and flower_type == 'real':
            if price.art_sale_price_with_tax and price.art_sale_round_off_price:
                sale_price = price.art_sale_price_with_tax + price.art_sale_round_off_price
            if price.art_sale_price_with_tax and not price.art_sale_round_off_price:
                sale_price = round(price.art_sale_price_with_tax)
            if not price.art_sale_price_with_tax and price.art_sale_price:
                sale_price = round(price.art_sale_price)

            if price.art_rent_price_with_tax and price.art_rent_round_off_price:
                rent_price = price.art_rent_price_with_tax + price.art_rent_round_off_price
            if price.art_rent_price_with_tax and not price.art_rent_round_off_price:
                rent_price = round(price.art_rent_price_with_tax)
            if not price.art_rent_price_with_tax and price.art_rent_price:
                rent_price = round(price.art_rent_price)

        else:
            if price.sale_price_with_tax and price.sale_round_off_price:
                sale_price = price.sale_price_with_tax + price.sale_round_off_price
            if price.sale_price_with_tax and not price.sale_round_off_price:
                sale_price = round(price.sale_price_with_tax)
            if not price.sale_price_with_tax and price.price_excl_tax:
                sale_price = round(price.price_excl_tax)

            if price.rent_price_with_tax and price.rent_round_off_price:
                rent_price = price.rent_price_with_tax + price.rent_round_off_price
            if price.rent_price_with_tax and not price.rent_round_off_price:
                rent_price = round(price.rent_price_with_tax)
            if not price.rent_price_with_tax and price.rent_price:
                rent_price = round(price.rent_price)

        if type == 'Sale':
            return sale_price

        if type == 'Rent':
            return rent_price


def bind_product_quantity(product, quantity, order_type, booking_days):
    if not order_type:
        return '3'

    if product.product_cost_type != 'Multiple':
        return '3'

    if not ProductCostEntries.objects.filter(product=product):
        return '2'

    cost = ProductCostEntries.objects.filter(product=product)

    if order_type in ['Rent', 'Professional'] and not cost.filter(rent_quantity_to__gte=quantity,
                                                                  rent_quantity_from__lte=quantity):
        return '1'

    if order_type in ['Rent', 'Professional'] and not cost.filter(rent_quantity_to__gte=quantity,
                                                                  rent_quantity_from__lte=quantity,
                                                                  rent_requirement_day__gte=booking_days):
        return '1'

    if order_type in ['Sale'] and not cost.filter(quantity_to__gte=quantity, quantity_from__lte=quantity):
        return '1'

    if order_type in ['Sale'] and not cost.filter(quantity_to__gte=quantity, quantity_from__lte=quantity,
                                                  requirement_day__gte=1):
        return '1'

    if order_type in ['Rent', 'Professional']:
        cost_product = cost.filter(rent_quantity_to__gte=quantity, rent_quantity_from__lte=quantity,
                                   rent_requirement_day__gte=booking_days).order_by('-rent_requirement_day')
        if not cost_product:
            cost_product = cost.filter(rent_quantity_to__gte=quantity, rent_quantity_from__lte=quantity).order_by(
                'rent_requirement_day')

        if not cost_product or not cost_product.last().rent_cost_incl_tax:
            return '1'

    if order_type in ['Sale']:
        cost_product = cost.filter(quantity_to__gte=quantity, quantity_from__lte=quantity,
                                   requirement_day__gte=1).order_by('-requirement_day')
        if not cost_product:
            cost_product = cost.filter(quantity_to__gte=quantity, quantity_from__lte=quantity).order_by(
                'requirement_day')

        if not cost_product or not cost_product.last().cost_incl_tax:
            return '1'

    return '0'
