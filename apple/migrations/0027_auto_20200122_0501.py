# Generated by Django 2.2.5 on 2020-01-22 05:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0026_packageistalledtb_package_version'),
    ]

    operations = [
        migrations.RenameField(
            model_name='packageistalledtb',
            old_name='device_id',
            new_name='device_udid',
        ),
    ]