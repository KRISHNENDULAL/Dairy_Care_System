# Generated by Django 5.1 on 2024-09-20 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0017_user_reset_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('customer', 'Customer'), ('employee', 'Employee')], default='admin', max_length=10),
        ),
    ]