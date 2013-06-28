import datetime
import time

from django.forms.models import model_to_dict
from django.template import loader
from django.template import RequestContext
import requests

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
    deps = models.Deployment.objects.filter(name__in=deployments)
    for dep in deps:
        url = "%s/stacky/reports"
        if count == 0:
            reports.extend(requests.get(url % dep.url).json)
        else:
            reports.extend(requests.get(url % dep.url).json[1:])
        count += 1
    return reports


@util.api_call
@util.session_deployments
def stacky_watch(request, deployments):
    if request.method == 'DELETE':
        start = datetime.datetime.now() - datetime.timedelta(minutes=5)
        for name in deployments:
            request.session['%s-last' % name] = time.mktime(start.timetuple())

    if request.method == 'GET':
        events = []
        deps = models.Deployment.objects.filter(name__in=deployments)
        start = datetime.datetime.now() - datetime.timedelta(minutes=5)
        for dep in deps:
            since = request.session.get('%s-last' % dep.name, time.mktime(start.timetuple()))
            url = "%s/stacky/watch/0/?since=%s"
            resp = requests.get(url % (dep.url, since))
            dep_events = []
            for x in resp.json[1]:
                event = [dep.name]
                event.extend(x)
                dep_events.append(event)
            events.extend(dep_events)
            request.session['%s-last' % dep.name] = resp.json[-1]
        events.sort(reverse=True,
                    key=lambda x: util.timestamp_to_dt("%s %s" % (x[3], x[4])))
        template = loader.get_template('api/stacky_watch.html')
        context = RequestContext(request, {'events': events})
        return template.render(context)


def _search_uuid(deployments, uuid):
    events = []
    deps = models.Deployment.objects.filter(name__in=deployments)
    for dep in deps:
        url = "%s/stacky/uuid/?uuid=%s"
        resp = requests.get(url % (dep.url, uuid))
        dep_events = []
        for x in resp.json[1:]:
            event = [dep.name]
            event.extend(x)
            dep_events.append(event)
        events.extend(dep_events)
    events.sort(reverse=True,
                key=lambda x: util.timestamp_to_dt("%s %s" % (x[3], x[4])))
    return events


def _search_requestid(deployments, requestid):
    events = []
    deps = models.Deployment.objects.filter(name__in=deployments)
    for dep in deps:
        url = "%s/stacky/request/?request_id=%s"
        resp = requests.get(url % (dep.url, requestid))
        dep_events = []
        for x in resp.json[1:]:
            event = [dep.name]
            event.extend(x)
            dep_events.append(event)
        events.extend(dep_events)
    events.sort(reverse=True,
                key=lambda x: util.timestamp_to_dt("%s %s" % (x[3], x[4])))
    return events


def _search(deployments, field, value):
    if field == 'UUID':
        return _search_uuid(deployments, value)
    elif field == 'RequestId':
        return _search_requestid(deployments, value)



@util.api_call
@util.session_deployments
def stacky_search(request, deployments):
    if request.method == 'GET':
        field = request.GET.get('field')
        value = request.GET.get('value')
        events = _search(deployments, field, value)
        template = loader.get_template('api/stacky_search.html')
        context = RequestContext(request, {'events': events})
        return template.render(context)