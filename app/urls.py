from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

api_url_patterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("user/<int:pk>/", views.UserView.as_view(), name="user"),
    path("sales/", views.SaleListView.as_view()),
    path("sales/<int:pk>/", views.SaleDetailView.as_view()),
    path("countries/", views.CountryListView.as_view(), name="countries"),
    path(
        "sale_statistics/", views.SaleStatisticsView.as_view(), name="sale_statistics"
    ),
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
