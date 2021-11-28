import collections

from django.views.decorators.csrf import csrf_exempt
import django.http as django_htt
import rest_framework.permissions as rest_permissions
import rest_framework.authtoken.views as authtoken_views
import rest_framework.authtoken.models as authtoken_models
import rest_framework.views as rest_views
import rest_framework.decorators as rest_decorators
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import app.models as models
import app.serializers as serializers


class LoginView(authtoken_views.ObtainAuthToken):
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="Login",
        security=[],
        operation_description="Login system. you will get the token from this api, then use this token for next requests to our endpoints",
        request_body=authtoken_views.ObtainAuthToken.serializer_class,
        responses={
            status.HTTP_200_OK: openapi.Response(
                "Get token successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "token": openapi.Schema(type=openapi.TYPE_STRING),
                        "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        },
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = serializers.AuthTokenSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = authtoken_models.Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.id})
        else:
            return Response(
                {"message": "Wrong email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(rest_views.APIView):
    permission_classes = (rest_permissions.IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="Logout",
        operation_description="Logout system. Your token will not be available after this operation",
        responses={
            status.HTTP_200_OK: openapi.Response(
                "Logout successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            )
        },
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"message": "Logout successfully", "success": True})


class UserView(rest_views.APIView):
    """
    Retrieve, update a user instance.
    """

    permission_classes = (rest_permissions.IsAuthenticated,)

    def get_object(self, pk):
        if self.request.user.id == pk:
            try:
                return models.User.objects.get(pk=pk)
            except models.User.DoesNotExist:
                raise django_htt.Http404
        return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"message": "not allowd"}, status=status.HTTP_403_FORBIDDEN)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"message": "not allowd"}, status=status.HTTP_403_FORBIDDEN)
        serializer = serializers.UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaleListView(generics.ListCreateAPIView):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    permission_classes = (rest_permissions.IsAuthenticated,)


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer
    permission_classes = (rest_permissions.IsAuthenticated,)


class CountryListView(generics.ListAPIView):
    queryset = models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    permission_classes = (rest_permissions.IsAuthenticated,)


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes((rest_permissions.IsAuthenticated,))
def get_sale_statistics(request):
    total_number_current, total_revenue_current = 0, 0
    total_number_all, total_revenue_all = 0, 0
    highest_revenue_sale_current = None
    highest_revenue_current = float("-inf")
    product_data = collections.defaultdict(dict)
    for sale in models.Sale.objects.all():
        if sale.user.id == request.user.id:
            # Calculate average_sales_for_current_user
            total_number_current += sale.sales_number
            total_revenue_current += sale.revenue

            # Calcualte highest_revenue_sale_for_current_user
            if sale.revenue > highest_revenue_current:
                highest_revenue_current = sale.revenue
                highest_revenue_sale_current = sale

            # Calculate data for each product
            product = product_data[sale.product]
            product["revenue"] = product.get("revenue", 0) + sale.revenue
            product["number_sold"] = product.get("number_sold", 0) + sale.sales_number
        else:
            total_number_all += sale.sales_number
            total_revenue_all += sale.revenue

    highest_revenue, highest_number = float("-inf"), float("-inf")
    revenue_product, number_product = None, None
    for product_name, data in product_data.items():
        if data["revenue"] > highest_revenue:
            highest_revenue = data["revenue"]
            revenue_product = product_name
        if data["number_sold"] > highest_number:
            highest_number = data["number_sold"]
            number_product = product_name

    return Response(
        {
            "average_sales_for_current_user": total_revenue_current
            / total_number_current,
            "average_sale_all_user": total_revenue_all / total_number_all,
            "highest_revenue_sale_for_current_user": {
                "sale_id": highest_revenue_sale_current.id,
                "revenue": highest_revenue_sale_current.revenue,
            },
            "product_highest_revenue_for_current_user": {
                "product_name": revenue_product
            },
            "product_highest_sales_number_for_current_user": {
                "product_name": number_product
            },
        },
        status=status.HTTP_200_OK,
    )
