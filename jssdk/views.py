from django.http import HttpResponse
from django.views import View


class JsSdkAPI(View):
    def get(self,request):
        # url = request.GET.get('url','')
        from jssdk.utils import JSSDK
        from wxApi.settings import appid
        from wxApi.settings import secret
        wxapi = JSSDK(appid, secret)
        access_token = wxapi.get_access_token()
        jsapi_ticket = wxapi.get_jsapi_ticket(access_token)
        url = request.META.get('HTTP_REFERER','')
        ret = wxapi.get_sign_package(jsapi_ticket, url)
        import json
        ret = json.dumps(ret)
        return HttpResponse(ret)

