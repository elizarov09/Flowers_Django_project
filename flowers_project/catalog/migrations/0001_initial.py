# Generated by Django 5.0.7 on 2024-08-01 11:58

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Flower",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Название")),
                ("description", models.TextField(verbose_name="Описание")),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Цена"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="flowers/",
                        verbose_name="Изображение",
                    ),
                ),
            ],
        ),
    ]