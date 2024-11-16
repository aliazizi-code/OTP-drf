import random
import string
import uuid


from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    phone_number = models.CharField(
        max_length=20,  # Adjust based on your needs
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


def generate_otp():
    rand = random.SystemRandom()
    digits = rand.choices(string.digits, k=6)
    return ''.join(digits)


class OTPRequest(models.Model):
    request_id = models.UUIDField(default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=50)
    password = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self, data):
        current_time = timezone.now()
        return OTPRequest.objects.filter(
            request_id=data['request_id'],
            password=data['password'],
            created_at__lt=current_time,
            created_at__gt=current_time - timezone.timedelta(seconds=120),
        ).exists()

    def refresh_otp(self):
        self.created_at = timezone.now()
        self.password = generate_otp()
        self.save()
