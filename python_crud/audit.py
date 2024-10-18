# routes, handlers, models

from crud_rest import wsgiApp as app, baseRoute, crudRoute, VERSION, DEBUG
from models import Model


### routes
@app.route('/audit', methods=['GET', 'POST'])
def audit(environ, start_response, item_id=None):
    return Audits(environ, start_response, item_id).handle(Audit)


### handlers
class Audits(crudRoute):
    '''
    • GET /api/audit - Получение аудита.
    • POST /api/audit - Добавления нового действия пользователя.
    '''


## models
class Audit(Model):
    __table__ = 'audit'
    __columns__ = {
        'id': 'uuid primary key default uuid_generate_v4()',  # Идентификатор
        'dt': 'timestamp not null default now()',
        'action_name': 'varchar not null',  # Действие пользователя
        'msg': 'varchar',  #
        'user_id': 'int references users (id) not null',  # id пользователя
    }
