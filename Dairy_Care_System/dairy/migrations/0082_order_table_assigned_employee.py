# Generated by Django 5.1 on 2025-01-22 14:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0081_alter_users_table_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_table',
            name='assigned_employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to='dairy.users_table'),
        ),
    ]
