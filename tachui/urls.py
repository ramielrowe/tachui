from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc', include('django.contrib.admindocs.urls')),
    url(r'^admin', include(admin.site.urls)),
    url(r'^$', 'tachui.views.index', name='index'),
    url(r'^events', 'tachui.views.events', name='events'),
    url(r'^settings$', 'tachui.views.settings', name='settings'),

    url(r'^api$', 'tachui.api.index', name='api_index'),
    url(r'^api/session', 'tachui.api.session', name='api_session'),
    url(r'^api/deployments$', 'tachui.api.deployments', name='api_deployments'),
    url(r'^api/stacky/reports', 'tachui.api.stacky_reports', name='api_deployments'),
    url(r'^api/stacky/watch', 'tachui.api.stacky_watch', name='api_deployments'),
    url(r'^api/stacky/search', 'tachui.api.stacky_search', name='api_deployments'),
)
