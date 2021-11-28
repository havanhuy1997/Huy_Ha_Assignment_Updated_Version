from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import rest_framework.permissions as rest_permissions

from . import views

api_url_patterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("user/<int:pk>/", views.UserView.as_view(), name="user"),
]

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="API Description",
        contact=openapi.Contact(email="havanhuy1997@gmail.com"),
    ),
    url="https://localhost:8000/api/v1",
    public=True,
    patterns=api_url_patterns,
)

urlpatterns = api_url_patterns + [
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="docs"),
]
