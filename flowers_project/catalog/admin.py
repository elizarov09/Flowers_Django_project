# catalog/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Flower, CartItem, Order

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('admin-report/', self.admin_view(self.admin_report_redirect), name='admin_report_redirect'),
        ]
        return custom_urls + urls

    def admin_report_redirect(self, request):
        return redirect('admin_report')

    def index(self, request, extra_context=None):
        print("CustomAdminSite.index() called")  # Добавьте эту строку
        extra_context = extra_context or {}
        extra_context['report_link'] = format_html('<a href="{}">Отчет по продажам</a>', '/admin/admin-report/')
        return super().index(request, extra_context=extra_context)

admin_site = CustomAdminSite(name='customadmin')

@admin.register(Flower, site=admin_site)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(CartItem, site=admin_site)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'flower', 'quantity')
    search_fields = ('user__username', 'flower__name')

@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'delivery_address', 'get_status_display', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'delivery_address')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            original_status = Order.objects.get(pk=obj.pk).status
            obj._original_status = original_status
        super().save_model(request, obj, form, change)

# Перерегистрация всех моделей из стандартного admin.site в наш CustomAdminSite
for model, model_admin in admin.site._registry.items():
    if model not in admin_site._registry:
        admin_site.register(model, type(model_admin))