# Generated by Django 2.1.4 on 2019-05-13 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LineDetection', '0002_auto_20190511_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='facility',
            name='energy_total',
            field=models.FloatField(default=0),
        ),
    ]
