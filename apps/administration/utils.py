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


def invite_user(username, inviter, email, project_title):
    """Send an invite mail to a person.

    :param username: the name of the invited person.
    :param inviter: first name or full name of the person who started the invite.
    :param email: the email sending the invite to.
    :param project_title: title of the created project.
    """
    context = {'name': username,
               'inviter': inviter,
               'project_name': project_title,
               'site': settings.SITE,
               'domain': settings.DOMAIN}

    mail('authentication/user_invite_subject.txt', 'authentication/user_invite_mail.txt', context, email)
