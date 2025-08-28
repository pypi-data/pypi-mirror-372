# -*- coding:utf-8 -*- 
from __future__ import unicode_literals
from django.db import models
from . import choices
from django.contrib.auth.models import User as SiteUser
from xyz_util import modelutils


class Message(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = '消息'

    to_id = models.CharField("接收者ID", max_length=64)
    from_id = models.CharField("发送者ID", max_length=64)
    create_time = models.DateTimeField("创建时间", editable=False, auto_now_add=True, db_index=True)
    type = models.CharField('类别', max_length=16, choices=choices.CHOICES_MESSAGE_TYPE,
                            default=choices.MESSAGE_TYPE_TEXT)
    msg_id = models.BigIntegerField('编号', blank=True, null=True)
    content = models.TextField('内容', blank=True, null=True)

    def __str__(self):
        return "%s:%s:%s" % (self.create_time, self.to_id, self.from_id)


class User(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = '用户'
        ordering = ('-subscribe_time',)

    user = models.OneToOneField(SiteUser, verbose_name="网站用户", null=True, on_delete=models.PROTECT,
                                related_name="as_wechat_user")
    openid = models.CharField("openId", max_length=64, primary_key=True)
    unionid = models.CharField("unionId", max_length=64, null=True, blank=True)
    nickname = models.CharField("昵称", max_length=128, null=True, blank=True)
    headimgurl = models.CharField("头像", max_length=255, null=True, blank=True)
    city = models.CharField("城市", max_length=128, null=True, blank=True)
    province = models.CharField("省份", max_length=128, null=True, blank=True)
    country = models.CharField("国家", max_length=128, blank=True, default="中国")
    sex = models.CharField("性别", max_length=2, null=True, blank=True, choices=choices.CHOICES_GENDER)
    longitude = models.FloatField("经度", null=True, blank=True)
    latitude = models.FloatField("纬度", null=True, blank=True)
    subscribe = models.BooleanField("订阅", blank=True, default=False)
    subscribe_time = models.DateTimeField("订阅时间", blank=True, null=True, db_index=True)
    subscribe_scene = models.CharField("关注渠道", max_length=32, blank=True, default="ADD_SCENE_QR_CODE")
    qr_scene = models.PositiveIntegerField("扫码场景", blank=True, null=True)
    qr_scene_str = models.CharField("扫码场景描述", max_length=32, blank=True, default="")
    remark = models.CharField("备注", max_length=255, blank=True, default="")
    tagid_list = modelutils.JSONField("标签ID列表", blank=True, default=[])
    groupid = models.PositiveIntegerField("分组ID", blank=True, default=0)
    language = models.CharField("语言", max_length=16, blank=True, default="zh_CN")
    create_time = models.DateTimeField("创建时间", editable=False, auto_now_add=True, db_index=True)

    def __str__(self):
        return self.nickname or self.openid

    def save(self, **kwargs):
        from xyz_util.datautils import filter_emoji
        if self.nickname:
            self.nickname = filter_emoji(self.nickname)
        if self.subscribe_time is None:
            self.subscribe_time = self.create_time
        if self.user is None:
            user_name = "%s@wechat" % self.openid[-10:]
            ms = SiteUser._meta.get_field('first_name').max_length
            from xyz_util.datautils import trim_by_length
            name = trim_by_length(self.nickname, ms)
            self.user, created = SiteUser.objects.get_or_create(username=user_name,
                                                                defaults=dict(email="", first_name=name))
        return super(User, self).save(**kwargs)
