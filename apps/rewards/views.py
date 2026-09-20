from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import CoinWallet


@login_required
def wallet(request):

    if not request.user.is_citizen:
        messages.error(
            request,
            "The rewards wallet is available only to citizens."
        )

        return redirect("users:dashboard")

    wallet, created = CoinWallet.objects.get_or_create(
        citizen=request.user
    )

    transactions = wallet.transactions.select_related(
        "issue"
    ).all()

    context = {
        "wallet": wallet,
        "transactions": transactions,
    }

    return render(
        request,
        "rewards/wallet.html",
        context
    )