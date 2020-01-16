# Generated by Django 2.2.5 on 2020-01-10 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramUserIdTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=32)),
                ('user_id', models.IntegerField()),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1)),
            ],
            options={
                'unique_together': {('user', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='TelegramChatGroupTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('group', models.CharField(max_length=32)),
                ('group_id', models.CharField(max_length=32)),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1)),
            ],
            options={
                'unique_together': {('group', 'group_id')},
            },
        ),
        migrations.CreateModel(
            name='DepartmentUserTb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('department', models.CharField(default='未知组', max_length=32)),
                ('status', models.IntegerField(choices=[(1, '启用'), (0, '禁用')], default=1)),
                ('user', models.ManyToManyField(db_constraint=False, to='detect.TelegramUserIdTb')),
            ],
            options={
                'unique_together': {('name', 'department')},
            },
        ),
    ]