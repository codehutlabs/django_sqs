from django.db import models


class Topping(models.Model):

    title = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.title


class Pizza(models.Model):

    title = models.CharField(max_length=255, blank=False, null=False)
    image = models.FileField(upload_to="uploads", blank=True, null=True)
    toppings = models.ManyToManyField(Topping, blank=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.title


class Order(models.Model):

    name = models.CharField(max_length=255, blank=False, null=False)
    address = models.CharField(max_length=255, blank=False, null=False)
    phone = models.CharField(max_length=255, blank=False, null=False)
    email = models.CharField(max_length=255, blank=False, null=False)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, null=False)
