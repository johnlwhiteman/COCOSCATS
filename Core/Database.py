import bleach
import json
import os
from pony import orm
import re
import sqlite3
import sys
from Core.Directory import Directory
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg
from Core.Text import Text

# Reference: https://www.blog.pythonlibrary.org/2014/07/21/python-101-an-intro-to-pony-orm/
class Database():
    directory = Framework.getDataDir()
    name = "Cocoscats"
    path = "{0}/{1}.db".format(directory, name)
    debugFlag = False
    ORM = orm
    ODB = orm.Database()

    class Table():
        Project = NotImplemented
        Input = NotImplemented
        Analyzer = NotImplemented
        Translator = NotImplemented
        Output = NotImplemented

    @staticmethod
    def checkProjectExists(projectID):
        return Database.getProject(projectID) is not None

    @staticmethod
    def commit():
        Database.ODB.commit()

    @staticmethod
    def connect():
        try:
            Database.ODB.bind("sqlite", Database.path, create_db=True)
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
        Directory.make(Database.directory)
        try:
            Database.ODB.bind("sqlite", Database.path, create_db=True)
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
            os.unlink(Database.path)

    @staticmethod
    def execute(sql, commit=True, asScript=False):
        conn = sqlite3.connect(Database.path)
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
        return os.path.isfile(Database.path)

    @staticmethod
    def getAnalyzerContent(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Analyzer.get(ProjectID=projectID)
            if result is None:
                return result
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def getInputContent(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Input.get(ProjectID=projectID)
            if result is None:
                return result
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "Source": result.Source,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def getOutputContent(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Output.get(ProjectID=projectID)
            if result is None:
                return result
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "Target": result.Target,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def getProject(projectID):
        result = {
            "ProjectID": projectID,
            "Message": "",
            "Error": False,
            "Title": "",
            "Description": "",
            "DataTime": "",
            "Vocabulary": [],
            "VocabularyParsed": [],
            "VocabularyCnt": 0,
            "Rejected": [],
            "RejectedCnt": 0,
            "L1": "",
            "L2": "",
            "L1L2": "",
        }
        projectDetails = Database.getProjectDetails(projectID)
        if projectDetails is not None:
            result["Title"] = projectDetails["Title"]
            result["Description"] = projectDetails["Description"]
            result["DateTime"] = projectDetails["DateTime"]
        else:
            result["Error"] = True
            result["Message"] = "No project found with ID: {0}".format(projectID)
            return result
        translatorContent = Database.getTranslatorContent(projectID)
        if translatorContent is not None and "ContentParsed" in translatorContent:
            result["Vocabulary"] = translatorContent["ContentParsed"]["Vocabulary"]
            result["VocabularyParsed"] = translatorContent["ContentParsed"]["VocabularyParsed"]
            result["VocabularyCnt"] = translatorContent["ContentParsed"]["VocabularyCnt"]
            result["Rejected"] = translatorContent["ContentParsed"]["Rejected"]
            result["RejectedCnt"] = translatorContent["ContentParsed"]["RejectedCnt"]
            result["L1"] = translatorContent["ContentParsed"]["L1"]
            result["L2"] = translatorContent["ContentParsed"]["L2"]
            result["L1L2"] = translatorContent["ContentParsed"]["L1L2"]
        else:
            result["Error"] = True
            result["Message"] = "No content found for project ID: {0}".format(projectID)
        return result

    @staticmethod
    def getProjectAll(projectID):
        result = {}
        result["ProjectID"] = projectID
        result["Project"] = Database.getProjectDetails(projectID)
        if result["Project"] is None:
            return None
        result["Input"] = Database.getInputContent(projectID)
        result["Analyzer"] = Database.getAnalyzerContent(projectID)
        result["Translator"] = Database.getTranslatorContent(projectID)
        result["Output"] = Database.getOutputContent(projectID)
        return result

    @staticmethod
    def getProjectDetails(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Project.get(ID=projectID)
            if result is None:
                return result
            return {
                "ID": result.ID,
                "Title": result.Title,
                "Description": result.Description,
                "DateTime": result.DateTime,
                "Workflow": result.Workflow
            }

    @staticmethod
    def getAllProjectDetails():
        with Database.ORM.db_session:
            result = Database.Table.Project.select()
            if result is None or result.count() < 1:
                return None
            projects = []
            for r in result:
                projects.append(Database.getProjectDetails(r.ID))
            return projects

    @staticmethod
    def getTranslatorContent(projectID):
        with Database.ORM.db_session:
            result =  Database.Table.Translator.get(ProjectID=projectID)
            if result is None:
                return result
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "ContentParsed": result.ContentParsed,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def sanitize(something):
        if something is str:
            something = something.replace("'", "\\'")
        return bleach.clean(something)

    @staticmethod
    def setDebug(debugFlag):
        orm.sql_debug(debugFlag)

    @staticmethod
    def setName(name):
        Database.name = name
        Database.path = "{0}/{1}.db".format(Framework.getDataDir(), name)

class Project(Database.ODB.Entity):
    ID = orm.PrimaryKey(str)
    Title = orm.Required(str)
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
    ContentParsed = orm.Required(orm.Json)
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
