from django.conf import settings
import os
import django_rq
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage

from dotenv import load_dotenv
load_dotenv()

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # if file already exists => delete
        if self.exists(name):
            self.delete(name)
        return name


def queue_send_confirm_mail(user, link):
    django_rq.get_queue('default').enqueue(
        send_user_email,
        user,
        subject="Confirm your account",
        template_name="confirm_account",
        link_name="activation_link",
        link_value=link
    )


def queue_send_reset_mail(user, link):
    django_rq.get_queue('default').enqueue(
        send_user_email,
        user,
        subject="Reset your password",
        template_name="reset_password",
        link_name="password_reset_link",
        link_value=link
    )


def queue_send_welcome_mail(user):
    django_rq.get_queue('default').enqueue(
        send_user_email,
        user,
        subject="Welcome to Videoflix",
        template_name="welcome_message",
        link_name="",
        link_value=""
    )


def attach_logo(msg):
    image_path = os.path.join(settings.BASE_DIR, 'app_auth', 'logo', 'app_auth', 'logo_icon.png')
    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read())
        img.add_header('Content-ID', '<logo_cid>')
        img.add_header('Content-Disposition', 'inline', filename='logo_icon.png')
        msg.attach(img)


def send_user_email(user, subject, template_name, link_name, link_value):
    from_email = os.getenv("DEFAULT_FROM_EMAIL")
    site_url = os.getenv("FRONTEND_URL", "http://localhost:8000")

    context = {
        'user': user,
        link_name: link_value,
        'site_url': site_url,
        'logo_cid': 'logo_cid',
    }
    
    # Render text and HTML versions of the email
    text_content = render_to_string(f"{template_name}.txt", context)
    html_content = render_to_string(f"{template_name}.html", context)
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        [user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    attach_logo(msg)
    msg.send(fail_silently=False)