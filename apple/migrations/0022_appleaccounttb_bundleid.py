# Generated by Django 2.2.5 on 2020-01-20 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0021_auto_20200120_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='appleaccounttb',
            name='bundleId',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='bundleId'),
        ),
    ]
