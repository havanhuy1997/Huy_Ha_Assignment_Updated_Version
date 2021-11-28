from django.db import models
import django.contrib.auth.models as auth_models


class Country(models.Model):
    name = models.TextField()


class City(models.Model):
    name = models.TextField()
    country = models.ForeignKey(
        Country, related_name="cities", on_delete=models.CASCADE
    )


class User(auth_models.AbstractUser):
    gender = models.TextField(null=True)
    age = models.IntegerField(null=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)


class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    product = models.TextField()
    sales_number = models.IntegerField(default=0)
    revenue = models.FloatField(default=0)
