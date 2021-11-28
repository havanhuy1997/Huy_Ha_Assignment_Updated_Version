import csv

import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "huy.settings")
django.setup()

from app.models import Sale, City, Country, User

user1 = User.objects.get(id=1)
user2 = User.objects.get(id=2)

with open("products.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        Sale.objects.create(
            user=user1,
            date=row["date"],
            product=row["product"],
            sales_number=int(row["sales_number"]),
            revenue=float(row["revenue"]),
        )
        Sale.objects.create(
            user=user2,
            date=row["date"],
            product=row["product"],
            sales_number=int(row["sales_number"]),
            revenue=float(row["revenue"]),
        )

with open("city.csv") as f:
    for row in f.readlines():
        row = row.strip()
        row_split = row.split()
        country = row_split[-1]
        country_obj = Country.objects.filter(name=country).first()
        city = " ".join(row_split[0:-1])
        if not country_obj:
            country_obj = Country.objects.create(name=country)
        City.objects.create(name=city, country=country_obj)
        print("Created city", city)
