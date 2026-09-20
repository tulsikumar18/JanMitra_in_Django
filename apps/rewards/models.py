
from django.conf import settings
from django.db import models

from apps.issues.models import Issue


class CoinWallet(models.Model):

    citizen = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coin_wallet"
    )

    balance = models.PositiveIntegerField(
        default=0
    )

    total_earned = models.PositiveIntegerField(
        default=0
    )

    total_redeemed = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.citizen.get_full_name()} - {self.balance} coins"


class CoinTransaction(models.Model):

    class TransactionType(models.TextChoices):

        EARNED = "earned", "Earned"

        REDEEMED = "redeemed", "Redeemed"


    wallet = models.ForeignKey(
        CoinWallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )

    coins = models.PositiveIntegerField()

    issue = models.OneToOneField(
        Issue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coin_transaction"
    )

    description = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        ordering = ["-created_at"]


    def __str__(self):

        return (
            f"{self.transaction_type} - "
            f"{self.coins} coins"
        )