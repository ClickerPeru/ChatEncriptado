# Generated by Django 4.1.3 on 2022-11-23 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_chat', '0002_alter_chat_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='aceptado',
            field=models.BooleanField(default=False, max_length=250, null=True),
        ),
    ]