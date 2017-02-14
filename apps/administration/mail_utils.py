from django.core.mail import send_mail
from django.template.loader import render_to_string

from MTShowcase import settings


def mail(subject_template,
         mail_template,
         context,
         to_mail=None,
         from_mail=settings.DEFAULT_FROM_EMAIL,
         commit=True):
    subject = render_to_string(subject_template,
                               context)

    subject = ''.join(subject.splitlines())
    message = render_to_string(mail_template,
                               context)
    if commit:
        send_mail(subject, message, from_mail, [to_mail])
    else:
        return subject, message
