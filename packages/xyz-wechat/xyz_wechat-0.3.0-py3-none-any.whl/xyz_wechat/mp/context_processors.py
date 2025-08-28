"""
A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.

These are referenced from the setting TEMPLATE_CONTEXT_PROCESSORS and used by
RequestContext.
"""
from __future__ import unicode_literals
# from xyz_util import httputils
# from . import helper
#
#
# def wxConfig(request):
#     try:
#         api = helper.MpApi()
#         return {'wxConfig': api.get_jsapi_params(httputils.get_url(request))}
#     except:
#         return {}
