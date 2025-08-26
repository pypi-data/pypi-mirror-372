from django.urls import path

from . import views

app_name = "yarik_django_auth"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("keycloak_callback/", views.keycloak_callback, name="keycloak_callback"),
    path("csrftoken/", views.get_new_csrftoken, name="csrftoken"),
]
