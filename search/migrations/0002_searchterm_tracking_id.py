# Generated by Django 2.1.7 on 2020-07-07 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchterm',
            name='tracking_id',
            field=models.CharField(default='', max_length=50),
        ),
    ]
