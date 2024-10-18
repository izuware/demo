# main wsgi routine
#
DEBUG: str = "ON"
VERSION: str = "0.0.0"
API_PATH: str = "/api.v1/"

import os
from exceptions import Error
from utils import file_type, parse_post, get_post_param, is_id, dumps, loads
import traceback


class baseWsgiApp:

    def __init__(self, con=None, staticdir=None, apidir=API_PATH):
        self.routes = {}
        self.staticdir = staticdir
        self.apidir = apidir
        self.conn = con

    def api_path(self, path):
        if not path.startswith(self.apidir):
            path = self.apidir[:-1] + path.rstrip('/')
        return path

    def route(self, path, methods=['GET']):
        path = self.api_path(path)

        def decorator(handler):
            for method in methods:
                self.routes[(method, path)] = handler
            return handler

        return decorator

    def static(self, environ, start_response):
        ''' обслуживание статичных файлов '''
        method = environ['REQUEST_METHOD']
        query = environ.get('QUERY_STRING')
        path = environ['PATH_INFO']
        if method != 'GET': raise Error.MethodNotAllowed('Method ' + method + ' not allowed')
        if os.path.exists(path):
            with open(path, 'rb') as file:
                content = file.read()
                start_response('200 OK', [('Content-Type', file_type(path))])
                return [content]
        raise Error.NotFound('File ' + path + ' not found')

    def environ(self, environ, start_response):
        environ_str = '\n'.join(f'{k}: {v}' for k, v in environ.items())
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [environ_str.encode('utf-8')]

    def options(self, path, start_response):
        """Метод OPTIONS:  HTTP методы допустимые для данного URL"""
        methods = []
        for m, p in self.routes:
            if path == p:
                methods.append(m)
        headers = ['Access-Control-Allow-Methods', ','.join(methods)]
        start_response('200 OK', headers)
        return []

    def __call__(self, environ, start_response_):
        try:
            method = environ['REQUEST_METHOD']
            query = environ.get('QUERY_STRING', None)
            path = environ['PATH_INFO']
            if 'environ' in path: return self.environ(environ, start_response_)
            ##  CRUD
            item_id = path.split('/')[-1]
            if is_id(item_id):
                path = path.rstrip(item_id)
            else:
                item_id = None
            path = path.rstrip('/')
            if method == "OPTIONS":
                return self.options(path, start_response_)
            handler = self.routes.get((method, path))
            self.start_response = start_response_
            ## тут проверить авторизацию и прочие условия, типа перегрузки и прочее
            ## санируем запросы, абы не было чего.

            if self.staticdir and self.staticdir.startwith(path):
                return self.static(environ, self.start_response)
            if handler is None:
                what = 'No handler '
                query = '?' + query if query else ''
                if DEBUG == "ON": what += method + ' ' + path + query
                raise Error.NotFound(what)
            if item_id:
                response = handler(environ, self.start_response, item_id)
            else:
                response = handler(environ, self.start_response)
            return response
        except Error.NotFound as e:
            self.start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [str(e).encode()]
        except Error.BadRequest as e:
            self.start_response('400 Bad Request', [('Content-Type', 'text/plain')])
            return [str(e).encode()]
        except Error.MethodNotAllowed as e:
            self.start_response('405 Method Not Allowed', [('Content-Type', 'text/plain')])
            return [str(e).encode()]
        except Error.NotAllowed as e:
            self.start_response('403 Forbidden', [('Content-Type', 'text/plain')])
            return [str(e).encode()]
        except Error.Conflict as e:
            self.start_response('409 Conflict', [('Content-Type', 'text/plain')])
            return [str(e).encode()]
        except Error.InternalServerError as e:
            self.start_response('501 Bad data', [('Content-Type', 'text/plain')])
            return [str(e).encode()]
        except RuntimeError as e:
            self.start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode()]

        except Exception as e:
            # Catch-all for other unexpected errors
            self.start_response('599 Internal Server Error', [('Content-Type', 'text/plain')])
            tb_str = traceback.format_exception(etype=TypeError, value=e, tb=e.__traceback__)
            t = "\n".join(tb_str)
            ret = str(t)
            ret = ret.encode()
            return [ret]


#####
# создадим приложение по умолчанию, без обслуживания статических файлов, локальная БД
wsgiApp = baseWsgiApp()


# ru.wikipedia.org/wiki/Список_кодов_состояния_HTTP
class baseRoute:
    def __init__(self, environ, start_response, item_id=None):
        self.environ = environ
        if environ.get('USER', '') == '':
            raise Error.NotAllowed('{"message":"Авторизуйтесь"}')
        self.method = environ['REQUEST_METHOD']
        self.query = environ.get('QUERY_STRING')
        self.path = environ['PATH_INFO']
        self.start_response_ = start_response
        item_id = self.path.split('/')[-1]
        if is_id(item_id):
            self.path = self.path.rstrip(item_id)
        else:
            item_id = None
        self.path = self.path.rstrip('/')
        self.item_id = item_id
        self.response_send = False
        from users import User
        self.user = User()
        self.user.conn = self.conn
        query = f"username = {self.user.placeholder}"
        vars = (environ.get('USER'),)
        self.user.find(query, vars)
        from audit import Audit
        self.audit = Audit()
        self.audit.conn = self.conn
        self.audit.userid = self.user.id
        self.audit.action_name = u'Обращение к REST API'
        fromip = self.environ.get('REMOTE_ADDR')
        self.audit.msg = str((fromip, self.method, self.path, self.query))
        self.audit.add()

    def start_response(self, status, headers):
        """ контроллируем отправку заголовков """
        if self.response_send: return
        for (a, b) in headers:
            if 'content-type' == a.lower():
                i = headers.index((a, b))
                if 'charset=' not in b.lower():
                    b = '; '.join([b, 'charset=utf-8'])
                    headers[i] = (a, b)
        self.start_response_(status, headers)
        self.response_send = True

    def handle(self, var=None):
        if 'GET' in self.method: return self.do_GET()
        if 'PUT' in self.method: return self.do_PUT()
        if 'POST' in self.method: return self.do_POST()
        if 'DELETE' in self.method: return self.do_DELETE()
        raise Error.NotFound('Метод не реализован')
        return self.do_Nothing()

    def do_Nothing(self):
        self.start_response('405 Method Not Allowed', [('Content-Type', 'text/plain; charset=utf-8')])
        what = 'метод не поддерживается '
        query = '?' + self.query if self.query else ''
        if DEBUG == "ON": what += self.method + ' ' + self.path + query
        return [what.encode()]

    def do_GET(self):
        return self.do_Nothing()

    def do_POST(self):
        return self.do_Nothing()

    def do_PUT(self):
        return self.do_Nothing()

    def do_DELETE(self):
        return self.do_Nothing()


class crudRoute(baseRoute):
    def handle(self, model):
        self.model = model
        self.model.conn = self.conn
        self.item = self.model()
        self.item.userid=self.user.id
        return super().handle(self)

    def do_GET(self):
        item = self.item
        if self.item_id is None:
            ret = item.all()
            item_id = ''
        else:
            item.id = self.item_id
            if item.get() is not None:
                ret = item.json()
                ret = dumps(ret)
                ret = [(ret,), ]
            else:
                ret =[]
        res = []
        for r in ret:
            res.append(loads(r[0]))
        # raise Error.Conflict(res)
        res = dumps(res, ensure_ascii=False)
        self.start_response('200 OK', [('Content-Type', 'text/json')])
        return [res]

    def do_POST(self):
        if self.item_id is not None:
            raise Error.BadRequest("Неправильный ИД")
        item = self.item
        post = parse_post(self.environ)
        try:
            get_post_param(post, item)
        except AttributeError as e:
            raise Error.BadRequest(e)
        ret = item.add()
        self.start_response('201 Created', [('Content-Type', 'text/plain')])
        return [str(ret).encode()]

    def do_PUT(self):
        if self.item_id is None:
            raise Error.BadRequest("Неправильный ИД")
        item = self.item
        item.id = self.item_id
        ret = item.get()
        post = parse_post(self.environ)
        try:
            get_post_param(post, item)
        except AttributeError as e:
            raise Error.BadRequest(e)
        ret = item.put()
        self.start_response('202 Accepted', [('Content-Type', 'text/plain')])
        return [str(ret).encode()]

    def do_DELETE(self):
        if self.item_id is None:
            raise Error.BadRequest("Неправильный ИД")
        item = self.item
        item.id = self.item_id
        ret = item.delete()
        for r in ret:
            res = r
        ret = res
        self.start_response('200 OK', [('Content-Type', 'text/plain')])
        return [str(ret).encode()]


import routes
