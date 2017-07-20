import copy
import datetime
import hashlib
import importlib
import os
import sys
import traceback
from Core.Cfg import Cfg
from Core.Database import Database
from Core.Error import Error
from Core.File import File
from Core.Msg import Msg

class Cocoscats(Cfg):

    def __init__(self):
        super(Cocoscats, self).__init__()
        self.frameworkParams = {
            "dataDir": None,
            "originalPath": None,
            "inputPath": None,
            "analyzerPath": None,
            "translatorPath": None,
            "outputPath": None,
            "idHash": None,
            "sessionTimestamp": None
        }

    def __callPluginMethod(self, pluginType, workflowPluginParams, frameworkParams):
        pluginName = workflowPluginParams["Plugin"]
        pluginMethod = workflowPluginParams["Method"]
        pluginCfg = self.getPlugin(pluginType, pluginName)
        pluginParams = self.getPluginMethod(pluginType, pluginName, pluginMethod)["Params"]
        pluginModule= getattr(importlib.import_module(
            "Plugin.{0}.{1}".format(pluginType, pluginName)), pluginName)
        pluginInstance = pluginModule(pluginCfg, pluginParams, workflowPluginParams, frameworkParams)
        return self.__getPluginMethodInstance(pluginInstance, pluginMethod)()

    def getCfg(self):
        return copy.deepcopy(self.cfg)

    def __getPluginMethodInstance(self, pluginInstance, pluginMethod):
        method = None
        try:
            method = getattr(pluginInstance, pluginMethod)
        except Exception as e:
            Error.handleException(
                "Something bad happened: {0}/{1}\n{2}".format(
                    pluginInstance.__class__,
                    pluginMethod, str(e)), True)
        return method

    def getWorkflowInputPath(self):
        path = self.getWorkflowPlugin("Input")["Path"]
        if path is None or path.strip() == "":
            return None
        return path

    def getWorkflowOutputPath(self):
        path = self.getWorkflowPlugin("Output")["Path"]
        if path is None or path.strip() == "":
            return None
        return path

    def initialize(self, cfgPath):
        super(Cocoscats, self).load(cfgPath)
        self.frameworkParams["dataDir"] = "{0}/Data/{1}".format(self.installDir, self.cfg["ID"])
        os.makedirs(self.frameworkParams["dataDir"], exist_ok=True)
        self.frameworkParams["originalPath"] = "{0}/original.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["inputPath"] = "{0}/input.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["analyzerPath"] = "{0}/analyzer.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["translatorPath"] = "{0}/translator.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["outputPath"] = "{0}/output.txt".format(self.frameworkParams["dataDir"])
        self.frameworkParams["idHash"] = hashlib.sha256(self.cfg["ID"].encode('utf-8')).hexdigest()
        self.frameworkParams["sessionTimestamp"] = datetime.datetime.now().isoformat()

    def purgeContent(self):
        self.purgeContentByTypes(["originalPath", "inputPath", "analyzerPath", "translatorPath", "outputPath"])

    def purgeContentByTypes(self, contentTypes):
        for contentType in contentTypes:
            File.delete(self.frameworkParams[contentType])

    def runAnalyzer(self):
        Msg.show("Execute: Analyzer Phase")
        content = self.__callPluginMethod("Analyzer", self.getWorkflowPlugin("Analyzer"), self.frameworkParams)
        return File.getContent(self.frameworkParams["analyzerPath"])

    def runInput(self):
        Msg.show("Execute: Input Phase")
        content = self.__callPluginMethod("IO", self.getWorkflowPlugin("Input"), self.frameworkParams)
        File.setContent(self.frameworkParams["originalPath"], content)
        return content

    def runOutput(self):
        Msg.show("Execute: Output Phase")
        content = self.__callPluginMethod("IO", self.getWorkflowPlugin("Output"), self.frameworkParams)        
        return content

    def runTranslator(self):
        Msg.show("Execute: Translation Phase")
        content = self.__callPluginMethod("Translator", self.getWorkflowPlugin("Translator"), self.frameworkParams)
        return content

    def updateDatabase(self):
        print("updateDatabase")