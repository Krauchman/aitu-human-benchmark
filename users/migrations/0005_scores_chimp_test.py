# Generated by Django 3.1.7 on 2021-03-20 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='scores',
            name='chimp_test',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
