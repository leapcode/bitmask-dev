import json
from twisted.web.server import NOT_DONE_YET

from twisted.web.resource import Resource
from twisted.logger import Logger

log = Logger()


class Api(Resource):

    isLeaf = True

    def __init__(self, dispatcher, global_tokens):
        Resource.__init__(self)
        self.dispatcher = dispatcher
        self.global_tokens = global_tokens

    def render_POST(self, request):
        token = request.getHeader('x-bitmask-auth')
        if not token:
            request.setResponseCode(401)
            return 'unauthorized: no app token'
        elif token.strip() not in self.global_tokens:
            request.setResponseCode(401)
            return 'unauthorized: bad app token'

        command = request.uri.split('/')[2:]
        params = request.content.getvalue()
        if params:
            # TODO sanitize this

            # json.loads returns unicode strings and the rest of the code
            # expects strings. This 'str(param)' conversion can be removed
            # if we move to python3
            for param in json.loads(params):
                if isinstance(param, basestring):
                    param = param.encode('ascii', 'replace')
                command.append(str(param))

        d = self.dispatcher.dispatch(command)
        d.addCallback(self._write_response, request)
        d.addErrback(
            lambda f: log.error('Error on POST: {0!r}'.format(f)))
        return NOT_DONE_YET

    def _write_response(self, response, request):
        request.setHeader('Content-Type', 'application/json')
        request.write(response)
        request.finish()
