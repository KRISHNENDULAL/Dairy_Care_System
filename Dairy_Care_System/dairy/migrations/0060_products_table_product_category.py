# Generated by Django 5.1 on 2024-10-21 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0059_notifications_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='products_table',
            name='product_category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]