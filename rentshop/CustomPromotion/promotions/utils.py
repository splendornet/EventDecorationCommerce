# django imports
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


def send_mail_core(**data):

    try:

        mail_subject = data.get('subject')
        to_email = data.get('to_email')
        mail_template = data.get('mail_template')
        mail_context = data.get('mail_context')

        message = render_to_string(mail_template, mail_context)

        to_email = to_email
        from_email = settings.FROM_EMAIL_ADDRESS

        email = EmailMessage(mail_subject, message, from_email, to_email)
        email.content_subtype = "html"
        email.send()

        return True

    except Exception as e:

        return False