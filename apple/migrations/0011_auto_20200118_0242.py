# Generated by Django 2.2.5 on 2020-01-18 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0010_auto_20200118_0223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appleaccounttb',
            name='bundleid',
            field=models.CharField(max_length=64, null=True, verbose_name='bundle ID'),
        ),
        migrations.AlterField(
            model_name='appleaccounttb',
            name='cer_id',
            field=models.CharField(max_length=64, null=True, verbose_name='证书 ID'),
        ),
        migrations.AlterField(
            model_name='appleaccounttb',
            name='count',
            field=models.IntegerField(default=0, verbose_name='账号签名所剩设备数'),
        ),
        migrations.AlterField(
            model_name='appleaccounttb',
            name='p12',
            field=models.CharField(max_length=128, null=True, verbose_name='p12 文件名'),
        ),
    ]
