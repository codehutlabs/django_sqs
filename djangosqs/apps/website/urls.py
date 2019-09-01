from django.urls import path
from djangosqs.apps.website.views import HomeView
from djangosqs.apps.website.views import OrdersView
from djangosqs.apps.website.views import OrderView

app_name = "website"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("order/", OrderView.as_view(), name="order"),
    path("order/<int:pizza>/", OrderView.as_view(), name="order"),
    path("orders/", OrdersView.as_view(), name="orders"),
]
