from django.contrib import auth
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.contrib.sessions.models import Session
from .conf import get
from .forms import RegistrationForm, EmailOrUsernameAuthenticationForm
from .session_utils import sessions_for_user
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from .session_utils import revoke_sessions_for_user
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
def login_view(request):
    Form = EmailOrUsernameAuthenticationForm if get("LOGIN_WITH_EMAIL") else AuthenticationForm ##TODO betere beveiliging
    if request.method == "POST":
        if Form is AuthenticationForm:
            form = Form(request, data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                return redirect(get("POST_LOGIN_REDIRECT"))
        else:
            form = Form(request.POST)
            if form.is_valid():
                user = form.cleaned_data["user"]
                login(request, user)
                return redirect(get("POST_LOGIN_REDIRECT"))
    else:
        form = Form() if Form is not AuthenticationForm else Form(request)
    return render(request, "tlcc_auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(get("POST_LOGOUT_REDIRECT"))

class RegisterView(FormView): #toelatingen van registreren. 
    template_name = "tlcc_auth/register.html"
    form_class = RegistrationForm
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if not get("ALLOW_REGISTRATION"):
            return redirect("tlcc_auth:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        auth.login(self.request, user)
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "tlcc_auth/profile.html"

@login_required
def sessions_view(request): #toont of bewerken profiel
    sessions = sessions_for_user(request.user.id)
    return render(request, "tlcc_auth/sessions.html", {"sessions": sessions})

@require_POST
@login_required
def revoke_session_view(request): #gebruikers uitloggen met sessions
    session_key = request.POST.get("session_key")
    if not session_key:
        return redirect("tlcc_auth:sessions")
    owner_sessions = {s.session_key for s in sessions_for_user(request.user.id)}
    if session_key in owner_sessions or request.user.is_staff:
        if request.session.session_key == session_key:
            request.session.flush()
        Session.objects.filter(session_key=session_key).delete()
    return redirect("tlcc_auth:sessions")


@staff_member_required
def sessions_all_view(request): #alle active sessions en users erbij zetten. Voor admins
    rows = []
    qs = Session.objects.all().order_by("-expire_date")
    for s in qs:
        try:
            data = s.get_decoded()
        except Exception:
            data = {}
        uid = data.get("_auth_user_id")
        username = None
        if uid:
            try:
                username = get_user_model().objects.get(pk=uid).get_username()
            except get_user_model().DoesNotExist:
                username = None
        rows.append({
            "session_key": s.session_key,
            "expire_date": s.expire_date,
            "uid": uid,
            "username": username or "Anonymous",
            "data": data,
        })
    return render(request, "tlcc_auth/sessions_admin.html", {"rows": rows})



@require_POST
@staff_member_required
def revoke_all_user_sessions_view(request, user_id):
    user = get_object_or_404(get_user_model(), pk=user_id)
    revoke_sessions_for_user(user.id)
    messages.success(request, f"Revoked sessions for {user.get_username()}")
    return redirect("tlcc_auth:sessions-all")
