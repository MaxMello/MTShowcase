import json

from apps.home import search as src
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from MTShowcase import names
from django.shortcuts import render_to_response
from django.template import RequestContext


class HomeView(TemplateView):

    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name, context={'names': names})


class Search(TemplateView):

    def post(self, request, *args, **kwargs):
        parameters = json.loads(request.POST.get('parameters'))
        #print(parameters)
        tags = parameters['tags']
        except_projects = parameters['except']
        order = parameters['order']
        maximum = parameters['maximum']
        user = None

        if not (parameters['user_id'] is None or parameters['user_id'] == 'null'):
            user = int(parameters['user_id'])

        search = src.Search(user=user, tags=tags, except_projects=except_projects, order=order, maximum=maximum)

        return HttpResponse(
            json.dumps({'projects': search.projects_jsons}),
            content_type="application/json"
        )


class About(TemplateView):

    template_name = 'home/about.html'

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name, context={'names': names})


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response