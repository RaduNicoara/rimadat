# Generated by Django 4.2.2 on 2023-06-18 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_pointofinterest_place_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointofinterest',
            name='quiz_completed',
            field=models.BooleanField(default=False),
        ),
    ]
