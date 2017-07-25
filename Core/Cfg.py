import copy
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
        self.pluginTypes = ["IO", "Analyzer", "Translator", "Demo"]
        self.pluginTypeAlias = \
            {"Input": "IO", "Analyzer": "Analyzer", "Translator": "Translator", "Output": "IO", "Demo": "Demo"}

    def checkIfCfgLoaded(self):
        if self.cfg is None:
            Error.raiseException("Missing cfg file. Did you load it?")

    def getCfg(self):
        return copy.deepcopy(self.cfg)

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

    def getWorkflowDemoPluginChoices(self):
        choices = []
        for i in range(0, len(self.cfg["Workflow"]["Demo"]["Plugin"])):
            self.cfg["Workflow"]["Demo"]["Plugin"][i]
            self.cfg["Workflow"]["Demo"]["Method"][i]
            choices.append(
                {"Name": self.cfg["Workflow"]["Demo"]["Plugin"][i],
                 "Method": self.cfg["Workflow"]["Demo"]["Method"][i]})
        if len(choices) < 1:
            return None
        return choices

    def getWorkflowDemoPluginCount(self):
        return len(self.cfg["Workflow"]["Demo"]["Plugin"])

    def getWorkflowInputSource(self):
        source = self.getWorkflowPlugin("Input")["Source"]
        if Text.isNothing(source):
            return None
        return source

    def getWorkflowOutputTarget(self):
        target = self.getWorkflowPlugin("Output")["Target"]
        if Text.isNothing(target):
            return None
        return target

    def getWorkflowPlugin(self, pluginType):
        plugin = self.cfg["Workflow"][pluginType]
        plugin["Type"] = pluginType
        plugin["Alias"] = pluginType
        if pluginType == "Input" or pluginType == "Output":
            plugin["Alias"] = "IO"
        plugin["__workflowSourcePath__"] = self.getWorkflowSourcePath()
        plugin["__workflowTargetPath__"] = self.getWorkflowTargetPath()
        return plugin

    def getWorkflowSourcePath(self):
        if Text.isNothing(self.cfg["Workflow"]["Input"]["Source"]):
            return None
        return self.cfg["Workflow"]["Input"]["Source"]

    def getWorkflowTargetPath(self):
        if Text.isNothing(self.cfg["Workflow"]["Output"]["Target"]):
            return None
        return self.cfg["Workflow"]["Output"]["Target"]

    def isWorkflowDemoEnabled(self):
        return Text.isTrue(self.cfg["Workflow"]["Demo"]["Enable"])

    def isWorkflowEditTrue(self, pluginType):
        if pluginType == "Demo":
            return False
        return Text.isTrue(self.cfg["Workflow"][pluginType]["Edit"])

    def isWorkflowDebugTrue(self, pluginType):
        if pluginType == "Demo":
            return False
        return Text.isTrue(self.cfg["Workflow"][pluginType]["Debug"])

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
        pluginLookupMap = []
        for plugin in self.cfg["Plugin"]:
            pluginMethods = self.getPluginMethods(plugin["Type"], plugin["Name"])
            for pluginMethod in pluginMethods["Method"]:
                if not Framework.hasPluginClassMethod(
                    plugin["Type"], plugin["Name"], pluginMethod["Name"]):
                        Error.raiseException(
                        "Can't find {0}::{1}::{2}()".format(
                            plugin["Type"], plugin["Name"], pluginMethod["Name"]))
                pluginLookupMap.append(
                    "{0}{1}{2}".format(plugin["Type"], plugin["Name"], pluginMethod["Name"]))
        if len(self.cfg["Workflow"]["Demo"]["Plugin"]) != len(self.cfg["Workflow"]["Demo"]["Method"]):
            Error.raiseException("Mismatched number of demo plugins and methods")
        workflowPluginLookupMap = []
        for workflowPluginType, workflowPluginCfg in self.cfg["Workflow"].items():
            pluginType = self.pluginTypeAlias[workflowPluginType]
            if pluginType != "Demo":
                workflowPluginLookupMap.append(
                    "{0}{1}{2}".format(pluginType, workflowPluginCfg["Plugin"],
                                       workflowPluginCfg["Method"]))
            else:
                for i in range(0, len(workflowPluginCfg["Plugin"])):
                    key = "{0}{1}{2}".format(pluginType, workflowPluginCfg["Plugin"][i],
                                             workflowPluginCfg["Method"][i])
                    if key not in pluginLookupMap:
                        Error.raiseException(
                        "Can't find workflow plugin {0}::{1}::{2}()".format(
                            workflowPluginType, workflowPluginCfg["Plugin"][i],
                            workflowPluginCfg["Method"][i]))