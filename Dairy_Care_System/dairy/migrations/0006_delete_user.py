# Generated by Django 5.1 on 2024-08-29 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0005_alter_user_role'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
