from django.http import HttpRequest
from django.contrib.sessions.models import Session


def clear_previos_sessions(request: HttpRequest):
    sessions = Session.objects.order_by("-expire_date")
    for session in sessions:
        session_data_decoded = session.get_decoded()
        if "_auth_user_id" in session_data_decoded and int(
            session_data_decoded["_auth_user_id"]
        ) == int(request.user.id):
            session.delete()
