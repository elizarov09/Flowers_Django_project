# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Электронная почта")
    first_name = forms.CharField(max_length=30, required=True, label="Имя")
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия")
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Формат номера: '+999999999'. До 15 цифр.")
    phone_number = forms.CharField(validators=[phone_regex], max_length=17, required=True, label="Телефонный номер")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']
        field_classes = {'email': forms.EmailField}

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # Удаление подсказок для всех полей
        for fieldname in ['email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
