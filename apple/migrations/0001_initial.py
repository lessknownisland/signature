# Generated by Django 2.2.5 on 2020-01-11 09:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppleAccountTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=64, unique=True, verbose_name='账号邮箱')),
                ('count', models.IntegerField(verbose_name='账号签名所剩设备数')),
                ('p8', models.TextField(verbose_name='p8证书')),
                ('iss', models.TextField(verbose_name='issue ID')),
                ('kid', models.TextField(verbose_name='key ID')),
                ('cer_id', models.CharField(max_length=64, unique=True, verbose_name='证书 ID')),
                ('bundleid', models.CharField(max_length=64, unique=True, verbose_name='bundle ID')),
                ('p12', models.CharField(max_length=128, unique=True, verbose_name='bundle ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='生成的日期')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
            ],
        ),
    ]
