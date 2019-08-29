from django.contrib import admin

from djangosqs.apps.website.models import Topping, Pizza, Order


class ToppingAdmin(admin.ModelAdmin):
    list_display = ("title",)


admin.site.register(Topping, ToppingAdmin)


class PizzaAdmin(admin.ModelAdmin):
    list_display = ("title", "image", "price")


admin.site.register(Pizza, PizzaAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "email", "pizza", "quantity")


admin.site.register(Order, OrderAdmin)
