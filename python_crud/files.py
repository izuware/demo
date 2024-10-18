# routes, handlers, models
## Файл

from crud_rest import wsgiApp as app , baseRoute, crudRoute
from exceptions import Error
from models import Model
from utils import wsgi_input_file

### routes
@app.route('/files', methods=['GET','POST','DELETE'])
def files(environ, start_response, item_id=None):
    return Files(environ, start_response, item_id).handle(File)

### handlers
class Files(crudRoute):
    '''
    • POST /api/files - Загрузка файла.
    • GET /api/files/{id} - Получение файла по идентификатору.
    • DELETE /api/files/{id} - Удаление файла.
    '''
    def do_GET(self):
        item = self.model()
        if self.item_id is None:
           raise Error.BadRequest()
        item.id = self.item_id
        self.start_response('200 OK', [('Content-Type','application/octet-stream')])
        return [item.getchunk()]

    def do_POST(self):
        item = self.model()
        if self.item_id is not None:
           raise Error.BadRequest()
        else:
            item.id = self.item_id
        chunk = {}
        for chunk in wsgi_input_file(self.environ):
            item.save(chunk['input'])
        size = chunk['size']
        if chunk['boundary'] != 'OK':
           raise Error.InternalServerError("Файл получен не полностью, получено %d байт" % size)
        item.commit()        
        ret = chunk
        ret = f"File saved  {self.__class__.__name__}\n{str(ret)}\n".encode()
        self.start_response('200 OK', [('Content-Type', 'text/plain')])
        return [ret]

        
    def do_DELETE(self):
       return super().do_DELETE()
## models
class File(Model):
  __table__   = 'table_file'
  __columns__ = {'id':'INTEGER PRIMARY KEY',
               'file_name':'TEXT UNIQUE',
               'file_content':'BLOB'}

  def save(self, chunk):
    """save chunk to BLOB"""
    query = f"INSERT INTO {self.__table__} (file_content) VALUES ({self.placeholder})"
    self.conn.exec(query, (chunk,))

  def getchunk(self):
    query = f"SELECT (file_content) FROM {self.__table__} WHERE  id = {self.id} ;"
    self.exec(query)
    yield self.fetchone()[0]

