# python imports
import json, datetime, collections


# module imports
from oscar.core.loading import get_class, get_model

Product = get_model('catalogue', 'product')
Line = get_model('order','Line')
VendorCalender = get_model('partner','VendorCalender')


def get_product_blocked_date(product_id):

    try:
        context = {}
        unsorted_dates = []
        sorted_date =[]
        block_date =[]
        product = Product.objects.get(id=product_id, is_deleted=False)

        # for events
        events = VendorCalender.objects.filter(product=product)

        for event in events:

            sdate = datetime.datetime.date(event.from_date)
            edate = datetime.datetime.date(event.to_date)
            sorted_date.append((str(sdate), str(edate)))

            delta = edate - sdate

            for i in range(delta.days + 1):
                day = sdate + datetime.timedelta(days=i)
                unsorted_dates.append(str(datetime.datetime.strptime(str(day), '%Y-%m-%d').strftime('%m/%d/%Y')))

        # for orders
        order_lines = Line.objects.filter(product=product, booking_start_date__gte=datetime.datetime.now())

        orders_dates = []
        for line in order_lines:
            orders_dates.append((str(line.booking_start_date.date()), str(line.booking_end_date.date())))
            sorted_date.append((str(line.booking_start_date.date()), str(line.booking_end_date.date())))


        # if orders_dates and product.daily_capacity:
        #     dates_counter = collections.Counter(orders_dates)
        #     for i in dates_counter:
        #         print("in if@", dates_counter[i], product.daily_capacity)
        #         print("in if##", dates_counter[i] >= product.daily_capacity)
        #         if dates_counter[i] >= product.daily_capacity:
        #             print("in if")
        #             d1 = datetime.datetime.strptime(i[0], '%Y-%m-%d')
        #             d2 = datetime.datetime.strptime(i[1], '%Y-%m-%d')
        #             sdate = datetime.datetime.date(d1)
        #             edate = datetime.datetime.date(d2)
        #
        #             delta = edate - sdate
        #
        #             for i in range(delta.days + 1):
        #                 day = sdate + datetime.timedelta(days=i)
        #                 unsorted_dates.append(str(datetime.datetime.strptime(str(day), '%Y-%m-%d').strftime('%m/%d/%Y')))

        if sorted_date and product.daily_capacity:
            dates_counter = collections.Counter(sorted_date)
            for i in dates_counter:

                if dates_counter[i] >= product.daily_capacity:
                    d1 = datetime.datetime.strptime(i[0], '%Y-%m-%d')
                    d2 = datetime.datetime.strptime(i[1], '%Y-%m-%d')
                    sdate = datetime.datetime.date(d1)
                    edate = datetime.datetime.date(d2)

                    delta = edate - sdate
                    for i in range(delta.days + 1):
                        day = sdate + datetime.timedelta(days=i)
                        block_date.append(str(datetime.datetime.strptime(str(day), '%Y-%m-%d').strftime('%m/%d/%Y')))


        status = False
        default = 0
        if product.product_booking_time_delay:
            default = product.product_booking_time_delay
            default_booking_date = datetime.datetime.now()+ datetime.timedelta(hours=product.product_booking_time_delay)
            default_booking_date = default_booking_date.strftime('%m/%d/%Y')

            while str(default_booking_date) in block_date:
                status = True
                default = default + 24
                default_booking_date = datetime.datetime.now() + datetime.timedelta(hours=default)
                default_booking_date = default_booking_date.strftime('%m/%d/%Y')


        context = {
            'unsorted_dates' : block_date,
            'status': status,
            'default' : default

        }
        return context
        # return unsorted_dates

    except Exception as e:
        import os
        import sys
        print('---------#--in exception----------')
        print(e.args)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        return []