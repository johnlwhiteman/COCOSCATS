from Core.Database import Database
from Core.Error import Error
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg
from Core.Result import Result
from Core.Text import Text
import inspect
import re
import sys

class Interface(object):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        self.__cfg = cfg
        self.__pluginParams = pluginParams
        self.__workflowPluginParams = workflowPluginParams
        self.__frameworkParams = frameworkParams

    def getAnalyzerContent(self):
        return self.__getContent("analyzerPath")

    def getAnalyzerContentDB(self):
        return Database.getAnalyzerContent(self.getProjectID())

    def getCfgValue(self, name):
        return self.__cfg[name]

    def __getContent(self, inputType):
        return File.getContent(self.__frameworkParams[inputType])

    def getCredentials(self):
        stack = inspect.stack()
        className = str(stack[1][0].f_locals["self"].__class__.__name__)
        path = "{0}/{1}.json".format(Framework.getSecurityDir(), className)
        if not File.exists(path):
            self.raiseException("Missing {0} credentials file".format(className))
        return File.getContent(path, asJson=True)

    def getFrameworkParamValue(self, name):
        return self.__frameworkParams[name]

    def getInputContent(self):
        return self.__getContent("inputPath")

    def getInputContentDB(self):
        return Database.getInputContent(self.getProjectID())

    def getOutputContent(self):
        return self.__getContent("outputPath")

    def getOutputContentDB(self):
        return Database.getOutputContent(self.getProjectID())

    def getPluginParamValue(self, name):
        return self.__pluginParams[name]

    def getPluginParamValueAsInt(self, name):
        return int(self.getPluginParamValue(name))

    def getPluginParamValueAsTrueOrFalse(self, name):
        return Text.toTrueOrFalse(self.getPluginParamValue(name))

    def getProjectDescription(self):
        return self.__workflowPluginParams["__projectDescription__"]

    def getProjectID(self):
        return self.__workflowPluginParams["__projectID__"]

    def getTranslatorContent(self):
        return self.__getContent("translatorPath")

    def getTranslatorContentAsJson(self):
        return Result.getTranslatorContentAsJson(self.getTranslatorContent())

    def getTranslatorContentFromDatabase(self):
        return Database.getTranslatorContent(self.getProjectID())

    def getWorkflowSource(self):
        return self.__workflowPluginParams["__workflowSourcePath__"]

    def getWorkflowTarget(self):
        return self.__workflowPluginParams["__workflowTargetPath__"]

    def handleException(msg, showStackTraceFlag=True, abortFlag=True):
        Error.handleException(msg, showStackTraceFlag, abortFlag)

    def raiseException(self, msg):
        Error.raiseException(msg)

    def setAnalyzerContent(self, content):
        return self.__setContent("analyzerPath", content)

    def __setContent(self, outputType, content):
        return File.setContent(self.__frameworkParams[outputType], content)

    def setInputContent(self, content):
        return self.__setContent("inputPath", content)

    def setOutputContent(self, content):
        content = self.__setContent("outputPath", content)
        File.copy(self.__frameworkParams["outputPath"], self.getWorkflowTarget())
        return content

    def setTranslatorContent(self, content):
        return self.__setContent("translatorPath", content)

    def show(self):
        Msg.showRaw("Configuration")
        Msg.showPretty(self.__cfg)
        Msg.showRaw("Plugin Parameters")
        Msg.showPretty(self.__pluginParams)
        Msg.showRaw("Framework Parameters")
        Msg.showPretty(self.__frameworkParams)