# Generated by Django 5.1 on 2024-11-03 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0064_rename_postcode_zip_address_table_pincode'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address_table',
            old_name='street_address',
            new_name='delivery_address',
        ),
    ]
