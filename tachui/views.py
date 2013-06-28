from django.http import HttpResponse
from django.template import loader
from django.template import RequestContext

from tachui import models
from tachui import util


def context_data(page):
    return {
        'nav': {
            'page': page
        }
    }


@util.session_deployments
def index(request, deployments=None):
    template = loader.get_template('index.html')
    context = RequestContext(request, context_data('index'))
    return HttpResponse(template.render(context))


@util.session_deployments
def events(request, deployments=None):
    template = loader.get_template('events.html')
    context = RequestContext(request, context_data('events'))
    return HttpResponse(template.render(context))


@util.session_deployments
def settings(request, deployments=None):

    if request.method == 'POST':
        deployments = request.POST.getlist('deployments')
        request.session['deployments'] = deployments
        print deployments

    template = loader.get_template('settings.html')
    data = context_data('settings')
    data.update({
        'selected_deployments': deployments,
        'all_deployments': models.Deployment.objects.all()
    })
    context = RequestContext(request, data)
    return HttpResponse(template.render(context))
