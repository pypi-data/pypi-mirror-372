from django.contrib.sessions.models import Session
from django.utils import timezone

def sessions_for_user(user_id): #sessie decoden en dan filteren per user.id
    sessions = []
    for s in Session.objects.filter(expire_date__gt=timezone.now()):
        try:
            data = s.get_decoded()
        except Exception:
            continue
        uid = data.get("_auth_user_id")
        if str(uid) == str(user_id):
            sessions.append(s)
    return sessions

def revoke_sessions_for_user(user_id): #elke sessie die matched deleten
    for s in Session.objects.filter(expire_date__gt=timezone.now()):
        try:
            data = s.get_decoded()
        except Exception:
            continue
        if str(data.get("_auth_user_id")) == str(user_id):
            s.delete()
