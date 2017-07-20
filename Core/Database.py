import os
import sqlite3
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg

class Database():
    dirPath = Framework.getDatabaseDir()
    dbPath = "{0}/Cocoscats.db".format(dirPath)
    dropPath = "{0}/Drop.sql".format(dirPath)
    schemaPath = "{0}/Schema.sql".format(dirPath)

    @staticmethod
    def create(forceDeleteIfExists=False):
        if Database.exists():
            if forceDeleteIfExists:
                Database.drop()
            else:
                return
        Database.execute(Database.getSchemaSql(), True, True)

    @staticmethod
    def drop():
        if Database.exists():
            os.unlink(Database.dbPath)

    @staticmethod
    def execute(sql, commit=True, asScript=False):
        conn = sqlite3.connect(Database.dbPath)
        cur = conn.cursor()
        if not asScript:
            cur.execute(sql)
        else:
            cur.executescript(sql)        
        results = cur.fetchall()
        if commit:
            conn.commit()
        conn.close()
        return results

    @staticmethod
    def exists():
        return os.path.isfile(Database.dbPath)

    @staticmethod
    def getDropSql():
        return File.getContent(Database.dropPath)

    @staticmethod
    def getSchemaSql():
        return File.getContent(Database.schemaPath)

    @staticmethod
    def getTableNames():
        sql = """SELECT name FROM sqlite_master WHERE TYPE = 'table'"""
        results = Database.execute(sql, False, False)
        tableNames = []
        for r in results:
            tableName = r[0]
            if tableName == "sqlite_sequence":
                continue
            tableNames.append(tableName)
            Database.getTableRowCount(tableName)
        tableNames.sort()
        return tableNames

    @staticmethod
    def getTableRowCount(tableName):
        sql = """SELECT COUNT(*) FROM {0}""".format(tableName)
        results = Database.execute(sql, False, False)
        return int(results[0][0])
 
    @staticmethod
    def showTablesInfo():
        tableNames = Database.getTableNames()
        for tableName in tableNames:
            rowCount = Database.getTableRowCount(tableName)
            print("{0}: [{1}]".format(tableName, rowCount))