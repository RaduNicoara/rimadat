# Generated by Django 4.2.2 on 2023-06-17 14:17

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_adventure_pointofinterest_delete_entity'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatconversation',
            name='created_at',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='conversationmessage',
            name='created_at',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='conversationmessage',
            name='conversation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='core.chatconversation'),
        ),
    ]