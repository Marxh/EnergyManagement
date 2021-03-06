# Generated by Django 2.1.4 on 2019-05-28 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LineDetection', '0008_auto_20190518_0335'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_name', models.CharField(default='', max_length=200, null=True)),
                ('article', models.CharField(default='', max_length=2000, null=True)),
                ('pub_date', models.DateTimeField(verbose_name='article date')),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_text', models.CharField(default='', max_length=200, null=True)),
            ],
            options={
                'verbose_name': '标签',
                'verbose_name_plural': '标签',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='tag_on',
            field=models.ManyToManyField(blank=True, to='LineDetection.Tag'),
        ),
    ]
