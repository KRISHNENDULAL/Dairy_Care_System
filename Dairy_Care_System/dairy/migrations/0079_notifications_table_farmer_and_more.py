# Generated by Django 5.1 on 2025-01-09 03:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0078_alter_notifications_table_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications_table',
            name='farmer',
            field=models.ForeignKey(default=21, on_delete=django.db.models.deletion.CASCADE, to='dairy.users_table'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notifications_table',
            name='product',
            field=models.ForeignKey(default=21, on_delete=django.db.models.deletion.CASCADE, to='dairy.products_table'),
            preserve_default=False,
        ),
    ]