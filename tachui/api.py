import requests

from django.forms.models import model_to_dict

from tachui import models
from tachui import util


@util.api_call
@util.session_deployments
def index(request, deployments=None):
    return {"selected_deployments": deployments}


def _create_deployment(request):
    pass


def _list_deployments(request):
    deployments = models.Deployment.objects.all()
    resp = [model_to_dict(x) for x in deployments]
    return {"deployments": resp}


def _delete_deployment(request):
    pass


def _update_deployment(request):
    pass

@util.api_call
def session(request):
    print request.META['HTTP_ACCEPT']
    if request.method == 'DELETE':
        request.session.flush()

@util.api_call
def deployments(request):
    print request.META['HTTP_ACCEPT']
    if request.method == 'POST':
        return _create_deployment(request)
    if request.method == 'PUT':
        return _update_deployment(request)
    elif request.method == 'GET':
        return _list_deployments(request)
    elif request.method == 'DELETE':
        return _delete_deployment(request)

@util.api_call
@util.session_deployments
def stacky_reports(request, deployments=None):
    reports = []
    count = 0
    for name in deployments:
        dep = models.Deployment.objects.get(name=name)
        url = "%s/stacky/reports"
        if count == 0:
            reports.extend(requests.get(url % dep.url).json)
        else:
            reports.extend(requests.get(url % dep.url).json[1:])
        count += 1
    return reports