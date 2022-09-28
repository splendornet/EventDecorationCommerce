# python import
import os

# django imports
from django.conf import settings
from django.contrib.sites.models import Site

# package import
import pdfkit
from oscar.core.loading import get_model, get_class

send_email = get_class('RentCore.email', 'send_email')
Partner = get_model('partner', 'Partner')


def get_site():

    current_site = Site.objects.get_current()
    site = current_site.domain

    if site[-1] == '/':
        return site

    return site + '/'


def generate_order_summary(order):
    import pdfkit, tempfile
    from django.template.loader import get_template

    pdf_name = 'order_summary_%s.pdf' % (str(order.number))
    pdf_path = 'media/order_summary/' + pdf_name

    options = {}

    current_site = Site.objects.get_current()

    context = dict()
    context['order'] = order
    context['site'] = 'TakeRentPe'  # replace this
    context['site_logo'] = current_site.domain + '/static/' + settings.LOGO_URL

    # create pdf body
    template = get_template('dashboard/orders/invoices/order_summary.html')
    html = template.render(context)
    # create pdf body
    try:
        pdfkit.from_string(
            html, pdf_path, options=options
        )
    except:
        pass

    return pdf_path


def generate_order_invoice(order):
    import pdfkit, tempfile
    from django.template.loader import get_template

    pdf_name = 'order_invoice_%s.pdf' % (str(order.number))
    # pdf_path = 'media/order_summary/' + pdf_name

    pdf_path = 'opt/takerentpe-dev/rentshop/media/order_summary/' + pdf_name

    options = {}

    current_site = Site.objects.get_current()

    context = dict()
    context['order'] = order
    context['site'] = 'TakeRentPe'  # replace this
    context['site_logo'] = current_site.domain + '/static/' + settings.LOGO_URL
    context['pan_number'] = 'AAAA1111222'
    context['gst_number'] = 'FFF00011111'

    # create pdf body
    template = get_template('dashboard/orders/invoices/order_invoice_product.html')
    html = template.render(context)
    # create pdf body
    try:
        pdfkit.from_string(
            html, pdf_path, options=options
        )
    except:
        pass

    return pdf_path


def generate_order_invoice_product(line, order):
    import pdfkit, tempfile
    from django.template.loader import get_template

    pdf_name = pdf_name = 'order_invoice_%s_%s_%s.pdf' % (str(order.number), str(line.partner.id), (line.product.id))
    # pdf_path = 'media/order_summary/' + pdf_name

    pdf_path = 'opt/takerentpe-dev/rentshop/media/order_summary/' + pdf_name

    options = {}
    vendor = Partner.objects.get(id=line.partner.id)
    current_site = Site.objects.get_current()

    context = dict()
    context['order'] = order
    context['order_line'] = line
    context['line'] = line
    context['site'] = 'TakeRentPe'
    context['site_logo'] = current_site.domain + '/static/' + settings.LOGO_URL
    context['vendor'] = vendor

    # create pdf body
    template = get_template('dashboard/orders/invoices/order_invoice_product.html')
    html = template.render(context)
    # create pdf body
    try:
        pdfkit.from_string(
            html, pdf_path, options=options
        )
    except:
        pass

    return pdf_path


def send_order_summary_invoice(order):

    try:
        invoice_template = 'dashboard/orders/invoices/email_order_summary.html'

        mail_data = {
            'mail_subject': '#%s Order Summary' % (str(order.number)),
            'mail_template': invoice_template,
            'mail_to': [order.user.email],
            'mail_context': {
                'order': order
            },
            'mail_attach': True,
            'mail_attach_file_type': 'application/pdf',
            'mail_attach_file_name': '#%s Order Summary PDF' % (str(order.number)),
            'mail_attach_file': open(order.order_summary_pdf_path(), 'rb').read()
        }

        send_email(**mail_data)

        return True

    except:

        return False


def send_order_invoice(order):

    try:
        invoice_template = 'dashboard/orders/invoices/email_order_invoice.html'

        mail_data = {
            'mail_subject': '#%s Order Invoice' % (str(order.number)),
            'mail_template': invoice_template,
            'mail_to': [order.user.email],
            'mail_context': {
                'order': order
            },
            'mail_attach': True,
            'mail_attach_file_type': 'application/pdf',
            'mail_attach_file_name': '#%s Order Summary PDF' % (str(order.number)),
            'mail_attach_file': open(order.order_invoice_pdf_path(), 'rb').read()
        }

        send_email(**mail_data)

        return True

    except:

        return False


def send_order_ask_feedback_email(order):

    try:
        invoice_template = 'dashboard/orders/invoices/email_ask_feedback.html'

        mail_data = {
            'mail_subject': '#%s Order FeedBack' % (str(order.number)),
            'mail_template': invoice_template,
            'mail_to': [order.user.email],
            'mail_context': {
                'order': order
            }
        }

        send_email(**mail_data)

        return True

    except:

        return False
    