from rest_framework import serializers

import app.models as models


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
