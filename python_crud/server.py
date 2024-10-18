# test app: web server, integration tests runner
#

from crud_rest import wsgiApp as app
from utils import file_type
import os


@app.route('/favicon.ico', ['GET', 'POST'])
def favicon(environ, start_response):
    file_path = 'favicon.ico'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            content = file.read()
            start_response('200 OK', [('Content-Type', file_type(file_path))])
            return [content]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'File not found']


@app.route('/environ', ['GET', 'POST'])
def print_environ(environ, start_response, item_id=None):
    # Convert the environ dictionary into a string
    environ_str = '\n'.join(f'{k}: {v}' for k, v in environ.items())
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [environ_str.encode('utf-8')]


def integration_test():
    import time
    import requests
    import threading

    print(' Создание потока для web сервера ')
    thread = threading.Thread(target=run_server)
    thread.start()
    # Даем серверу время на запуск
    time.sleep(2)

    # Тут будут тесты
    print('Выполнение обращения к веб-серверу')
    response = requests.get("http://localhost:8000")
    # Вывод содержимого ответа
    print(response.text)

    print('Завершение работы веб-сервера')
    global FOREVER
    FOREVER = 'NO'
    time.sleep(1)
    response = requests.get("http://localhost:8000")  # для завершения
    thread.join()


FOREVER = 'YES'


def run_server():
    # from wsgiref.validate import validator
    # validator_app = validator(app)
    from wsgiref.simple_server import make_server
    # app = baseWsgiApp()
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")
    # httpd.serve_forever()
    global FOREVER
    while FOREVER == 'YES':
        httpd.handle_request()
    httpd.server_close()


if __name__ == '__main__':
    run_server()
    # integration_test()
