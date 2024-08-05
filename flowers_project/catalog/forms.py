# catalog/forms.py

from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_date', 'delivery_time']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_time': forms.TimeInput(attrs={'type': 'time'}),
        }
