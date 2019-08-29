from django import forms

from djangosqs.apps.website.models import Pizza, Order


class RequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(RequestForm, self).__init__(*args, **kwargs)


class OrderForm(RequestForm):

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        )
    )
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Address"}
        )
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Phone"}
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Email"}
        )
    )

    CHOICES = ((1, "1 pizza"), (2, "2 pizzas"), (3, "3 pizzas"))
    quantity = forms.ChoiceField(
        choices=CHOICES,
        initial="1",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    pizza = forms.ModelChoiceField(
        queryset=Pizza.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Order
        fields = ["name", "address", "phone", "email", "quantity", "pizza"]

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
