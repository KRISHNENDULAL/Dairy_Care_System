# Generated by Django 5.1 on 2024-11-18 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0067_rename_district_address_table_place'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users_table',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('customer', 'Customer'), ('employee', 'Employee'), ('farm owner', 'Farm Owner')], max_length=10),
        ),
    ]