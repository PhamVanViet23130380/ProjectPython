from django.db import models
from django.conf import settings


class Verification(models.Model):
    code = models.CharField(max_length=10, unique=True)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    expired_at = models.DateTimeField(null=True)
    verify_type = models.CharField(max_length=5, choices=(('phone', 'Phone'), ('email', 'Email')))

    def __str__(self):
        return f"Verification {self.code} for {self.account.email}"

    class Meta:
        db_table = 'verifications'
        verbose_name = 'Xác thực'
        verbose_name_plural = 'Xác thực'
