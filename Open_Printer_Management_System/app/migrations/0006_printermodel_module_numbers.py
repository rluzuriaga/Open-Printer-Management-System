# Generated by Django 3.0.6 on 2020-06-22 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_printermodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='printermodel',
            name='module_numbers',
            field=models.IntegerField(default=1, verbose_name='Number of modules'),
        ),
    ]