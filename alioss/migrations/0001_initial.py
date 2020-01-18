# Generated by Django 2.2.5 on 2020-01-17 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AliossBucketTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bucket_name', models.CharField(max_length=64, verbose_name='存储桶 名称')),
                ('access_keyid', models.CharField(max_length=128, verbose_name='账号 keyid')),
                ('access_keysecret', models.CharField(max_length=128, verbose_name='账号 keysecret')),
                ('main_host', models.CharField(max_length=128, verbose_name='Bucket 主域名')),
                ('vpc_host', models.CharField(max_length=128, null=True, verbose_name='Bucket 内网域名')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
            ],
        ),
    ]