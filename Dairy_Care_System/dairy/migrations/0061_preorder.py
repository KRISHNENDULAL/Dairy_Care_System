# Generated by Django 5.1 on 2024-10-26 04:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0060_products_table_product_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('additional_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dairy.products_table')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dairy.users_table')),
            ],
        ),
    ]