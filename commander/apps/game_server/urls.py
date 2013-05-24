from django.conf.urls import patterns, include, url
# from views import AdminIndexView

# urlpatterns = patterns('game_server.views',
#     url(r'^$', AdminIndexView.as_view(), name="server_admin"),
# )

urlpatterns = patterns('game_server.views',
    (r'^$', 'server_admin_index', {}, 'server_admin'),
)
