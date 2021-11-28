from django.views.decorators.csrf import csrf_exempt
import django.http as django_htt
import rest_framework.permissions as rest_permissions
import rest_framework.authtoken.views as authtoken_views
import rest_framework.authtoken.models as authtoken_models
import rest_framework.views as rest_views
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
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = authtoken_models.Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.id})
        else:
            return Response(
                {"message": "Wrong username or password"},
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
