from django.db import models

from zconnect.models import Product


class DemoProduct(Product):
    wiring_mapping = models.ForeignKey("WiringMapping", models.PROTECT, blank=True, null=True)
