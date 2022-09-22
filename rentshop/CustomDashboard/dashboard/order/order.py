# python imports
from decimal import Decimal as D, InvalidOperation
import logging
import pdfkit
import datetime
# django imports
from django.db.models import Q
from django.views import View
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.urls import NoReverseMatch, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site

# packages imports
from oscar.apps.dashboard.orders.views import OrderDetailView, OrderListView
from oscar.core.loading import get_classes, get_model, get_class
from oscar.apps.checkout.signals import post_checkout
from oscar.core.compat import get_user_model


# internal imports
from .. import forms as dash_form

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
Partner = get_model('partner', 'Partner')

Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
OrderNote = get_model('order', 'OrderNote')
ShippingAddress = get_model('order', 'ShippingAddress')
Line = get_model('order', 'Line')
ShippingEventType = get_model('order', 'ShippingEventType')
PaymentEventType = get_model('order', 'PaymentEventType')
BillingAddress = get_model('order', 'BillingAddress')
PaymentEvent = get_model('order', 'PaymentEvent')
PaymentEventQuantity = get_model('order', 'PaymentEventQuantity')
OrderAllocatedVendor = get_model('order', 'OrderAllocatedVendor')

Transaction = get_model('payment', 'Transaction')
trigger_email = get_class('RentCore.tasks', 'trigger_email')
send_sms = get_class('RentCore.email', 'send_sms')

CommunicationEventType = get_model('customer', 'CommunicationEventType')
User = get_user_model()

OrderNoteForm = get_class('dashboard.orders.forms', 'OrderNoteForm')
OrderStatusForm = get_class('dashboard.orders.forms', 'OrderStatusForm')
EventHandler = get_class('order.processing', 'EventHandler')
Dispatcher = get_class('customer.utils', 'Dispatcher')

logger = logging.getLogger('oscar.checkout')


def queryset_orders_for_user(user):

    """
    Get order users
    :param user: user
    :return: qs
    """

    queryset = Order._default_manager.select_related('billing_address', 'billing_address__country', 'shipping_address', 'shipping_address__country', 'user').prefetch_related('lines')

    if not user.is_staff:
        return queryset
    else:
        if user.is_superuser:
            return queryset
        else:
            return queryset


def custom_get_order_for_user_or_404(user, number):

    """
    Method to validate order
    :param user: user
    :param number: order
    :return: flag
    """

    try:
        return queryset_orders_for_user(user).get(number=number)
    except ObjectDoesNotExist:
        raise Http404()


class CustomOrderListView(OrderListView):

    """
    Oscar order list extended method.
    """

    form_class = dash_form.CustomOrderSearchForm

    def queryset_orders_for_user_obj(self):

        """
        Method to get core query set.
        :return: order queryset
        """

        queryset = Order._default_manager.select_related('billing_address', 'billing_address__country', 'shipping_address', 'shipping_address__country', 'user').prefetch_related('lines')

        if not Partner.objects.filter(users=self.request.user):
            return queryset
        else:
            partners = Partner.objects.filter(users=self.request.user)

            # allocated orders
            allocated_orders = OrderAllocatedVendor.objects.filter(vendor=partners.last())
            queryset = queryset.filter(lines__id__in=allocated_orders.values_list('order_line__id', flat=True)).distinct()

            return queryset

    def dispatch(self, request, *args, **kwargs):

        """
        List view core method
        :param request: default
        :param args: default
        :param kwargs: default
        :return: super class object.
        """

        self.base_queryset = self.queryset_orders_for_user_obj().order_by('-date_placed')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        """
        List view extended queryset method.
        :return: queryset
        """

        queryset = self.queryset_orders_for_user_obj().order_by('-number')

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data['order_number']:
            queryset = queryset.filter(number__icontains=data['order_number'])

        if data['name']:
            # If the value is two words, then assume they are first name and
            # last name
            parts = data['name'].split()
            allow_anon = getattr(settings, 'OSCAR_ALLOW_ANON_CHECKOUT', False)

            if len(parts) == 1:
                parts = [data['name'], data['name']]
            else:
                parts = [parts[0], parts[1:]]

            filter = Q(user__first_name__istartswith=parts[0])
            filter |= Q(user__last_name__istartswith=parts[1])
            if allow_anon:
                filter |= Q(billing_address__first_name__istartswith=parts[0])
                filter |= Q(shipping_address__first_name__istartswith=parts[0])
                filter |= Q(billing_address__last_name__istartswith=parts[1])
                filter |= Q(shipping_address__last_name__istartswith=parts[1])

            queryset = queryset.filter(filter).distinct()


        if data.get('product'):
            product = data.get('product')
            order_line = OrderLine.objects.filter(product=product)
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        if data.get('category') and data.get('sub_category'):

            category_list = []

            category = Category.objects.filter(id=data.get('category').id)
            sub_category = Category.objects.filter(id=data.get('sub_category').id)

            category_list.extend(list(category.values_list('id', flat=True)))
            category_list.extend(list(sub_category.values_list('id', flat=True)))

            order_line = OrderLine.objects.filter(product__categories__in=category_list)
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        if data.get('category') and not data.get('sub_category'):
            category = Category.objects.filter(id=data.get('category').id)
            id_list = [obj.id for obj in category.last().get_descendants_and_self()]
            order_line = OrderLine.objects.filter(product__categories__in=id_list)
            # order_line = OrderLine.objects.filter(product__categories__in=category.values_list('id', flat=True))
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        if data.get('sub_category') and not data.get('category'):
            category = Category.objects.filter(id=data.get('sub_category').id)
            order_line = OrderLine.objects.filter(product__categories__in=category.values_list('id', flat=True))
            queryset = queryset.filter(id__in=order_line.values_list('order', flat=True))

        if data.get('status'):
            status = data.get('status')
            queryset = queryset.filter(status__icontains=status)

        return queryset

    def get(self, request, *args, **kwargs):

        """
        Get method to return order list
        :param request: default
        :param args: default
        :param kwargs: default
        :return: render
        """
        if request.GET.get('response_format', 'html') == 'html':
            _mutable = request.GET._mutable

            # set to mutable
            request.GET._mutable = True
            request.GET['response_format'] = ''
            request.GET._mutable = _mutable
        if 'order_number' in request.GET and request.GET.get('response_format', 'html') == 'html':

            try:

                return super().get(request, *args, **kwargs)

            except Order.DoesNotExist:

                order_number = request.GET['order_number']
                messages.error(self.request, ("Order with '%s' order number does not exists.") % order_number)

                return redirect('dashboard:order-list')

        return super().get(request, *args, **kwargs)

    def get_search_filter_descriptions(self):

        """
        Order search label text.
        :return: label text
        """

        descriptions = []
        data = getattr(self.form, 'cleaned_data', None)

        if data is None:
            return descriptions

        if data.get('order_number'):
            descriptions.append(_('Order number starts with "{order_number}').format(order_number=data['order_number']))

        return descriptions

    def get_context_data(self, **kwargs):

        """
        List view extended context data method.
        :param kwargs: default
        :return: default
        """

        ctx = super().get_context_data(**kwargs)
        ctx['search_filters'] = self.get_search_filter_descriptions()
        return ctx


class CustomOrderDetailView(OrderDetailView):

    """
    Dashboard view to display a single order.
    Supports the permission-based dashboard.
    """

    communication_type_code = 'ORDER_PLACED'

    view_signal = post_checkout
    model = Order
    context_object_name = 'order'
    template_name = 'dashboard/orders/order_detail.html'

    order_actions = (
        'save_note', 'delete_note', 'change_order_status',
        'create_order_payment_event', 'update_paid_amount',
        'change_refund_status'
    )
    line_actions = ('change_line_statuses', 'create_shipping_event', 'create_payment_event', 'change_final_payment_status',)

    def get_object(self, queryset=None):

        return custom_get_order_for_user_or_404(self.request.user, self.kwargs['number'])

    def get_order_lines(self):

        try:
            if self.request.user.is_superuser:
                return self.object.lines.all()
            else:

                partners = Partner._default_manager.filter(users=self.request.user)
                allocated_lines = OrderAllocatedVendor.objects.filter(vendor=partners.last())

                return self.object.lines.filter(id__in=allocated_lines.values_list('order_line__id', flat=True))

        except Exception as e:

            raise PermissionDenied

    def post(self, request, *args, **kwargs):

        order = self.object = self.get_object()

        if 'order_action' in request.POST:
            return self.handle_order_action(request, order, request.POST['order_action'])

        if 'line_action' in request.POST:
            return self.handle_line_action(request, order, request.POST['line_action'])

        return self.reload_page(error=_("No valid action submitted"))

    def handle_order_action(self, request, order, action):

        if action not in self.order_actions:
            return self.reload_page(error=_("Invalid action"))
        return getattr(self, action)(request, order)

    def handle_line_action(self, request, order, action):

        if action not in self.line_actions:
            return self.reload_page(error=_("Invalid action"))

        if action == "change_final_payment_status":
            line_id = request.POST.get('line_id')
            return getattr(self, action)(request, order, line_id)
        else:
            line_ids = request.POST.getlist('selected_line')
            if len(line_ids) == 0:
                return self.reload_page(error=_("You must select some lines to act on"))

            lines = self.get_order_lines()
            lines = lines.filter(id__in=line_ids)

            if len(line_ids) != len(lines):
                return self.reload_page(error=_("Invalid lines requested"))

            line_quantities = []
            for line in lines:
                qty = request.POST.get('selected_line_qty_%s' % line.id)
                try:
                    qty = int(qty)
                except ValueError:
                    qty = None
                if qty is None or qty <= 0:
                    error_msg = _("The entered quantity for line #%s is not valid")
                    return self.reload_page(error=error_msg % line.id)
                elif qty > line.quantity:
                    error_msg = _("The entered quantity for line #%(line_id)s should not be higher than %(quantity)s")
                    kwargs = {'line_id': line.id, 'quantity': line.quantity}
                    return self.reload_page(error=error_msg % kwargs)

                line_quantities.append(qty)

            return getattr(self, action)(request, order, lines, line_quantities)

    def reload_page(self, fragment=None, error=None):
        url = reverse('dashboard:order-detail', kwargs={'number': self.object.number})

        if fragment:
            url += '#' + fragment
        if error:
            messages.error(self.request, error)
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):

        ctx = super().get_context_data(**kwargs)
        ctx['active_tab'] = kwargs.get('active_tab', 'lines')

        ctx['note_form'] = self.get_order_note_form()
        ctx['order_status_form'] = self.get_order_status_form()

        ctx['lines'] = self.get_order_lines()
        ctx['line_statuses'] = Line.all_statuses()
        ctx['shipping_event_types'] = ShippingEventType.objects.all()
        ctx['payment_event_types'] = PaymentEventType.objects.all()
        ctx['due_amount'] = self.get_due_amount()
        ctx['order_total_after_discount'] = self.get_order_total_after_discount()

        ctx['payment_transactions'] = self.get_payment_transactions()
        ctx['is_super_user'] = self.request.user.is_superuser

        return ctx

    def get_payment_transactions(self):
        return Transaction.objects.filter(source__order=self.object)

    def get_order_note_form(self):

        kwargs = {
            'order': self.object,
            'user': self.request.user,
            'data': None
        }

        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST

        note_id = self.kwargs.get('note_id', None)

        if note_id:
            note = get_object_or_404(OrderNote, order=self.object, id=note_id)
            if note.is_editable():
                kwargs['instance'] = note

        return OrderNoteForm(**kwargs)

    def get_order_status_form(self):

        data = None

        if self.request.method == 'POST':
            data = self.request.POST

        return OrderStatusForm(order=self.object, data=data)

    def get_due_amount(self):

        paidAmount = self.object.total_discount_excl_tax + self.object.paid_amount
        ordertotalAmt = self.object.total_amount_incl_tax - paidAmount

        return ordertotalAmt

    def get_order_total_after_discount(self):
        ordertotalAmtAfterDiscount = self.object.total_amount_incl_tax - self.object.total_discount_excl_tax
        return ordertotalAmtAfterDiscount

    def save_note(self, request, order):
        form = self.get_order_note_form()
        if form.is_valid():
            form.save()
            messages.success(self.request, _("Note saved"))
            return self.reload_page(fragment='notes')

        ctx = self.get_context_data(note_form=form, active_tab='notes')
        return self.render_to_response(ctx)

    def delete_note(self, request, order):
        try:
            note = order.notes.get(id=request.POST.get('note_id', None))
        except ObjectDoesNotExist:
            messages.error(request, _("Note cannot be deleted"))
        else:
            messages.info(request, _("Note deleted"))
            note.delete()
        return self.reload_page()

    def update_paid_amount(self, request, order):
        amount_str = request.POST.get('paid_amount', None)
        try:
            amount = D(amount_str)
            order_total = self.get_order_total_after_discount()
            if amount > order_total or amount < 0:
                messages.error(request, _(
                    'Paid Amount must not be greater than "Total after discount" and must not be less than zero'))
                return self.reload_page()

            order.paid_amount = amount
            order.save()

            self.send_confirmation_message(order, self.communication_type_code)
            messages.info(request, _("Paid Amount Updated"))
        except InvalidOperation:
            messages.error(request, _("Please choose a valid amount"))
            return self.reload_page()
        return self.reload_page()

    def change_refund_status(self, request, order):
        amount_str = request.POST.get('is_refund', None)
        try:
            if order.is_refund == False:

                amount = 0
                lines = self.get_order_lines()
                for line in lines:
                    obj = Product.objects.filter(upc=line.upc, is_deleted=False)
                    if obj.last() and obj.last().is_deposite_applicable and obj.last().deposite_amount:
                        amount = amount + obj.last().deposite_amount

                if amount != 0:
                    current_site = Site.objects.get_current()
                    mail_subject = 'TakeRentPe -  Refund Amount.'
                    message = render_to_string(
                        'customer/email/order_refund_email.html',
                        {
                            'user': order.user,
                            'number': order.number,
                            'deposite_amount': amount,
                            'domain': current_site.domain,
                        }
                    )

                    to_email = order.user.email,
                    from_email = settings.FROM_EMAIL_ADDRESS
                    email = EmailMessage(mail_subject, message, from_email, to_email)
                    email.content_subtype = "html"
                    email.send()
                    order.is_refund = True
                    order.save()
                    messages.info(request, _("Amount is Refunded"))
                else:

                    messages.info(request, _("There is no amount for refund"))

        except InvalidOperation:
            messages.error(request, _("Please choose a valid amount"))
            return self.reload_page()
        return self.reload_page()

    def change_order_status(self, request, order):
        form = self.get_order_status_form()

        if not form.is_valid():
            return self.reload_page(error=_("Invalid form submission"))

        old_status, new_status = order.status, form.cleaned_data['new_status']
        handler = EventHandler(request.user)

        success_msg = _("Order status changed from '%(old_status)s' to '%(new_status)s'") % {'old_status': old_status, 'new_status': new_status}
        try:
            handler.handle_order_status_change(
                order, new_status, note_msg=success_msg)
            if order.status == "Cancelled":
                order.order_cancelled_date = datetime.datetime.now()
                order.save()
                self.send_cancellation_message(order, self.communication_type_code)

        except PaymentError as e:
            messages.error(request, _("Unable to change order status due to payment error: %s") % e)
        except order_exceptions.InvalidOrderStatus as e:
            # The form should validate against this, so we should only end up
            # here during race conditions.
            messages.error(request, _("Unable to change order status as the requested new status is not valid"))
        else:
            messages.info(request, success_msg)
            ##########send order completed msg

            try:
                mobile_number = order.user.profile_user.mobile_number

            # message = 'Your full payment is successfully received for Order No. '+ str(order.number)+''
                message = 'Your Order No. '+ str(order.number)+'  is '+str(new_status).lower()+' successfully. Take Rent Pe.'
                msg_kwargs = {
                   'message': message,
                    'mobile_number': mobile_number,
                }

                send_sms(**msg_kwargs)
            except:
                messages.error(request, "No number is attached to user to sent message")
        return self.reload_page()

    def create_order_payment_event(self, request, order):
        """
        Create a payment event for the whole order
        """
        amount_str = request.POST.get('amount', None)
        try:
            amount = D(amount_str)
        except InvalidOperation:
            messages.error(request, _("Please choose a valid amount"))
            return self.reload_page()
        return self._create_payment_event(request, order, amount)

    # Line-level actions

    def change_line_statuses(self, request, order, lines, quantities):

        new_status = request.POST['new_status'].strip()

        if not new_status:
            messages.error(request, _("The new status '%s' is not valid") % new_status)
            return self.reload_page()

        errors = []

        for line in lines:
            if new_status not in line.available_statuses():
                errors.append(_("'%(status)s' is not a valid new status for line %(line_id)d") % {'status': new_status, 'line_id': line.id})

        if errors:
            messages.error(request, "\n".join(errors))
            return self.reload_page()

        msgs = []
        for line in lines:
            msg = _("Status of line #%(line_id)d changed from '%(old_status)s' to '%(new_status)s'") % {'line_id': line.id, 'old_status': line.status, 'new_status': new_status}
            msgs.append(msg)
            line.set_status(new_status)
        message = "\n".join(msgs)
        messages.info(request, message)
        order.notes.create(user=request.user, message=message, note_type=OrderNote.SYSTEM)
        return self.reload_page()

    def change_final_payment_status(self, request, order, line_id):

        amount_str = request.POST.get('final_payment', None)
        try:
            obj_list = Line.objects.filter(id=line_id)
            obj = obj_list.last()
            if obj_list and not obj.final_payment:

                current_site = Site.objects.get_current()
                mail_subject = 'TakeRentPe -  Final Payment.'
                message = render_to_string(
                    'customer/email/order_final_payment_email.html',
                    {
                        'user': order.user,
                        'number': order.number,
                        'partner_name': obj.partner_name,
                        'domain': current_site.domain,
                    }
                )

                to_email = settings.SUPPORT_EMAIL,
                from_email = settings.FROM_EMAIL_ADDRESS
                email = EmailMessage(mail_subject, message, from_email, to_email)
                email.content_subtype = "html"
                email.send()

                obj.final_payment = True
                obj.save()
                all_success = True
                lines = self.get_order_lines()

                if False not in lines.values_list("final_payment",flat=True):
                    order.order_payment_status = "success"
                    if order.order_type == 'partial':
                        mail_subject = 'TakeRentPe : Full Payment'
                        message = render_to_string(
                            'customer/email/order_full_payment.html',
                            {
                                'user': order.user,
                                'order_user_id': order.user.id,
                                'partner_name': obj.partner_name,
                                'domain': current_site.domain,
                            }
                        )

                        to_email = [order.user.email]
                        from_email = settings.FROM_EMAIL_ADDRESS
                        email = EmailMessage(mail_subject, message, from_email, to_email)
                        email.content_subtype = "html"
                        email.send()

                        mobile_number=None
                        #send sms to client FULL PAYMENT
                        try:
                            if order.user.is_staff:
                                active_user = User.objects.filter(id= order.user.id).values_list('id')
                                active_partner = Partner.objects.filter(users__in=active_user)
                                mobile_number = active_partner.last().telephone_number
                        except:
                            mobile_number = order.user.profile_user.mobile_number

                        # message = 'Your full payment is successfully received for Order No. '+ str(order.number)+''
                        message = 'Your full payment is successfully received for Order No. '+ str(order.number)+' Take Rent Pe.'
                        msg_kwargs = {
                            'message': message,
                            'mobile_number': mobile_number,
                        }

                        send_sms(**msg_kwargs)

                        lines = self.get_order_lines()
                        for line in lines:
                            if line.allocated_order_line.all():
                                part_obj = Partner.objects.filter(id=line.allocated_order_line.last().vendor_id,
                                                                  users__is_active=True)
                                if part_obj:
                                    email_data = {
                                        'mail_subject': 'TakeRentPe : Order Full Payment Received',
                                        'mail_template': 'dashboard/sales/prime_bucket/order_full_payment_recemail_toasp.html',
                                        'mail_to': [line.allocated_order_line.last().vendor.email_id],
                                        'mail_type': 'order_full_payment_toasp',
                                        'allocated_obj_id': line.allocated_order_line.last().id,
                                        'order_number': line.allocated_order_line.last().order_id,
                                        'domain': current_site.domain
                                    }

                                    trigger_email.delay(**email_data)
                                    invoice_link = current_site.domain + line.product_invoice

                                    # sms send code ORDER FULL PAYMENT RECEIVED MAIL
                                    # message = 'Hello ' + part_obj.last().name + 'I hereby confirm that the sum of #' + _allocated.last().order_number + ' which is ' + _allocated.last().order_line.booking_start_date.date + '-' + _allocated.last().order_line.booking_end_date.date + 'to another ASP.So click on below link for more details and If you have any questions please let us know. We will get back to you in no time, promise! Happy celebranto!'
                                    message = 'Hello! Your payment is successfully received for ' + str(order.number) + ' The funds will be with you shortly. Visit the link for more details. '+'('+str(invoice_link)+')'+' Happy celebranto!'
                                    msg_kwargs = {
                                        'message': message,
                                        'mobile_number': part_obj.last().telephone_number,
                                    }
                                    send_sms(**msg_kwargs)

                        order.order_type = 'full'

                    order.save()

                messages.info(request, _("Final Payment Received"))
            else:

                messages.info(request, _("There is no amount"))


        except InvalidOperation:
            messages.error(request, _("Please choose a valid amount"))
            return self.reload_page()
        return self.reload_page()

    def create_shipping_event(self, request, order, lines, quantities):
        code = request.POST['shipping_event_type']
        try:
            event_type = ShippingEventType._default_manager.get(code=code)
        except ShippingEventType.DoesNotExist:
            messages.error(request, _("The event type '%s' is not valid")
                           % code)
            return self.reload_page()

        reference = request.POST.get('reference', None)
        try:
            EventHandler().handle_shipping_event(order, event_type, lines,
                                                 quantities,
                                                 reference=reference)
        except order_exceptions.InvalidShippingEvent as e:
            messages.error(request, _("Unable to create shipping event: %s") % e)
        except order_exceptions.InvalidStatus as e:
            messages.error(request, _("Unable to create shipping event: %s") % e)
        except PaymentError as e:
            messages.error(request, _("Unable to create shipping event due to payment error: %s") % e)
        else:
            messages.success(request, _("Shipping event created"))
        return self.reload_page()

    def create_payment_event(self, request, order, lines, quantities):
        """
        Create a payment event for a subset of order lines
        """
        amount_str = request.POST.get('amount', None)

        # If no amount passed, then we add up the total of the selected lines
        if not amount_str:
            amount = sum([line.line_price_incl_tax for line in lines])
        else:
            try:
                amount = D(amount_str)
            except InvalidOperation:
                messages.error(request, _("Please choose a valid amount"))
                return self.reload_page()

        return self._create_payment_event(request, order, amount, lines, quantities)

    def _create_payment_event(self, request, order, amount, lines=None,
                              quantities=None):
        code = request.POST.get('payment_event_type')
        try:
            event_type = PaymentEventType._default_manager.get(code=code)
        except PaymentEventType.DoesNotExist:
            messages.error(
                request, _("The event type '%s' is not valid") % code)
            return self.reload_page()
        try:
            EventHandler().handle_payment_event(
                order, event_type, amount, lines, quantities)
        except PaymentError as e:
            messages.error(request, _("Unable to create payment event due to"
                                      " payment error: %s") % e)
        except order_exceptions.InvalidPaymentEvent as e:
            messages.error(
                request, _("Unable to create payment event: %s") % e)
        else:
            messages.info(request, _("Payment event created"))
        return self.reload_page()

    def send_confirmation_message(self, order, code, **kwargs):
        ctx = self.get_message_context(order)
        try:
            event_type = CommunicationEventType.objects.get(code=code)
        except CommunicationEventType.DoesNotExist:

            messages = CommunicationEventType.objects.get_and_render(code, ctx)
            event_type = None
        else:
            messages = event_type.get_messages(ctx)

        if messages and messages['body']:
            logger.info("Order #%s - sending %s messages", order.number, code)
            dispatcher = Dispatcher(logger)
            dispatcher.dispatch_order_messages(order, messages,
                                               event_type, **kwargs)
        else:
            logger.warning("Order #%s - no %s communication event type",
                           order.number, code)

    def send_cancellation_message(self, order, code, **kwargs):
        ctx = self.get_message_context(order, cancelOrder=True)
        try:
            event_type = CommunicationEventType.objects.get(code=code)
        except CommunicationEventType.DoesNotExist:
            # No event-type in database, attempt to find templates for this
            # type and render them immediately to get the messages.  Since we
            # have not CommunicationEventType to link to, we can't create a
            # CommunicationEvent instance.
            messages = CommunicationEventType.objects.get_and_render(code, ctx)
            event_type = None
        else:
            messages = event_type.get_messages(ctx)

        if messages and messages['body']:
            logger.info("Order #%s - sending %s messages", order.number, code)
            dispatcher = Dispatcher(logger)
            dispatcher.dispatch_order_messages(order, messages,
                                               event_type, **kwargs)
        else:
            logger.warning("Order #%s - no %s communication event type",
                           order.number, code)

    def get_message_context(self, order, cancelOrder=False):
        if cancelOrder:
            ctx = {
                'user': self.request.user,
                'order': order,
                'site': get_current_site(self.request),
                'lines': order.lines.all(),
                'cancelOrder': True,
                'order_total_after_discount': self.get_order_total_after_discount(),
                'due_amount': self.get_due_amount()
            }
        else:
            ctx = {
                'user': self.request.user,
                'order': order,
                'site': get_current_site(self.request),
                'lines': order.lines.all(),
                'paidDetails': True,
                'order_total_after_discount': self.get_order_total_after_discount(),
                'due_amount': self.get_due_amount()
            }

        if not self.request.user.is_authenticated:
            # Attempt to add the anon order status URL to the email template
            # ctx.
            try:
                path = reverse('customer:anon-order',
                               kwargs={'order_number': order.number,
                                       'hash': order.verification_hash()})
            except NoReverseMatch:
                # We don't care that much if we can't resolve the URL
                pass
            else:
                site = Site.objects.get_current()
                ctx['status_url'] = 'http://%s%s' % (site.domain, path)
        return ctx


class OrderSummaryInvoiceView(View):

    def get(self, request, *args, **kwargs):

        order = Order.objects.get(id=kwargs.get('pk'))
        current_site = Site.objects.get_current()

        context = dict()
        context['order'] = order
        context['site'] = 'TakeRentPe'      # replace this
        context['site_logo'] = current_site.domain + '/static/' + settings.LOGO_URL

        return render(request, 'dashboard/orders/invoices/order_summary.html', context=context)


class OrderInvoiceView(View):

    def get(self, request, *args, **kwargs):

        order = Order.objects.get(id=kwargs.get('pk'))
        current_site = Site.objects.get_current()

        context = dict()
        context['order'] = order
        context['site'] = 'TakeRentPe'      # replace this
        context['site_logo'] = current_site.domain + '/static/' + settings.LOGO_URL
        context['pan_number'] = 'AAAA1111222'
        context['gst_number'] = 'FFF00011111'

        return render(request, 'dashboard/orders/invoices/order_invoice.html', context=context)


class OrderInvoiceProductView(View):

    def get(self, request, *args, **kwargs):

        vendor = Partner.objects.get(id=kwargs.get('vendor_id'))
        order = Order.objects.get(id=kwargs.get('pk'))
        current_site = Site.objects.get_current()

        context = dict()
        context['order'] = order
        context['site'] = 'TakeRentPe'
        context['site_logo'] = current_site.domain + '/static/' + settings.LOGO_URL
        context['vendor'] = vendor

        return render(request, 'dashboard/orders/invoices/order_invoice_product.html', context=context)


class OrderInvoiceRaw(View):

    def get_site(self):
        current_site = Site.objects.get_current()
        site = current_site.domain

        if site[-1] == '/':
            return site

        return site + '/'

    def get(self, request, *args, **kwargs):

        order = Order.objects.get(id=kwargs.get('pk'))

        pdf_name = 'order_invoice_%s.pdf' % (str(order.number))

        pdf_path = 'media/order_summary/' + pdf_name

        full_path = settings.MEDIA_ROOT + '/order_summary/' + pdf_name

        url = self.get_site() + 'dashboard/orders/order-invoice/' + str(order.id)
        pdfkit.from_url(url, pdf_path)

        return FileResponse(open(full_path, 'rb'), content_type='application/pdf')