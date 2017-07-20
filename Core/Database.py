import os
from pony import orm
import sqlite3
import sys
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg

class Database():
    dirPath = Framework.getDatabaseDir()
    dbPath = "{0}/Cocoscats.db".format(dirPath)
    dropPath = "{0}/Drop.sql".format(dirPath)
    schemaPath = "{0}/Schema.sql".format(dirPath)
    @staticmethod
    def Foo():
        pass
       #orm.show(Database.Project)
        #orm.show(Database.Input)






    @staticmethod
    def create(forceDeleteIfExists=False):
        return
        if Database.exists():
            if forceDeleteIfExists:
                Database.drop()
            else:
                return
        Database.execute(Database.getSchemaSql(), True, True)

    @staticmethod
    def drop():
        return
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
    def sanitizeText(something):
        something = something.replace("'", "\\'") 
        return something

    @staticmethod
    def showTablesInfo():
        tableNames = Database.getTableNames()
        for tableName in tableNames:
            rowCount = Database.getTableRowCount(tableName)
            print("{0}: [{1}]".format(tableName, rowCount))


#orm.sql_debug(True)

ORM = orm.Database()

class Project(ORM.Entity):
    ID = orm.PrimaryKey(str)
    Description = orm.Required(str)
    DateTime = orm.Required(str)
    Cfg = orm.Optional(str)
    Input = orm.Set("Input", cascade_delete=True)

class Input(ORM.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)  
    Content = orm.Required(orm.LongStr)
    Source = orm.Required(str)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(str)

dbPath = Database.dbPath
if os.path.isfile(dbPath):
    os.unlink(dbPath)

ORM.bind("sqlite", dbPath, create_db=True)
ORM.generate_mapping(create_tables=True)

with orm.db_session:
    id = "homeskillet"

    projectTable = Project(ID=id,
                    Description="Read All About It",
                    DateTime="7/20/2017",
                    Cfg="config goes here")

    inputTable = Input(ProjectID=projectTable,
                       Content="Here is the content",
                       Source="Source",
                       PluginName="foobar",
                       PluginMethod="foobarmethod",
                       Plugin="{}")

    #https://www.blog.pythonlibrary.org/2014/07/21/python-101-an-intro-to-pony-orm/
    p = Project.get(ID=id)
   # if p is not None:
    #    p.delete()
    #p = Project.get(ID="dfasfasf")
    #print(len(p))
    #band.delete()


