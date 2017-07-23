import glob
import inspect
import json
import os
import re
import sys
from pprint import pprint
from Core.Error import Error
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg
from Core.Text import Text

class Cfg(object):

    def __init__(self):
        self.cfgPath = None
        self.cfg = None
        self.installDir = Framework.getInstallDir()
        self.pluginTypes = ["IO", "Analyzer", "Translator"]

    def checkIfCfgLoaded(self):
        if self.cfg is None:
            Error.raiseException("Missing cfg file. Did you load it?")

    def getPlugin(self, pluginType, pluginName):
        for plugin in self.cfg["Plugin"]:
            if plugin["Type"] == pluginType and plugin["Name"] == pluginName:
                return plugin
        Error.raiseException("Plugin {0}:{1} not found.".format(pluginType, pluginName))

    def getPlugins(self):
        if len(self.cfg["Plugin"]) < 1:
            return """{"Plugin:":[]}"""
        return json.loads(json.dumps({"Plugin": self.cfg["Plugin"]}))

    def getPluginsByType(self, pluginType):
        plugins = []
        if pluginType == "Input" or pluginType == "Output":
            pluginType = "IO"
        for plugin in self.cfg["Plugin"]:
            if plugin["Type"] == pluginType:
                plugins.append(plugin)
        if len(plugins) < 1:
            return """{"Plugin:":[]}"""
        return json.loads(json.dumps({"Plugin": plugins}))

    def getPluginMethod(self, pluginType, pluginName, pluginMethod):
        methods = self.getPlugin(pluginType, pluginName)["Method"]
        for method in methods:
            if pluginMethod == method["Name"]:
                return method
        Error.raiseException(
        "Can't find {0}::{1}::{2}()".format(
            pluginType, pluginName, pluginMethod))

    def getPluginMethods(self, pluginType, pluginName):
        methods = self.getPlugin(pluginType, pluginName)["Method"]
        if methods is None or len(methods) < 1:
            return """{"Methods:":[]}"""
        return json.loads(json.dumps({"Method": methods}))

    def getWorkflow(self):
        return self.cfg["Workflow"]

    def getWorkflowInputSource(self):
        source = self.getWorkflowPlugin("Input")["Source"]
        if source is None or source.strip() == "":
            return None
        return source

    def getWorkflowOutputTarget(self):
        target = self.getWorkflowPlugin("Output")["Target"]
        if target is None or target.strip() == "":
            return None
        return target

    def getWorkflowPlugin(self, pluginType):
        plugin = self.cfg["Workflow"][pluginType]
        plugin["Type"] = pluginType
        plugin["Alias"] = pluginType
        if pluginType == "Input" or pluginType == "Output":
            plugin["Alias"] = "IO"
        return plugin

    def isTrue(self, something):
        return something is not None and something.strip().lower() == "true"

    def isWorkflowEditTrue(self, pluginType):
        return self.isTrue(self.cfg["Workflow"][pluginType]["Edit"])

    def isWorkflowDebugTrue(self, pluginType):
        return self.isTrue(self.cfg["Workflow"][pluginType]["Debug"])

    def load(self, cfgPath="cfg.json"):
        if not os.path.isfile(cfgPath):
            Error.raiseException("Can't find cfg file: {0}".format(cfgPath))
        with open(cfgPath) as fd:
            self.cfg = json.loads(fd.read())
            for name, value in self.cfg.items():
                self.__dict__[name] = value
        self.verifyCfg()
        self.cfgPath = cfgPath

    def saveCfg(self, path):
        with open(path, "w") as fd:
            json.dump(self.cfg, fd)

    def showCfg(self):
        if self.cfg is None or self.cfgPath is None:
            Msg.showWarning("No information found for cfg file. Did you load it?")
            return
        pprint(self.cfg)

    def verifyCfg(self):
        for name, value in self.cfg.items():
            if name == "ProjectID":
                if len(value) > 256 or Text.isNothing(value):
                    Error.raiseException(
                    "{0} can only be 256 characters or less: {1}".format(name, value))
                if re.search(r'[^A-Za-z0-9_\-\\]', value):
                    Error.raiseException(
                    "{0} contains invalid characters: {1}".format(name, value))
            if Text.isNothing(value):
                Error.raiseException(
                "Missing '{0}' value in {1}".format(name, self.cfgPath))
        for pluginType in self.pluginTypes:
            self.__verifyCfgPlugins(
                pluginType,
                self.getPluginsByType(pluginType),
                Framework.getPluginFiles(pluginType)
        )

    def __verifyCfgPlugins(self, pluginType, plugins, pluginFiles):
        if plugins is None or len(plugins["Plugin"]) < 1:
            Error.raiseException(
                "No {0} plugins found: {1}".format(pluginType, self.cfgPath))

        if pluginFiles is None or len(pluginFiles) < 1:
            Error.raiseException(
                "No plugins found under: {0}/Plugin/?".format(
                self.installDir))

        methods = {}
        for plugin in plugins["Plugin"]:
            methods = self.getPluginMethods(plugin["Type"], plugin["Name"])
            for method in methods["Method"]:
                if not Framework.hasPluginClassMethod(
                    plugin["Type"], plugin["Name"], method["Name"]):
                        Error.raiseException(
                        "Can't find {0}::{1}::{2}()".format(
                            plugin["Type"], plugin["Name"], method["Name"]))

        pluginFileNames = []
        for plugin in pluginFiles:
            pluginFileNames.append(plugin["Name"])

        pluginNames = []
        for plugin in plugins["Plugin"]:
            if not plugin["Name"] in pluginFileNames:
                Error.raiseException(
                    "Plugin doesn't exist: {0}/Plugin/{1}/{2}.py".format(
                    self.installDir, pluginType, plugin))
            pluginNames.append(plugin["Name"])

        workflowPlugins = []
        if pluginType == "IO":
            workflowPlugins.append(self.getWorkflowPlugin("Input"))
            workflowPlugins.append(self.getWorkflowPlugin("Output"))
        else:
            workflowPlugins.append(self.getWorkflowPlugin(pluginType))

        for workflowPlugin in workflowPlugins:
            if not workflowPlugin["Plugin"] in pluginNames:
                Error.raiseException(
                "Workflow plugin {0} isn't defined in {1} plugin".format(
                workflowPlugin, pluginType))
            pluginType = workflowPlugin["Alias"]
            pluginName = workflowPlugin["Plugin"]
            pluginMethod = workflowPlugin["Method"]
            methods = self.getPluginMethods(pluginType, pluginName)
            foundFlag = False
            for method in methods["Method"]:
                if method["Name"] == pluginMethod:
                    foundFlag = True
            if not foundFlag:
                Error.raiseException(
                "Can't find {0}::{1}::{2}()".format(
                    pluginType, pluginName, pluginMethod))
