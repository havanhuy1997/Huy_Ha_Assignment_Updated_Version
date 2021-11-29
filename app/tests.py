from django.contrib.auth.models import User
import django.urls as django_url
from django.urls.base import reverse
import rest_framework.test as rest_test
from rest_framework import status
import rest_framework.authtoken.models as authtoken_models

import app.models as models


class NoAuthAPITest(rest_test.APITestCase):
    def setUp(self):
        self.user = models.User.objects.create_user(
            "user1@gmail.com", "user1@gmail.com", "user1_pass"
        )
        self.login_url = django_url.reverse("login")
        self.logout_url = django_url.reverse("logout")

    def test_login(self):
        response = self.client.post(
            self.login_url, {"email": "user1@gmail.com", "password": "user1_pass"}
        )
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue("token" in response.data)
        self.assertEqual(
            response.data["token"],
            authtoken_models.Token.objects.filter(user=self.user).first().key,
        )

    def test_login_with_wrong_data(self):
        response = self.client.post(
            self.login_url, {"email": "user1@gmail.com", "password": "user1_passxxx"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        response = self.client.post(self.logout_url)
        self.assertTrue(response.status_code != status.HTTP_200_OK)

    def test_get_user(self):
        response = self.client.get(f"/user/{self.user.id}/")
        self.assertTrue(response.status_code != status.HTTP_200_OK)

    def test_update_user(self):
        response = self.client.patch(f"/user/{self.user.id}/", {"last_name": "Test"})
        self.assertTrue(response.status_code != status.HTTP_200_OK)


class AuthAPITest(rest_test.APITestCase):
    def setUp(self):
        self.user = models.User.objects.create_user(
            "user1@gmail.com", "user1@gmail.com", "user1_pass"
        )
        self.another_user = models.User.objects.create_user(
            "user2@gmail.com", "user2@gmail.com", "user2_pass"
        )
        self.client.force_authenticate(user=self.user)
        self.sales1 = [
            {
                "date": "2010-2-2",
                "product": "Product1",
                "sales_number": 30,
                "revenue": 2.3,
            },
            {
                "date": "2010-2-2",
                "product": "Product1",
                "sales_number": 20,
                "revenue": 1.3,
            },
            {
                "date": "2010-2-2",
                "product": "Product2",
                "sales_number": 10,
                "revenue": 2.3,
            },
        ]
        self.sales2 = [
            {
                "date": "2010-2-2",
                "product": "Product2",
                "sales_number": 32,
                "revenue": 4.3,
            },
            {
                "date": "2010-2-2",
                "product": "Product3",
                "sales_number": 21,
                "revenue": 0.3,
            },
            {
                "date": "2010-2-2",
                "product": "Product3",
                "sales_number": 11,
                "revenue": 7.3,
            },
        ]
        for sale in self.sales1:
            models.Sale.objects.create(**sale, user=self.user)
        for sale in self.sales2:
            models.Sale.objects.create(**sale, user=self.another_user)

    def test_get_all_sales(self):
        response = self.client.get("/api/v1/sales/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(self.sales1))

    def test_get_sale(self):
        response = self.client.get("/api/v1/sales/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["product"], "Product1")

    def test_update_partial_sale(self):
        response = self.client.patch("/api/v1/sales/1/", {"revenue": 56})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["product"], "Product1")
        self.assertEqual(response.data["revenue"], 56)

    def test_update_sale(self):
        response = self.client.put(
            "/api/v1/sales/1/",
            {
                "date": "2011-2-2",
                "product": "ProductXX",
                "sales_number": 12,
                "revenue": 1.3,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": 1,
                "date": "2011-02-02",
                "product": "ProductXX",
                "sales_number": 12,
                "revenue": 1.3,
                "user_id": self.user.id,
            },
        )

    def test_delete_sale(self):
        response = self.client.delete("/api/v1/sales/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_sale_with_auth_of_another_auth(self):
        self.client.force_authenticate(user=self.another_user)
        response = self.client.put(
            "/api/v1/sales/1/",
            {
                "date": "2011-2-2",
                "product": "ProductXX",
                "sales_number": 12,
                "revenue": 1.3,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sale_statistics(self):
        response = self.client.get(reverse("sale_statistics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            round(response.data["average_sales_for_current_user"], 3), 0.098
        )
        self.assertEqual(round(response.data["average_sale_all_user"], 4), 0.1435)
        self.assertEqual(
            response.data["highest_revenue_sale_for_current_user"],
            {"sale_id": 1, "revenue": 2.3},
        )
        self.assertEqual(
            response.data["product_highest_revenue_for_current_user"],
            {"product_name": "Product1"},
        )
        self.assertEqual(
            response.data["product_highest_sales_number_for_current_user"],
            {"product_name": "Product1"},
        )
