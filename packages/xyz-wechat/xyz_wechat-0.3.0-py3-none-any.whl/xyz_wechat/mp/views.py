# -*- coding:utf-8 -*-
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, RedirectView, TemplateView, View
from django.conf import settings
from ..helper import get_wx_oauth_url
from six import text_type
__author__ = 'denishuang'

from . import helper, forms


@csrf_exempt
def ports(request):
    echostr = request.GET.get("echostr")
    api = helper.MpApi()
    flag = api.check_tencent_signature(request)
    if flag:
        um = api.deal_post(request.body)
        if um:
            response = HttpResponse(api.response_user(um), "text/xml; charset=utf-8")
            response._charset = "utf-8"
            return response
    return HttpResponse(echostr)


@csrf_exempt
def notice(request):
    api = helper.MpApi()
    return HttpResponse(api.pay_result_notify(request.body))


def jsapi_config(request):
    api = helper.MpApi()
    if settings.DEBUG:
        d = {}
    else:
        d = api.get_jsapi_params(request.META.get('HTTP_REFERER'))
    return JsonResponse(d)


class LoginView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get("next")


class QRLoginView(TemplateView):
    template_name = "wechat/mp/qrlogin.html"

    def post(self, request, task_id):
        from celery.result import AsyncResult
        rs = AsyncResult(task_id)
        user = self.request.user
        d = {'username': user.username}
        from xyz_auth.authentications import add_token_for_user
        add_token_for_user(d, user)
        rs.backend.store_result(rs.id, d, 'SUCCESS')
        return HttpResponse("登录成功:%s" % rs)


class LoginQRCodeView(View):
    def get(self, request):
        from django.shortcuts import reverse
        import uuid
        api = helper.MpApi()
        task_id = text_type(uuid.uuid1())
        url = reverse("wechat:mp:qr-login", kwargs=dict(task_id=task_id))
        url = request.build_absolute_uri(url)
        url = get_wx_oauth_url(api.appid, url, state='.qrcode')
        return JsonResponse({'url': url, 'task': {'id': task_id, 'status': 'RUNNING'}})
