# database adapters
#
from exceptions import Error

import sqlite3
import sys

class Sqlite:
  con = sqlite3.connect("server.db")
  conn = con.cursor()
  placeholder = '?'

  def exec(self, query,vars=None):
    print("Sqlite.exec : ", query, vars)
    if vars is not None:
      return self.conn.execute(query,vars)
    return self.conn.execute(query)

  def commit(self):
    return self.con.commit()

class fooSql:
    placeholder = "%s"

    def exec(self, query, vars=()):
        return self.conn.execNT(query, vars)

    def fetchall(self):
        result = []
        for ret in self.conn:
            result.append(ret)
        return result

    def fetchone(self):
        try:
            ret = self.conn.fetchone()
        except ValueError:
            ret = None
        return ret

    def commit(self):
        return
