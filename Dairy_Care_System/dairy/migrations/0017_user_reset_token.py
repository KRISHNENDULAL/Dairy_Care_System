# Generated by Django 5.1 on 2024-09-05 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0016_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]