import json

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from apps.user.models import User


class ProfAdminPermissionMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = get_object_or_404(User, pk=request.user.id)
            if not (user.type == User.PROF or user.type == User.ADMIN):
                raise PermissionDenied()

        else:
            raise PermissionDenied()

        return super(ProfAdminPermissionMixin, self).dispatch(request, *args, **kwargs)


class JSONResponseMixin(object):
    content_type = u"application/json"

    def render_json_response(self, json_content_dict, status=200):
        return HttpResponse(
            content=json.dumps(json_content_dict),
            content_type=self.content_type,
            status=status
        )


class AjaxResponseMixin(object):
    allowed_http_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def dispatch(self, request, *args, **kwargs):
        request_method = request.method.lower()

        if request.is_ajax() and request_method in self.allowed_http_methods:
            handler = getattr(self, "{0}_ajax".format(request_method),
                              self.http_method_not_allowed)
            self.request = request
            self.args = args
            self.kwargs = kwargs

            return handler(request, *args, **kwargs)

        return super(AjaxResponseMixin, self).dispatch(
            request, *args, **kwargs)

    def get_ajax(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post_ajax(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
