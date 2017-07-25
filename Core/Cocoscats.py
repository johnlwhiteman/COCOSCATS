import datetime
import importlib
import os
import sys
from Core.Cfg import Cfg
from Core.Database import Database
from Core.Directory import Directory
from Core.Error import Error
from Core.File import File
from Core.Msg import Msg
from Core.Text import Text

class Cocoscats(Cfg):

    def __init__(self):
        super(Cocoscats, self).__init__()
        self.frameworkParams = {
            "projectID": None,
            "dataDir": None,
            "originalPath": None,
            "inputPath": None,
            "analyzerPath": None,
            "translatorPath": None,
            "outputPath": None,
            "sourcePath": None,
            "targetPath": None,
            "dateTime": None
        }

    def __callPluginMethod(self, pluginType, workflowPluginParams, frameworkParams, pluginName=None, pluginMethod=None):
        if pluginName is None:
            pluginName = workflowPluginParams["Plugin"]
        if pluginMethod is None:
            pluginMethod = workflowPluginParams["Method"]
        pluginCfg = self.getPlugin(pluginType, pluginName)
        pluginParams = self.getPluginMethod(pluginType, pluginName, pluginMethod)["Params"]
        pluginModule= getattr(importlib.import_module(
            "Plugin.{0}.{1}".format(pluginType, pluginName)), pluginName)
        pluginInstance = pluginModule(pluginCfg, pluginParams, workflowPluginParams, frameworkParams)
        return self.__getPluginMethodInstance(pluginInstance, pluginMethod)()

    def __getPluginMethodInstance(self, pluginInstance, pluginMethod):
        method = None
        try:
            method = getattr(pluginInstance, pluginMethod)
        except Exception as e:
            Error.handleException(
                "Something bad happened: {0}/{1}\n{2}".format(
                    pluginInstance.__class__,
                    pluginMethod, str(e)), True, True)
        return method

    def initialize(self, cfgPath):
        super(Cocoscats, self).load(cfgPath)
        self.frameworkParams["projectID"] = self.getProjectID()
        self.frameworkParams["dataDir"] = "{0}/Data/{1}".format(self.installDir, self.getProjectID())
        Directory.make(self.frameworkParams["dataDir"])
        self.frameworkParams["originalPath"] = "{0}/original.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["inputPath"] = "{0}/input.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["analyzerPath"] = "{0}/analyzer.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["translatorPath"] = "{0}/translator.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["outputPath"] = "{0}/output.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["dateTime"] = datetime.datetime.now().isoformat()
        self.__initializeDatabase()

    def __initializeDatabase(self):
        Database.setPath(self.cfg["Database"]["Path"])
        if Text.isTrue(self.cfg["Database"]["Rebuild"]):
            Database.drop()
        if not Database.exists():
            Database.create(True)

    def purgeContent(self):
        self.purgeContentByTypes(["originalPath", "inputPath", "analyzerPath", "translatorPath", "outputPath"])

    def purgeContentByTypes(self, contentTypes):
        for contentType in contentTypes:
            File.delete(self.frameworkParams[contentType])

    def runAnalyzer(self):
        content = self.__callPluginMethod("Analyzer", self.getWorkflowPlugin("Analyzer"), self.frameworkParams)
        return File.getContent(self.frameworkParams["analyzerPath"])

    def runDemo(self, pluginName, pluginMethod):
        responseCode = self.__callPluginMethod("Demo", self.getWorkflowPlugin("Demo"), self.frameworkParams, pluginName, pluginMethod)
        return 1

    def runInput(self):
        content = self.__callPluginMethod("IO", self.getWorkflowPlugin("Input"), self.frameworkParams)
        File.setContent(self.frameworkParams["originalPath"], content)
        return content

    def runOutput(self):
        content = self.__callPluginMethod("IO", self.getWorkflowPlugin("Output"), self.frameworkParams)
        return content

    def runTranslator(self):
        content = self.__callPluginMethod("Translator", self.getWorkflowPlugin("Translator"), self.frameworkParams)
        return content

    def updateDatabase(self):
        if not Text.isTrue(self.cfg["Database"]["Enable"]):
            Msg.showWarning("Database is NOT enabled in {0}".format(self.cfgPath))
            return
        Database.connect()
        Database.setDebug(Text.toTrueOrFalse(self.cfg["Database"]["Debug"]))
        with Database.ORM.db_session:
            records = Database.Table.Project.get(ID=self.getProjectID())
            if records is not None:
                records.delete()
                Database.commit()

            projectTable = Database.Table.Project(
                ID=self.getProjectID(),
                Description=Database.sanitize(self.cfg["Description"]),
                DateTime=self.frameworkParams["dateTime"],
                Workflow=self.cfg["Workflow"])

            inputTable = Database.Table.Input(
                ProjectID=projectTable,
                Content=Database.sanitize(File.getContent(self.frameworkParams["inputPath"])),
                Source=Database.sanitize(self.cfg["Workflow"]["Input"]["Source"]),
                PluginName=Database.sanitize(self.cfg["Workflow"]["Input"]["Plugin"]),
                PluginMethod=Database.sanitize(self.cfg["Workflow"]["Input"]["Method"]),
                Plugin=self.cfg["Workflow"]["Input"])

            analyzerTable = Database.Table.Analyzer(
                ProjectID=projectTable,
                Content=Database.sanitize(File.getContent(self.frameworkParams["analyzerPath"])),
                PluginName=Database.sanitize(self.cfg["Workflow"]["Analyzer"]["Plugin"]),
                PluginMethod=Database.sanitize(self.cfg["Workflow"]["Analyzer"]["Method"]),
                Plugin=self.cfg["Workflow"]["Analyzer"])

            translatorTable = Database.Table.Translator(
                ProjectID=projectTable,
                Content=Database.sanitize(File.getContent(self.frameworkParams["translatorPath"])),
                PluginName=Database.sanitize(self.cfg["Workflow"]["Translator"]["Plugin"]),
                PluginMethod=Database.sanitize(self.cfg["Workflow"]["Translator"]["Method"]),
                Plugin=self.cfg["Workflow"]["Translator"])

            outputTable = Database.Table.Output(
                ProjectID=projectTable,
                Content=Database.sanitize(File.getContent(self.frameworkParams["outputPath"])),
                Target=Database.sanitize(self.cfg["Workflow"]["Output"]["Target"]),
                PluginName=Database.sanitize(self.cfg["Workflow"]["Output"]["Plugin"]),
                PluginMethod=Database.sanitize(self.cfg["Workflow"]["Output"]["Method"]),
                Plugin=self.cfg["Workflow"]["Output"])

        Database.disconnect()