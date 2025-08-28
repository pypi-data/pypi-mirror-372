from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views
from . import jwt_views
from .conf import get

app_name = "tlcc_auth"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("sessions/", views.sessions_view, name="sessions"),
    path("sessions/revoke/", views.revoke_session_view, name="revoke-session"),
    path("sessions/all/", views.sessions_all_view, name="sessions-all"),
    path("password_change/", auth_views.PasswordChangeView.as_view(template_name="tlcc_auth/password_change_form.html"), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="tlcc_auth/password_change_done.html"), name="password_change_done"),
    path("password_reset/", auth_views.PasswordResetView.as_view(email_template_name="tlcc_auth/email/password_reset_email.txt", html_email_template_name="tlcc_auth/email/password_reset_email.html", template_name="tlcc_auth/password_reset_form.html"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="tlcc_auth/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="tlcc_auth/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="tlcc_auth/password_reset_complete.html"), name="password_reset_complete"),
    path("api/", include("tlcc_auth.rest.urls")),
    path("sessions/revoke-all/<int:user_id>/", views.revoke_all_user_sessions_view, name="revoke-all-user-sessions"),
]

if get("ENABLE_JWT"): #jwt erin verwerkt
    try:
        from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
        urlpatterns += [
            path("api/jwt/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
            path("api/jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
            path("api/jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
        ]
        if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS and get("ENABLE_BLACKLIST_UI"):
            urlpatterns += [
                path("tokens/", jwt_views.tokens_view, name="tokens"),
                path("tokens/revoke/<str:jti>/", jwt_views.revoke_token_view, name="revoke-token"),
            ]
    except Exception:
        pass
