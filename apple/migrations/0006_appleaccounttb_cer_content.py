# Generated by Django 2.2.5 on 2020-01-12 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0005_auto_20200112_0644'),
    ]

    operations = [
        migrations.AddField(
            model_name='appleaccounttb',
            name='cer_content',
            field=models.IntegerField(null=True, verbose_name='证书 详情'),
        ),
    ]
