# Generated by Django 5.1 on 2024-09-30 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0045_animals_table_animalimages_table_animalhealth_table'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AnimalImages_table',
            new_name='AnimalImages',
        ),
    ]
