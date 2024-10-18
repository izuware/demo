# routes 

from crud_rest import wsgiApp as app, baseRoute, VERSION, DEBUG

# import handlers
import audit
import files
import users


# routes
""" 
    Обработчики маршрутов для каждого метода из списка записывается в словарь при импорте файлов с помощью декоратора @route
    Три варианта создания роута:
    - вызов специально сконструированного класса
    - вызов фунции которая генерирует необходимый вывод
    - необходимый вывод непостредственно в создаваемой ф-ии
"""


@app.route('/', methods=['GET'])
def index(environ, start_response, item_id=None):
    ''' создаем обьект нужного класса и вызываем его обработчик
    @param environ: WSGI environment.
    @type  environ: dict

    @param start_response: Function that should be run before end of handle.
    @type  start_response: callable.

    @param item_id: When the call is CRUD API
    @type  item_id: integer as str
    '''
    ret = Hello_world(environ, start_response)
    return ret.handle()


@app.route('/about', methods=['GET', 'POST'])
def about_page(environ, start_response, item_id=None):
    return about(environ, start_response)


@app.route('/version', methods=['GET'])
def version_page(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])
    return [VERSION.encode()]


#
# handlers
#
class Hello_world(baseRoute):
    ''' Реализуем нужные методы '''

    def do_GET(self):
        self.start_response('200 OK', [('Content-Type', 'text/html')])
        '''Получим список зарегисмтрированных маршрутов'''
        r = app.routes
        header = '''<!DOCTYPE html><html><head><title>API routes Table</title></head><body>
        <table border="1"><tr> <th>Method </th> <th>API route </th> <th>function</th></tr>'''
        footer = ''' <th colspan="3">Footer</th> </tr> </table>'''
        ret = header + "\t\n<tr>".join(
            f"<td>{m[0]}<td>\t{m[1]}<td>\t {r.get(m).__name__}()</tr>" for (m) in r) + footer + "\n\n"
        return [ret.encode()]


def about(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])
    return ['CRUD REST API: Демонстрационный Модуль'.encode('utf-8')]
