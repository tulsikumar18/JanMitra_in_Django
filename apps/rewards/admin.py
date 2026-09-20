from django.contrib import admin

# Register your models here.


from django.contrib import admin

from .models import CoinWallet, CoinTransaction


@admin.register(CoinWallet)
class CoinWalletAdmin(admin.ModelAdmin):

    list_display = (
        "citizen",
        "balance",
        "total_earned",
        "total_redeemed",
        "updated_at",
    )

    search_fields = (
        "citizen__email",
        "citizen__first_name",
        "citizen__last_name",
    )


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "wallet",
        "transaction_type",
        "coins",
        "issue",
        "created_at",
    )

    list_filter = (
        "transaction_type",
    )

    search_fields = (
        "wallet__citizen__email",
        "description",
    )