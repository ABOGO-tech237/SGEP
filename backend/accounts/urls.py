from django.urls import path

from accounts.views import (
    AdminDashboardView,
    BootstrapView,
    ChangePasswordView,
    LoginView,
    LogoutView,
    RefreshTokenView,
)

urlpatterns = [
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("auth/bootstrap/", BootstrapView.as_view(), name="auth-bootstrap"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
]
