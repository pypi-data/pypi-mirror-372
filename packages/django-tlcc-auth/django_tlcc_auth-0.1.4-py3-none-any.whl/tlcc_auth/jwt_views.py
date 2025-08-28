from django.shortcuts import redirect, render
# from django.contrib.auth.decorators import login_required
from django.conf import settings
from .conf import get
from django.contrib.admin.views.decorators import staff_member_required
def has_blacklist():
    return "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS

@staff_member_required 
def tokens_view(request): #tonen welke tokens op blacklist en pagina met outstandings jwts (met jwt enabled )
    if not get("ENABLE_JWT") or not has_blacklist():
        return redirect("tlcc_auth:profile")
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
    outstanding = OutstandingToken.objects.filter(user=request.user).order_by("-created_at")

    blacklisted_ids = set(BlacklistedToken.objects.values_list("token_id", flat=True))
    return render(request, "tlcc_auth/tokens.html", {"outstanding": outstanding, "blacklisted_ids": blacklisted_ids})

@staff_member_required
def revoke_token_view(request, jti): #blacklisten van een bepaalde token identifier (jti?) #TODO duidelijkere errors
    if not get("ENABLE_JWT") or not has_blacklist():
        return redirect("tlcc_auth:profile")
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
    try:
        token = OutstandingToken.objects.get(jti=jti, user=request.user)
        BlacklistedToken.objects.get_or_create(token=token)
    except OutstandingToken.DoesNotExist:
        pass
    return redirect("tlcc_auth:tokens")
