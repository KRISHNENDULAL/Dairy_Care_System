# Generated by Django 5.1 on 2024-12-18 09:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0071_notifications_table_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animals_table',
            name='animal_category',
        ),
    ]