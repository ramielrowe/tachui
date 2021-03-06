import datetime
import time

from django.forms.models import model_to_dict
from django.template import loader
from django.template import RequestContext
import requests

from tachui import models
from tachui import util


def _json(request):
    j = request.json
    if callable(j):
        return j()
    else:
        return j


@util.api_call
@util.session_deployments
def index(request, deployments=None):
    return {"selected_deployments": deployments}


def _create_deployment(request):
    pass


def list_deployments(request):
    deployments = models.Deployment.objects.all()
    resp = [model_to_dict(x) for x in deployments]
    return {"deployments": resp}


def _delete_deployment(request):
    pass


def _update_deployment(request):
    pass

@util.api_call
def session(request):
    if request.method == 'DELETE':
        request.session.flush()

@util.api_call
def deployments(request):
    if request.method == 'POST':
        return _create_deployment(request)
    if request.method == 'PUT':
        return _update_deployment(request)
    elif request.method == 'GET':
        return list_deployments(request)
    elif request.method == 'DELETE':
        return _delete_deployment(request)


def list_reports(deployments):
    dep_reports = []
    count = 0
    deps = models.Deployment.objects.filter(name__in=deployments)
    for dep in deps:
        url = "%s/stacky/reports"
        reports = _json(requests.get(url % dep.url))[1:]
        for report in reports:
            dep_report = [dep.name]
            dep_report.extend(report)
            dep_reports.append(dep_report)
        count += 1
    dep_reports.sort(reverse=True, key=lambda x: x[5])
    return dep_reports

@util.api_call
@util.session_deployments
def stacky_reports(request, deployments=None):
    return list_reports(deployments)


@util.api_call
@util.session_deployments
def stacky_watch(request, deployments=None):
    service = request.GET.get('service', 'nova')
    if request.method == 'DELETE':
        start = datetime.datetime.now() - datetime.timedelta(minutes=30)
        for name in deployments:
            request.session['%s-last' % name] = time.mktime(start.timetuple())

    if request.method == 'GET':
        events = []
        deps = models.Deployment.objects.filter(name__in=deployments)
        start = datetime.datetime.now() - datetime.timedelta(minutes=30)
        for dep in deps:
            since = request.session.get('%s-last' % dep.name, time.mktime(start.timetuple()))
            url = "%s/stacky/watch/0/"
            params = {
                'since': since,
                'service': service
            }
            resp = requests.get(url % dep.url, params=params)
            dep_events = []
            for x in _json(resp)[1]:
                event = [dep.name]
                event.extend(x)
                dep_events.append(event)
            events.extend(dep_events)
            request.session['%s-last' % dep.name] = _json(resp)[-1]
        events.sort(reverse=True,
                    key=lambda x: util.timestamp_to_dt("%s %s" % (x[3], x[4])))
        template = loader.get_template('api/stacky_watch.html')
        context_dict = {
            'service': service,
            'events': events
        }
        context = RequestContext(request, context_dict)
        return template.render(context)


def _search_uuid(deployments, service, uuid, limit):
    events = []
    deps = models.Deployment.objects.filter(name__in=deployments)
    for dep in deps:
        url = "%s/stacky/uuid/"
        params = {
            'uuid': uuid,
            'service': service,
        }
        if limit:
            params['limit'] = limit
        resp = requests.get(url % dep.url, params=params)
        dep_events = []
        for x in _json(resp)[1:]:
            event = [dep.name]
            event.extend(x)
            dep_events.append(event)
        events.extend(dep_events)
    events.sort(reverse=True,
                key=lambda x: util.timestamp_to_dt(x[3]))
    return events


def _search_requestid(deployments, service, requestid, limit):
    events = []
    deps = models.Deployment.objects.filter(name__in=deployments)
    for dep in deps:
        url = "%s/stacky/request/"
        params = {
            'request_id': requestid,
            'service': service
        }
        if limit:
            params['limit'] = limit
        resp = requests.get(url % dep.url, params=params)
        dep_events = []
        for x in _json(resp)[1:]:
            event = [dep.name]
            event.extend(x)
            dep_events.append(event)
        events.extend(dep_events)
    events.sort(reverse=True,
                key=lambda x: util.timestamp_to_dt(x[3]))
    return events


def _search_by_field(deployments, service, field, value, limit):
    events = []
    deps = models.Deployment.objects.filter(name__in=deployments)
    for dep in deps:
        url = "%s/stacky/search/"
        params = {
            'field': field,
            'value': value,
            'service': service
        }
        if limit:
            params['limit'] = limit
        resp = requests.get(url % dep.url, params=params)
        dep_events = []
        for x in _json(resp)[1:]:
            event = [dep.name]
            event.extend(x)
            dep_events.append(event)
        events.extend(dep_events)
    events.sort(reverse=True,
                key=lambda x: util.timestamp_to_dt(x[3]))
    return events


def _search(deployments, service, field, value, limit):
    if field == 'UUID':
        return _search_uuid(deployments, service, value, limit)
    elif field == 'RequestId':
        return _search_requestid(deployments, service, value, limit)
    else:
        if field == 'uuid' and (service == 'nova' or service == 'generic'):
            field = 'instance'

        if field == 'tenant' and service == 'glance':
            field = 'owner'

        return _search_by_field(deployments, service, field, value, limit)



@util.api_call
@util.session_deployments
def stacky_search(request, deployments=None):
    service = request.GET.get('service', 'nova')
    if request.method == 'GET':
        field = request.GET.get('field')
        value = request.GET.get('value')
        limit = request.GET.get('limit')
        events = _search(deployments, service, field, value, limit)
        template = loader.get_template('api/stacky_search.html')
        context_dict = {
            'service': service,
            'events': events
        }
        context = RequestContext(request, context_dict)
        return template.render(context)



@util.api_call
def stacky_show(request, deployment, id):
    service = request.GET.get('service', 'nova')
    if request.method == 'GET':
        dep = models.Deployment.objects.get(name=deployment)
        url = "%s/stacky/show/%s/" % (dep.url, id)
        params = {
            'service': service
        }
        resp = requests.get(url, params=params)
        template = loader.get_template('api/stacky_show.html')
        data = {'json': _json(resp)[-2], 'deployment': deployment, 'id': id}
        context = RequestContext(request, data)
        return template.render(context)
