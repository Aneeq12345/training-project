from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from rest_framework.response import Response


class BaseApiView:
    def sucess(data, description, status, errors, format=None):
        return Response({
            "success": True,
            "payload": data,
            "errors": errors,
            "description": description
            },
            status=status)

    def failed(data, description, status, errors, format=None):
        return Response({
            "success": False,
            "payload": data,
            "errors": errors,
            "description": description
            },
            status=status)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token,
                                 *args, **kwargs):

    email_plaintext_message = "token=" + reset_password_token.key

    send_mail(
        # title:
        "Password Reset for {title}".format(title="training-project"),
        # message:
        email_plaintext_message,
        # from:
        "muhammad.aneeq@emumba.com",
        # to:
        [reset_password_token.user.email]
    )
