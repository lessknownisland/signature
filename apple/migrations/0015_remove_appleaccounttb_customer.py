# Generated by Django 2.2.5 on 2020-01-18 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0014_appleaccounttb_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appleaccounttb',
            name='customer',
        ),
    ]
