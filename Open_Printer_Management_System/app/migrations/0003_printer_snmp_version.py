# Generated by Django 3.0.6 on 2020-05-27 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200518_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='printer',
            name='snmp_version',
            field=models.IntegerField(default=1, verbose_name='SNMP Version'),
        ),
    ]
