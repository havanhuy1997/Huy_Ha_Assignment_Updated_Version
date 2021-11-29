from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

import app.models as models


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), username=email, password=password
            )

            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)

    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "gender",
            "age",
            "country",
            "city",
        ]


class SaleSerializer(serializers.ModelSerializer):
    product = serializers.CharField(required=False)

    class Meta:
        model = models.Sale
        fields = [
            "id",
            "product",
            "revenue",
            "sales_number",
            "date",
            "user_id",
        ]

    def create(self, validated_data):
        return models.Sale.objects.create(
            **validated_data, user=self.context["request"].user
        )


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = [
            "id",
            "name",
        ]


class CountrySerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = models.Country
        fields = [
            "id",
            "name",
            "cities",
        ]
