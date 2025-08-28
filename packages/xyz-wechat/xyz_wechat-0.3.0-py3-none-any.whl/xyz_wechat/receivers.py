# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import receiver
from xyz_util.datautils import access
from xyz_auth.signals import to_get_user_profile
from xyz_saas.signals import to_get_party_settings
from . import serializers, helper, models
from django.conf import settings
from django.db.models.signals import post_save

@receiver(post_save, sender=models.Message)
def set_user_subscribe(sender, **kwargs):
    created = kwargs.get('created')
    if not created:
        return
    message = kwargs.get('instance')
    if message.type != 'event':
        return
    is_unsubscribe = '"Event": "unsubscribe"' in message.content
    is_subscribe = '"Event": "subscribe"' in message.content
    if not (is_subscribe or is_unsubscribe):
        return
    uid = message.from_id
    user = models.User.objects.filter(openid=uid).first()
    if not user:
        return
    if is_subscribe:
        # print(message, user, is_subscribe, user.subscribe_time)
        if user.subscribe_time is None or message.create_time>user.subscribe_time:
            user.subscribe_time = message.create_time
            user.subscribe = True
            user.save()
    elif is_unsubscribe:
        if user.subscribe_time and message.create_time>user.subscribe_time:
            user.subscribe = False
            user.save()



@receiver(to_get_user_profile)
def get_wechat_profile(sender, **kwargs):
    user = kwargs['user']
    if hasattr(user, 'as_wechat_user'):
        return serializers.UserSerializer(user.as_wechat_user, context=dict(request=kwargs['request']))

@receiver(to_get_party_settings)
def get_wechat_settings(sender, **kwargs):
    from django.shortcuts import reverse
    lurl = reverse('wechat:mp:login')
    request = kwargs.get('request')
    t = request.META.get('TENANT_SUBDOMAIN')
    if t:
        lurl = "/%s%s" % (t, lurl)
    lurl = "%s?next=REDIRECT_URL" % lurl
    return {
        'wechat': {
            'oauthUrl': helper.get_wx_oauth_url(access(settings, 'WECHAT.MP.APPID'), request.build_absolute_uri(lurl)),
        }
    }
