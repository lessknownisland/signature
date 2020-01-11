# Generated by Django 2.2.5 on 2020-01-10 07:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroupPermissionsTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='组名')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
            ],
        ),
        migrations.CreateModel(
            name='WebUriTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='接口名称')),
                ('uri', models.CharField(blank=True, default='', max_length=128, verbose_name='接口路径')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
            ],
        ),
        migrations.CreateModel(
            name='WebUriThirdLevelTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='html title')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='第三级路由名')),
                ('jump', models.CharField(blank=True, default='', max_length=128, verbose_name='跳转路由')),
                ('icon', models.CharField(blank=True, default='', max_length=32, verbose_name='layui图标')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
            ],
        ),
        migrations.CreateModel(
            name='WebUriSecondLevelTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='html title')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='第二级路由名')),
                ('jump', models.CharField(blank=True, default='', max_length=128, verbose_name='跳转路由')),
                ('icon', models.CharField(blank=True, default='', max_length=32, verbose_name='layui图标')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
                ('next_l', models.ManyToManyField(blank=True, db_constraint=False, to='control.WebUriThirdLevelTb', verbose_name='下一层路由')),
            ],
        ),
        migrations.CreateModel(
            name='WebUriFirstLevelTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='html title')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='第一级路由名')),
                ('jump', models.CharField(blank=True, default='', max_length=128, verbose_name='跳转路由')),
                ('icon', models.CharField(blank=True, default='', max_length=32, verbose_name='layui图标')),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1, verbose_name='是否启用')),
                ('next_l', models.ManyToManyField(blank=True, db_constraint=False, to='control.WebUriSecondLevelTb', verbose_name='下一层路由')),
            ],
        ),
        migrations.CreateModel(
            name='UserPermissionsTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('usergroup_p', models.ManyToManyField(blank=True, to='control.UserGroupPermissionsTb', verbose_name='路由组权限')),
                ('weburi_p', models.ManyToManyField(blank=True, to='control.WebUriTb', verbose_name='接口权限')),
                ('weburifirst_l', models.ManyToManyField(blank=True, to='control.WebUriFirstLevelTb', verbose_name='第一级路由权限')),
                ('weburisecond_l', models.ManyToManyField(blank=True, to='control.WebUriSecondLevelTb', verbose_name='第二级路由权限')),
                ('weburithird_l', models.ManyToManyField(blank=True, to='control.WebUriThirdLevelTb', verbose_name='第三级路由权限')),
            ],
        ),
        migrations.AddField(
            model_name='usergrouppermissionstb',
            name='weburi_p',
            field=models.ManyToManyField(blank=True, to='control.WebUriTb', verbose_name='接口权限'),
        ),
        migrations.AddField(
            model_name='usergrouppermissionstb',
            name='weburifirst_l',
            field=models.ManyToManyField(blank=True, to='control.WebUriFirstLevelTb', verbose_name='第一级路由权限'),
        ),
        migrations.AddField(
            model_name='usergrouppermissionstb',
            name='weburisecond_l',
            field=models.ManyToManyField(blank=True, to='control.WebUriSecondLevelTb', verbose_name='第二级路由权限'),
        ),
        migrations.AddField(
            model_name='usergrouppermissionstb',
            name='weburithird_l',
            field=models.ManyToManyField(blank=True, to='control.WebUriThirdLevelTb', verbose_name='第三级路由权限'),
        ),
    ]
