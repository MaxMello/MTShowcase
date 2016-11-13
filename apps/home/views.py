import json

from apps.home import search as src
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from MTShowcase import names


class HomeView(TemplateView):

    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs):
        context = {'names': names}
        http_response = render(request, template_name=self.template_name, context=context)
        return http_response


class Search(TemplateView):

    def post(self, request, *args, **kwargs):
        parameters = json.loads(request.POST.get('parameters'))
        print(parameters)
        tags = parameters['tags']
        except_projects = parameters['except']
        order = parameters['order']
        maximum = parameters['maximum']
        user = None
        if not (parameters['user_id'] is None or parameters['user_id'] == 'null'):
            user = int(parameters['user_id'])
        search = src.Search(user=user, tags=tags, except_projects=except_projects, order=order, maximum=maximum)
        result = {'projects': search.projects_jsons}
        return HttpResponse(json.dumps(result), content_type="application/json")
