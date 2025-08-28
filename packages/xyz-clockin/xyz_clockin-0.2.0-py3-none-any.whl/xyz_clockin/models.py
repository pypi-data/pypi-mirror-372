# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.auth.models import User
from xyz_util import modelutils
from datetime import datetime


class Project(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "计划"
        unique_together = ('creator', 'name')

    creator = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name='clockin_projects',
                                on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=64)
    is_active = models.BooleanField('有效', default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "小组"
        unique_together = ('project', 'name')

    project = models.ForeignKey(Project, verbose_name=Project._meta.verbose_name, related_name='groups',
                                blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=64)
    is_active = models.BooleanField('有效', default=True)
    is_free = models.BooleanField('自由打卡', default=False)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def __str__(self):
        return self.name

    def reload_items_names(self):
        for s in self.sessions.all():
            s.reload_items_names()

    def get_all_items(self):
        from django.contrib.contenttypes.models import ContentType
        rs = []
        for s in self.sessions.filter(is_active=True).values('items'):
            for d in s['items']:
                for item in d['items']:
                    ct = ContentType.objects.get_by_natural_key(*item['model'].split('.'))
                    rs.append((ct.id, item['id']))
        return rs

    def get_results(self):
        from xyz_dailylog.stores import UserLog
        ul = UserLog()
        fs = dict([('ct%s.%s' % a, 1) for a in self.get_all_items()])
        fs['_id'] = 0
        ids = list(self.memberships.values_list('user_id', flat=True))
        fs['id'] = 1
        return list(ul.collection.find({'id': {'$in': ids}}, fs))

    def clone_sessions(self, qset):
        for s in qset.all():
            s.group = self
            s.items = []
            s.id = None
            s.save()

    def get_old_membership_user_ids(self):
        def get_ids(g):
            return set(g.memberships.values_list('user_id', flat=True))

        ids = get_ids(self)
        oids = set()
        for g in self.project.groups.filter(create_time__lt=self.create_time):
            oids.update(get_ids(g))
        return ids.intersection(oids)

    def exam_answers(self):
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(Project)
        from xyz_exam.models import Paper, Answer
        ouids = self.get_old_membership_user_ids()
        pids = list(Paper.objects.filter(owner_type=ct, owner_id=self.project_id).values_list('id', flat=True))
        answers = Answer.objects.filter(
            paper_id__in=pids,
            user_id__in=ouids,
            create_time__gt=self.create_time
        )
        from xyz_util.statutils import group_by
        from django.db.models import Max
        ups = group_by(answers, ['user_id', 'paper_id'], measures=[Max('std_score')])
        from xyz_dailylog.stores import UserLog
        st = UserLog()
        ctpid = ContentType.objects.get_for_model(Paper).id
        huids = set()
        for uid, pid, score in ups:
            huids.add(uid)
            st.upsert({'id': uid}, {'ct%s.%s.quiz_score' % (ctpid, pid): score})

        # print(pids, ouids, self.create_time)
        # return answers

    def clear_old_group_membership(self):
        ogids = list(self.project.groups.filter(create_time__lt=self.create_time).values_list('id', flat=True))
        return MemberShip.objects.filter(group_id__in=ogids).exclude(group=self).update(is_active=False)


class MemberShip(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "成员"
        unique_together = ('group', 'user')

    group = models.ForeignKey(Group, verbose_name=Group._meta.verbose_name, related_name='memberships',
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name='clockin_memberships',
                             on_delete=models.PROTECT)
    user_name = models.CharField('用户姓名', max_length=64)
    is_active = models.BooleanField('有效', default=True)
    is_free = models.BooleanField('自由打卡', default=False)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def __str__(self):
        return "%s@%s" % (self.user_name, self.group)

    def clear_old_group_membership(self):
        ogids = self.group.project.groups.filter(create_time__lt=self.group.create_time).values_list('id', flat=True)
        return self.user.clockin_memberships.filter(group_id__in=ogids).exclude(group=self.group).update(is_active=False)

    def save(self, **kwargs):
        if self.is_free is None and self.group:
            self.is_free = self.group.is_free
        super(MemberShip, self).save(**kwargs)


class Session(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "周期"

    group = models.ForeignKey(Group, verbose_name=Group._meta.verbose_name, related_name='sessions',
                              on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=64, blank=True, default='第一期')
    number = models.PositiveIntegerField('序号', default=1)
    is_active = models.BooleanField('有效', default=True)
    begin_time = models.DateTimeField("开始时间", blank=True, null=True)
    end_time = models.DateTimeField("结束时间", blank=True, null=True)
    items = modelutils.JSONField('项目', blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def save(self, **kwargs):
        if not self.name:
            self.name = '第%s期' % self.number
        from datetime import datetime, timedelta
        if not self.begin_time:
            self.begin_time = datetime.now()
        if not self.end_time:
            self.end_time = self.begin_time + timedelta(days=7)
        if not self.items:
            self.items = []
        super(Session, self).save(**kwargs)

    def reload_items_names(self):
        from django.contrib.contenttypes.models import ContentType
        for d in self.items:
            for item in d['items']:
                ct = ContentType.objects.get_by_natural_key(*item['model'].split('.'))
                obj = ct.get_object_for_this_type(id=item['id'])
                item['name'] = obj.__str__()
                print(item)
        self.save()

    def __str__(self):
        return "%s%s" % (self.group, self.name)


class Point(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "成绩"

    group = models.ForeignKey(Group, verbose_name=Group._meta.verbose_name, related_name='points',
                              on_delete=models.PROTECT)
    session = models.ForeignKey(Session, verbose_name=Session._meta.verbose_name, related_name='points',
                                on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name='clockin_points',
                             on_delete=models.PROTECT)
    value = models.PositiveIntegerField('积分', blank=True, null=True, default=0)
    detail = modelutils.JSONField('详情', blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def __str__(self):
        return '%s:%d分@%s' % (self.user, self.value, self.group)

    def save(self, **kwargs):
        if self.detail is None:
            self.detail = {}
        super(Point, self).save(**kwargs)
