#!/usr/bin/env python   
# -*- coding:utf-8 -*-   
# Author:DenisHuang   
from __future__ import unicode_literals, print_function
import requests, json, hashlib, time
try:
    from urllib.parse import urlparse, urlunparse
    from urllib.request import urlretrieve
except:
    from urlparse import urlparse, urlunparse
    from urllib import urlretrieve

from datetime import datetime
from django.http import QueryDict

from xyz_util import datautils
import logging
from django.contrib.auth.models import User
from . import models
from django.utils.crypto import get_random_string
from django.core.cache import cache

log = logging.getLogger('wechat')

STATE_PREFIX = "WEIXIN_LOGIN"


def clean_state_code(url):
    r = urlparse(url)
    q = QueryDict(r.query, mutable=True)
    if "state" in q and q["state"] == STATE_PREFIX:
        q.pop("state")
        q.pop("code")
    return urlunparse([r[0], r[1], r[2], r[3], q.urlencode(), r[5]])


def get_wx_oauth_url(appid, redirect_uri, scope="snsapi_userinfo", state=""):
    from urllib.parse import quote
    return "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s%s#wechat_redirect" % (
        appid, quote(clean_state_code(redirect_uri)), scope, STATE_PREFIX, state)


class BaseApi(object):
    token_expire_time = 3600
    token_update_timestamp = 0
    token_invalid_codes = (40001,)
    cgi_url = None
    cache_key_format = "WECHAT_%s_%s"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.appid = None
        self.token = self.get_cache("token")
        self.ticket = self.get_cache("ticket")

    def get_cache(self, key):
        return cache.get(self.cache_key_format % (self.appid, key))

    def set_cache(self, key, data):
        return cache.set(self.cache_key_format % (self.appid, key), data)

    def requests_json(self, url):
        r = requests.get(url)
        r.encoding = 'utf8'
        return r.json()

    def get_access_token_url(self):
        raise NotImplementedError()

    def get_access_token(self):
        url = self.get_access_token_url()
        data = self.requests_json(url)
        token = data.get("access_token")
        if not token:
            raise IOError("get_access_token error:%s" % data)
        return token

    def get_jsapi_ticket_url(self):
        raise NotImplementedError()

    def get_jsapi_ticket(self):
        self.update_token()
        url = self.get_jsapi_ticket_url()
        data = self.requests_json(url)
        return data.get('ticket')

    def get_jsapi_params(self, url):
        self.update_ticket()
        d = dict(
            noncestr=get_random_string(32),
            timestamp=int(time.time()),
            jsapi_ticket=self.ticket,
            url=url
        )
        d["signature"] = self.get_signature(d, hash=hashlib.sha1)
        d["appId"] = self.appid
        log.debug(d)
        return d

    def get_signature(self, d, key=None, hash=hashlib.md5):
        ks = d.keys()
        ks.sort()
        s = "&".join(["%s=%s" % (k, d[k]) for k in ks if d[k]])
        if key:
            s = "%s&key=%s" % (s, key)
        signature = hash(s.encode('utf8')).hexdigest().upper()
        return signature

    def update_token(self, at_once=False):
        t = time.time()
        tstamp = self.get_cache("token_tstamp")
        if at_once is False and tstamp and self.token and (t - tstamp < self.token_expire_time):
            return
        self.token = self.get_access_token()
        self.set_cache("token", self.token)
        self.set_cache("token_tstamp", t)

    def update_ticket(self):
        t = time.time()
        tstamp = self.get_cache("ticket_tstamp")
        if tstamp and self.ticket and (t - tstamp < self.token_expire_time):
            return
        self.ticket = self.get_jsapi_ticket()
        self.set_cache("ticket", self.ticket)
        self.set_cache("ticket_tstamp", t)

    def get_or_create_user(self, data):
        openId = data.get("openid")
        user, created = User.objects.update_or_create(
            openId=openId,
            defaults={
                'sex': data.get('sex'),
                'headimgurl': data.get('headimgurl'),
                'nickname': data.get('nickname'),
                'city': data.get('city'),
                'province': data.get('province'),
            })

        return user

    def deal_post(self, postData):
        if not postData:
            return
        from xml.etree import ElementTree

        root = ElementTree.fromstring(postData)
        d = datautils.node2dict(root)

        um = models.Message()
        um.from_id = d.pop('FromUserName')
        um.to_id = d.pop('ToUserName')
        um.create_time = datetime.fromtimestamp(int(d.pop('CreateTime')))
        um.type = d.pop('MsgType')
        um.msg_id = 'MsgId' in d and d.pop('MsgId') or None
        um.content = um.type == "text" and d.get("content") or json.dumps(d)
        um.save()
        return um

    def response_user(self, um):
        s = """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%d</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>
            <Content><![CDATA[%s]]></Content>
            </xml>""" % (um.from_id,
                         um.to_id,
                         time.mktime(um.create_time.timetuple()),
                         "text",
                         self.auto_reply(um)  #
                         )
        log.info(s)
        return s

    def get_auto_reply(self):
        return {'text': "欢迎",
                "image": "图片已收到，谢谢。",
                "shortvideo": "小视频已收到，谢谢。",
                "event": self.event_reply,
                }

    def auto_reply(self, message):
        replys = self.get_auto_reply()
        res = replys.get(message.type)
        if callable(res):
            res = res(message)
        return res or ""

    def text_reply(self, message):
        print(message.content)

        # return info

    def event_reply(self, message):
        event = json.loads(message.content)
        return self.on_event(event, message)
        # return info

    def on_event(self, event, context):
        pass

    def OAuthUrl(self, redirect_uri):
        return get_wx_oauth_url(self.appid, redirect_uri)

    def cgi_call(self, func, data=None, extraParams="", retrieve=False):
        self.update_token()
        try_times = 2
        for i in range(try_times):
            url = "%s%s?access_token=%s%s" % (self.cgi_url, func, self.token, extraParams)
            if retrieve:
                return urlretrieve(url)
            else:
                pd = data and json.dumps(data, ensure_ascii=False).encode("utf8")
                r = requests.post(url, pd)
                r.encoding = 'utf8'
                data = r.json()
                if data.get("errcode") in self.token_invalid_codes:
                    self.update_token(at_once=True)
                    continue
                return data
        raise ValueError("cgi_call: %s failed. %s" % (func, data))


def get_weixin_login_context(request):
    state = request.GET.get("state")
    if state and state.startswith(STATE_PREFIX):
        state = state[len(STATE_PREFIX):]
        from django.core.cache import cache
        context = cache.get(state)
        if not context:
            context = {'login_type': state}
        return context
