import os
from pony import orm
import sqlite3
import sys
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg

class Database():
    dirPath = Framework.getDatabaseDir()
    dbName = "Cocoscats"
    dbPath = "{0}/{1}.db".format(dirPath, dbName)
    dropPath = "{0}/Drop.sql".format(dirPath)
    schemaPath = "{0}/Schema.sql".format(dirPath)
    debugFlag = False
    ORM = orm
    ODB = orm.Database()

    class Table():
        Project = None
        Input = None
        Analyzer = None
        Translator = None
        Output = None

    @staticmethod
    def commit():
        Database.ODB.commit()

    @staticmethod
    def connect():
        try:
            Database.ODB.bind("sqlite", Database.dbPath, create_db=True)
        except TypeError:
            pass
        else:
            Database.ODB.generate_mapping(create_tables=True)

    @staticmethod
    def create(forceDeleteIfExists=False):
        if Database.exists():
            if forceDeleteIfExists:
                Database.drop()
            else:
                return
        os.makedirs(Database.dirPath, exist_ok=True)
        try:
            Database.ODB.bind("sqlite", Database.dbPath, create_db=True)
        except TypeError:
            pass
        else:
            Database.ODB.generate_mapping(create_tables=True)
            Database.ODB.disconnect()

    @staticmethod
    def disconnect():
        Database.ODB.disconnect()

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
    def sanitize(something):
        something = something.replace("'", "\\'")
        return something

    @staticmethod
    def setName(dbName):
        Database.dbName = dbName
        Database.dbPath = "{0}/{1}.db".format(Database.dirPath, Database.dbName)

    @staticmethod
    def setVerbose(verboseFlag):
        orm.sql_debug(verboseFlag)

    @staticmethod
    def showTablesInfo():
        tableNames = Database.getTableNames()
        for tableName in tableNames:
            rowCount = Database.getTableRowCount(tableName)
            print("{0}: [{1}]".format(tableName, rowCount))

class Project(Database.ODB.Entity):
    ID = orm.PrimaryKey(str)
    Description = orm.Required(str)
    DateTime = orm.Required(str)
    Workflow = orm.Optional(orm.Json)
    Input = orm.Set("Input", cascade_delete=True)
    Analyzer = orm.Set("Analyzer", cascade_delete=True)
    Translator = orm.Set("Translator", cascade_delete=True)
    Output = orm.Set("Output", cascade_delete=True)

class Input(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    Source = orm.Required(str)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

class Analyzer(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

class Translator(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

class Output(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    Target = orm.Required(str)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

Database.Table.Project = Project
Database.Table.Input = Input
Database.Table.Analyzer = Analyzer
Database.Table.Translator = Translator
Database.Table.Output = Output

#ORM.bind("sqlite", dbPath, create_db=True)
#ORM.generate_mapping(create_tables=True)

#with orm.db_session:
#    id = "homeskillet"

#    projectTable = Project(ID=id,
#                    Description="Read All About It",
#                    DateTime="7/20/2017",
#                    Cfg="config goes here")

#    inputTable = Input(ProjectID=projectTable,
#                       Content="Here is the content",
##                       Source="Source",
 #                      PluginName="foobar",
 #                      PluginMethod="foobarmethod",
 #                      Plugin="{}")

    #https://www.blog.pythonlibrary.org/2014/07/21/python-101-an-intro-to-pony-orm/
   # p = Project.get(ID=id)
   # if p is not None:
    #    p.delete()
    #p = Project.get(ID="dfasfasf")
    #print(len(p))
    #band.delete()





