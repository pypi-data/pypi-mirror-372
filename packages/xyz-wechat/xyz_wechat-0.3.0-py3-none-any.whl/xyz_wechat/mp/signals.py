import django.dispatch
import logging
from django.conf import settings

log = logging.getLogger('django.request')

token_updated = django.dispatch.Signal()
pay_result_notice = django.dispatch.Signal()
message_notice = django.dispatch.Signal()
