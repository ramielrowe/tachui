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
    return HttpResponse(json.dumps(data), content_type="application/json")