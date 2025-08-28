from django.contrib.auth.views import (
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
    logout_then_login,
)
from django.urls import path, reverse_lazy

app_name = "authplus"
urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="authplus/login.html",
        ),
        name="login",
    ),
    path(
        "logout/",
        logout_then_login,
        name="logout",
    ),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="authplus/password_change.html",
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password_change_done/",
        PasswordChangeDoneView.as_view(
            template_name="authplus/password_change_done.html",
        ),
        name="password_change_done",
    ),
]
