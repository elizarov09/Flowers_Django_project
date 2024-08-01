# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Получаем email вместо username
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)  # Пытаемся найти пользователя по email
            user_auth = authenticate(request, username=user.username, password=password)  # Аутентификация по username и паролю
            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, f'Добро пожаловать, {user.first_name}!')
                return redirect('home')  # Перенаправление на главную страницу после входа
            else:
                messages.error(request, 'Неправильный логин или пароль')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с такой электронной почтой не найден')
    return render(request, 'accounts/login.html')


from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect('home')
        else:
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
