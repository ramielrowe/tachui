import datetime
import functools
import json

from django.http import HttpResponse

from tachui import models


def session_deployments(func):

    @functools.wraps(func)
    def handled(request, *args, **kwargs):
        deployments = request.session.get('deployments', [])
        if len(deployments) == 0:
            default_deps = models.Deployment.objects.filter(is_default=True)
            for dep in default_deps:
                deployments.append(dep.name)
        kwargs['deployments'] = deployments
        return func(request, *args, **kwargs)

    return handled


def api_call(func):

    @functools.wraps(func)
    def handled(*args, **kwargs):
        return rsp(func(*args, **kwargs))

    return handled


def rsp(data):
    if data is None:
        return HttpResponse(content_type="application/json")
    if isinstance(data, basestring):
        return HttpResponse(data, content_type="text/html")
    return HttpResponse(json.dumps(data), content_type="application/json")


def timestamp_to_dt(when):
    if 'T' in when:
        try:
            # Old way of doing it
            when = datetime.datetime.strptime(when, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            try:
                # Old way of doing it, no millis
                when = datetime.datetime.strptime(when, "%Y-%m-%dT%H:%M:%S")
            except Exception, e:
                print "BAD DATE: ", e
    else:
        try:
            when = datetime.datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            try:
                when = datetime.datetime.strptime(when, "%Y-%m-%d %H:%M:%S")
            except Exception, e:
                print "BAD DATE: ", e

    return when