"""
Start all server components.
"""
from twisted.web import static, server
from twisted.application import internet, service

from web.commander.twisted_wsgi import get_root_resource


INTERFACE = "localhost"
WEB_PORT = 8000

# Twisted Application setup:
application = service.Application('server-commander')
serviceCollection = service.IServiceCollection(application)

# Django and static file server:
root_resource = get_root_resource()
# root_resource.putChild("static", static.File("static"))
http_factory = server.Site(root_resource, logPath="web.log")
internet.TCPServer(
    WEB_PORT,
    http_factory,
    interface=INTERFACE
).setServiceParent(serviceCollection)
