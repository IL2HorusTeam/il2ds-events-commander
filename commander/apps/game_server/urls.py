from django.conf.urls import patterns, include, url

urlpatterns = patterns('game_server.views',
    (r'^$', 'server_admin_index', {}, 'server_admin'),
    (r'^status/$', 'server_status', {}, 'server_status'),
)
