# coding: utf8
from django.db    import models
from django.utils import timezone
from control.middleware.config import choices_s
# from dns.models      import cf_account

import datetime, pytz

class TelegramChatGroupTb(models.Model):
    name     = models.CharField(max_length=32, null=False)
    group    = models.CharField(max_length=32, null=False)
    group_id = models.CharField(max_length=32, null=False)
    status   = models.IntegerField(choices=choices_s, default=1)
    class Meta:
        unique_together = ('group' ,'group_id')

    def __str__(self):
        return " | ".join([self.name, self.group, str(self.group_id)])

class TelegramUserIdTb(models.Model):
    user    = models.CharField(max_length=32, null=False)
    name    = models.CharField(max_length=32, null=False)
    user_id = models.IntegerField()
    status  = models.IntegerField(choices=choices_s, default=1)
    class Meta:
        unique_together = ('user' ,'user_id')

    def __str__(self):
        return " | ".join([self.user, self.name, str(self.user_id)])

class DepartmentUserTb(models.Model):
    name   = models.CharField(max_length=32, unique=True, null=False)
    department = models.CharField(max_length=32, unique=False, null=False, default="未知组")
    user   = models.ManyToManyField(TelegramUserIdTb, blank=False, db_constraint=False)
    status = models.IntegerField(choices=choices_s, default=1)

    class Meta:
        unique_together = ('name' ,'department')

    def __str__(self):
        users = ""
        for i in self.user.filter(status=1).all():
            users += i.name + " "
        return " | ".join([self.name, self.department, users])

    def AtUsers(self):
        users = []
        for i in self.user.filter(status=1).all():
            users.append("@" + i.user)
        return ", ".join(users)

    def display(self):
        users = []
        for i in self.user.filter(status=1).all():
            users.append(i.name)
        return ", ".join(users)