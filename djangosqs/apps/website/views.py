from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from djangosqs.apps.website.forms import OrderForm
from djangosqs.apps.website.models import Order
from djangosqs.apps.website.models import Pizza
from djangosqs.apps.website.sqs import Sqs
from djangosqs.settings import MICRO_CONFIG
from djangosqs.settings import TEMPLATE_ID

import datetime


class HomeView(TemplateView):

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["page_title"] = "Order a pizza"
        context["pizzas"] = Pizza.objects.all().order_by("id")

        return context


class OrderView(TemplateView):

    template_name = "order.html"

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        context["page_title"] = "Order a pizza"

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        pizza = Pizza.objects.get(pk=1)
        if "pizza" in kwargs:
            id = int(kwargs["pizza"])
            pizza = Pizza.objects.get(pk=id)

        context["form"] = OrderForm(None, initial={"pizza": pizza})
        return super(OrderView, self).render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = OrderForm(self.request.POST)
        if form.is_valid():
            order = form.save()

            details = []
            quantity = order.quantity
            while quantity > 0:
                details.append(
                    {
                        "description": order.pizza.title,
                        "amount": "{} EUR".format(order.pizza.price),
                    }
                )
                quantity -= 1

            total = order.pizza.price * order.quantity

            message_body = {
                "to": order.email,
                "name": order.name,
                "product_name": "Order a Pizza",
                "receipt_id": "#{}".format(str(order.id).zfill(4)),
                "date": datetime.date.today().strftime("%B %d, %Y"),
                "receipt_details": details,
                "total": "{} EUR".format(total),
                "image": "{}".format(order.pizza.image),
                "action_url": "",
            }

            region_name = str(MICRO_CONFIG["REGION_NAME"])
            queue_name = str(MICRO_CONFIG["STANDARD_QUEUE"])
            dl_queue_name = str(MICRO_CONFIG["DL_QUEUE"])

            sqs = Sqs(
                region_name=region_name,
                queue_name=queue_name,
                dl_queue_name=dl_queue_name,
                template_id=TEMPLATE_ID,
            )
            sqs.send_message(message_body)

            return HttpResponseRedirect(reverse("website:orders"))

        return super(OrderView, self).render_to_response(context)


class OrdersView(TemplateView):

    template_name = "orders.html"

    def get_context_data(self, **kwargs):
        context = super(OrdersView, self).get_context_data(**kwargs)
        context["page_title"] = "Pizza Orders"
        context["orders"] = Order.objects.all().order_by("id")

        return context
