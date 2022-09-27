# python imports
import requests
# django imports
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.http import HttpResponse


def send_email(**kwargs):

    """
    Method to send emails
    :return:
    """

    try:

        mail_subject = kwargs.get('mail_subject', '')
        mail_template = kwargs.get('mail_template')
        mail_to = kwargs.get('mail_to')
        mail_context = kwargs.get('mail_context')
        mail_attach = kwargs.get('mail_attach')

        mail_attach_file_type = kwargs.get('mail_attach_file_type')
        mail_attach_file_name = kwargs.get('mail_attach_file_name')
        mail_attach_file = kwargs.get('mail_attach_file')

        message = render_to_string(mail_template, mail_context)

        to_email = mail_to
        from_email = settings.FROM_EMAIL_ADDRESS
        email = EmailMessage(mail_subject, message, from_email, to_email)

        if mail_attach:
            email.attach(mail_attach_file_name, mail_attach_file, mail_attach_file_type)

        email.content_subtype = "html"
        email.send()
        print("email in django")

    except Exception as e:
        print('EEEEEEERRROOOOOOOO in MAIL ')
        print(e.args)
        print('EEEEEEERRROOOOOOOO in MAIL ')
        pass

def welcome_mail(request):
    mail_subject = "Welcome Email"
    mail_template = "customer/email/cart_reminder_email.html"
    mail_to = ['m.dhanwate@splendornet.com']
    current_site = Site.objects.get_current()
    mail_context = {
        "user" : "Mayuri",
        'domain': current_site.domain,

    }

    welcome_mail_data ={
        'mail_subject': mail_subject,
        'mail_template': mail_template,
        'mail_to': mail_to,
        'mail_context': mail_context,
    }

    send_email(**welcome_mail_data)
    return HttpResponse('done')


def send_sms(**msg_kwargs):
    """
    Method to send sms
    :param msg_kwargs:
    :return:
    """
    message = msg_kwargs.get('message')
    # For multiple mobile number the mobile number should be comma separated list e.g. mobile_number = '98xxxxxxxx,78xxxxxxxx'
    mobile_number = msg_kwargs.get('mobile_number')
    user = settings.SMS_USER
    pwd = settings.SMS_PASS

    # url = 'http://sms.vndsms.com/vendorsms/pushsms.aspx?user=' + str(user) + '&password=' + str(pwd) + '&msisdn=' + str(mobile_number) + '&sid=VISION&msg=' + str(message) + '&fl=0&gwid=2'
    # url = 'http://dlt.vndsms.com/api/mt/SendSMS?user=' + str(user) + '&password=' + str(pwd) + '&senderid=TRPGMP&channel=Trans&DCS=0&flashsms=0&number=' + str(91)+str(mobile_number) + '&text=' + str(message) + '&peid=1201161131173430752'
    # url = 'http://sms2.vndsms.com/sendsms/bulksms.php?username=takerentpe&password=123456&type=TEXT&sender=TRPGMP&entityId=1201161131173430752&mobile=' + str(91)+str(mobile_number) + '&message='+ str(message)
    
    url = 'http://sms2.vndsms.com/sendsms/bulksms_v2.php?apikey=dGFrZXJlbnRwZTpTc1VUM3E3bA==&type=TEXT&sender=TRPGMP&entityId=1201161131173430752&mobile=' + str(91)+str(mobile_number) + '&message='+ str(message)
    print(url)
    responce = requests.get(url)
    print(responce.content)
    return responce