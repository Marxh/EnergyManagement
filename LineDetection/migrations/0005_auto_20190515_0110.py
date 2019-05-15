# Generated by Django 2.1.4 on 2019-05-15 01:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LineDetection', '0004_production_amount_production_goal'),
    ]

    operations = [
        migrations.CreateModel(
            name='season_goal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.IntegerField(default=0)),
                ('production_line', models.IntegerField(default=0)),
                ('goal', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='production_goal',
            name='facility',
        ),
        migrations.RemoveField(
            model_name='production_amount',
            name='facility',
        ),
        migrations.AddField(
            model_name='production_amount',
            name='production_line',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='production_amount',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LineDetection.season_goal'),
        ),
        migrations.DeleteModel(
            name='production_goal',
        ),
    ]