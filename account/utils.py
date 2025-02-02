from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from .tasks import send_email_task


def send_welcome_email(user, request):
    subject = "به وب‌سایت SwiftOrder خوش آمدید!"
    message = f"سلام {user.first_name} عزیز،\n\nخوشحالیم که به خانواده SwiftOrder پیوسته‌اید. امیدواریم تجربه خوبی از استفاده از پلتفرم ما داشته باشید.\n\nبا احترام,\nتیم SwiftOrder"
    send_email_task.delay(subject, message, [user.email])


def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    link = f"{get_current_site(request).domain}/account//verify-email/{uid}/{token}/"

    subject = "Verify your email address"
    message = f"Click the link to verify your email: {link}"

    send_email_task.delay(subject, message, [user.email])


def send_password_reset_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    reset_link = (
        f"{get_current_site(request).domain}/account/reset-password/{uid}/{token}/"
    )

    subject = "بازنشانی رمز عبور"
    message = f"""
    سلام،

    درخواست بازنشانی رمز عبور شما در سایت ما دریافت شده است.

    برای بازنشانی رمز عبور خود، لطفاً روی لینک زیر کلیک کنید:

    {reset_link}

    اگر شما درخواست بازنشانی رمز عبور نکرده‌اید، لطفاً این ایمیل را نادیده بگیرید.

    با تشکر،
    تیم پشتیبانی
    """

    send_email_task.delay(subject, message, [user.email])
