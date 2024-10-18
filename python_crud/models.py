from exceptions import Error
from dbclass import Sqlite
import sys

db = Sqlite()


class Model(db):
    """ Базовый класс модели для отображения на БД
    """

    def __init__(self):
        """Создадим переменные из списка полей
          таблицу в БД при необходимости создадим и проверим
        """
        self.__count__ = -1
        for b in self.__columns__:
            setattr(self, b, None)
            self.__count__ += 1
        self.create_table()
        self.check_table()

    def check_table(self):
        pass

    def create_table(self):
        query = f"CREATE TABLE IF NOT EXISTS {self.__table__} (" + ", ".join(
            f"{a} {self.__columns__[a]}" for a in self.__columns__) + ");"
        self.exec(query)
        self.commit()

    def all(self, where=None, vars=()):
        where = f"WHERE {where}" if where else ""
        query = f"SELECT * FROM {self.__table__} {where} "
        jsonify = f"SELECT row_to_json(t) FROM({query})t"
        self.exec(jsonify, vars)
        return self.fetchall()

    def get(self, item_id=None):
        """Получаем из БД запись и заполняем свойства"""
        if item_id is None:
            item_id = self.id
        where = f" WHERE id={self.placeholder} "
        query = f"SELECT * FROM {self.__table__} {where} "
        ret = self.exec(query, (item_id))
        return self.next()

    def next(self):
        """Получаем из БД следующую запись и заполняем свойства"""
        ret = self.fetchone()
        if ret == None:
            return None
        num = 0
        try:
            for b in self.__columns__:
                var = ret[num] if ret[num] != '' else None
                setattr(self, b, var)
                num += 1
        except:
            raise Error.InternalServerError("Несоответсвие модели таблиц БД")
        return ret

    def json(self):
        from datetime import date, datetime
        ret = {}
        for b in self.__columns__:
            a = self.__dict__[b]
            if isinstance(a, (datetime, date)):
                a = a.isoformat()
            ret[b] = a
        return ret

    def add(self):
        """Добавляем в БД запись из свойств класса
          возвращаем добавленный ID
        """
        if 'user_id' in self.__columns__ and self.user_id is None:
            self.user_id = self.userid
        self.created_by = self.userid
        what, vars = self.skip_nulls()
        what += " RETURNING id "
        self.insert(what, vars)
        result = self.fetchall()
        return result[0][0]

    def put(self):
        """Изменяем в БД запись из заполненных свойств
        """
        self.modified_by = self.userid
        self.modified_at = 'now()'
        what = f" = {self.placeholder},".join(
            a for a in self.__columns__ if a != "id" and self.__dict__[a] not in (None, '')) + f" = {self.placeholder}"
        vars = tuple(self.__dict__[a] for a in self.__columns__ if a != "id" and self.__dict__[a] not in (None, ''))
        ret = self.update(what, vars)
        result = "ok?"
        for r in ret: result = r
        return result

    def skip_nulls(self):
        """ удаляем пустые значения из запроса """
        var = []
        value = []
        count = 0
        for v in self.__columns__:
            if v == 'id': continue
            if self.__dict__[v] is None: continue
            if self.__dict__[v] == '': continue
            var.append(v)
            value.append(self.__dict__[v])
            count += 1
        vars = ', '.join(v for v in var)
        what = f"({vars}) VALUES (" + ", ".join([self.placeholder] * count) + ")"
        return what, tuple(value)

    def san_timestamp(self, timestamp):
        ret = timestamp.replace('::timestamp', '')
        return ret

    def select(self, what='*', _from='', where='', vars=()):
        """???"""
        if _from == '': _from = self.__table__
        if where != '': where = "WHERE " + where
        query = f"SELECT {what} FROM {_from} {where} ;"
        return self.exec(query, vars)

    def show(self):
        """ shows table and variables"""
        return f"\t{self.__table__} \n\t========\n " + ",\n ".join(
            f"{a}\t =\t {self.__dict__[a]}" for a in self.__columns__)

    def insert(self, what, vars=()):
        query = f"INSERT INTO {self.__table__} {what} ;"
        ret = self.exec(query, vars)
        return ret

    def delete(self):
        """ удаление записи
        """
        query = f"DELETE FROM {self.__table__} WHERE id = {self.placeholder} ;"
        ret = self.exec(query, (self.id,))
        result = "ok"
        for r in ret: result = r
        return result

    def set_deleted(self, flag):
        """ установка признака на удаление записи
        """
        what = "deleted = " + "'TRUE'" if flag else "'FALSE'"
        return self.update(what)

    def update(self, what, vars=()):
        query = f"""UPDATE {self.__table__}
        SET {what}
        WHERE id = '{self.id}' ;"""
        ret = self.exec(query, vars)
        # ret = self.commit()
        return ret

    def count(self, query, vars=()):
        count = 0
        query = f"SELECT COUNT (*)t FROM ({query})t ;"
        ret = self.exec(query, vars)
        for items in ret:
            count = items[0]
        return count

    def unpack(self, ret):
        res = []
        for r in ret:
            res.append(r[0])
        return res

    def save(self):
        raise Error.InternalServerError(" Model.save : not implemented")

    def find(self, who, vars=()):
        self.select(where=who, vars=vars)
        return self.next()
