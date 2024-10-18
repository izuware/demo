# routes, handlers, models
# Управление пользователями
from crud_rest import wsgiApp as app, baseRoute, crudRoute, VERSION, DEBUG
from exceptions import Error
from models import Model


### routes
@app.route('/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users(environ, start_response, item_id=None):
    return Users(environ, start_response, item_id).handle(User)


@app.route('/roles', methods=['GET', 'POST', 'PUT', 'DELETE'])
def roles(environ, start_response, item_id=None):
    return Roles(environ, start_response, item_id).handle(Role)


### handlers
# ru.wikipedia.org/wiki/Список_кодов_состояния_HTTP
class Users(crudRoute):
    '''
    • GET /api/users - Получение списка пользователей.
    • POST /api/users - Создание нового пользователя.
    • GET /api/users/{id} - Получение информации о конкретном    пользователе.
    • PUT /api/users/{id} - Обновление информации о пользователе.
    • DELETE /api/users/{id} - Удаление пользователя.
    '''


## 5.2.14. Системные таблицы
class Roles(crudRoute):
    '''
    • GET /api/roles - Получение списка ролей.
    • POST /api/roles - Создание новой роли.
    • GET /api/roles/{id} - Получение информации о конкретно роли.
    • PUT /api/roles/{id} - Обновление информации о роли.
    • DELETE /api/roles/{id} - Удаление роли.
    '''


## models
class Role(Model):
    __table__ = 'table_role'
    __columns__ = {'id': 'INTEGER PRIMARY KEY',
                   'role_name': 'TEXT UNIQUE'}


class User(Model):
    __table__ = 'table_users'
    __columns__ = {
        # 'id':'INTEGER PRIMARY KEY',
        # 'username':'TEXT UNIQUE',
        # 'password':'TEXT' }
        'id': 'serial primary key',
        'username': 'varchar    not null unique',
        'password': 'varchar    not null',
        'fio': 'varchar    not null',
        'telephone': 'varchar    not null',
        'role_id': 'varchar(3) not null references app_role (id)',
        'blocked': 'bool       not null default false',
        'created_at': 'timestamp           default now()',
        'modified_at': 'timestamp           default now()',
        'deleted': 'boolean    not null default false'
    }
