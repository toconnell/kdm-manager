#!/usr/bin/env python

from flup.server.fcgi import WSGIServer

def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])

    output = '<h1>FastCGI Environment</h1>\n<table>'
    for k, v in sorted(environ.items()):
         output += '<tr><th>%s</th><td>%s</td></tr>' % (k,v)
    output += '</table>'
    yield output

def start(socket_path="/tmp/server.sock"):
    WSGIServer(app, bindAddress=socket_path).run()

if __name__ == '__main__':
    start()

