# Generated by Django 5.0.2 on 2024-03-19 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AdminsID",
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
                ("admin_id", models.BigIntegerField()),
                ("group_id", models.BigIntegerField()),
            ],
            options={
                "verbose_name_plural": "Adminlar",
                "db_table": "admins_id",
            },
        ),
        migrations.CreateModel(
            name="DailyMessages",
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
                ("telegram_id", models.BigIntegerField()),
                ("message_date", models.DateField()),
                ("message_count", models.IntegerField()),
            ],
            options={
                "verbose_name_plural": "Kunlik xabarlar",
                "db_table": "daily_message",
            },
        ),
        migrations.CreateModel(
            name="SupportUsers",
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
                ("full_name", models.CharField(max_length=100)),
                ("username", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "telegram_id",
                    models.BigIntegerField(blank=True, null=True, unique=True),
                ),
            ],
            options={
                "verbose_name_plural": "Foydalanuvchilar",
                "db_table": "support_user",
            },
        ),
    ]
