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

    def __init__(self, cfgPath):
        self.cfgPath = cfgPath
        self.cfg = None
        self.installDir = Framework.getInstallDir()
        self.pluginTypes = ["IO", "Analyzer", "Translator", "Demo"]
        self.pluginTypeAlias = \
            {"Input": "IO", "Analyzer": "Analyzer", "Translator": "Translator", "Output": "IO", "Demo": "Demo"}

    def checkIfCfgLoaded(self):
        if self.cfg is None:
            Error.raiseException("Missing cfg file. Did you load it?")

    def disableDemo(self):
        self.cfg["Workflow"]["Demo"]["Enable"] = "False"

    def enableDemo(self):
        self.cfg["Workflow"]["Demo"]["Enable"] = "True"

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

    def getProjectDescription(self):
        return self.cfg["Description"]

    def getProjectID(self):
        return self.cfg["ProjectID"]

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
        plugin["__projectID__"] = self.getProjectID()
        plugin["__projectDescription__"] = self.getProjectDescription()
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

    def load(self, verifyFlag=True):
        __cfgPath = self.cfgPath
        if not os.path.isfile(__cfgPath):
            Error.raiseException("Can't find cfg file: {0}".format(__cfgPath))
        with open(__cfgPath) as fd:
            self.cfg = json.loads(fd.read())
            for name, value in self.cfg.items():
                self.__dict__[name] = value
        if verifyFlag:
            self.verify()
        self.cfgPath = __cfgPath

    def save(self, path):
        with open(path, "w") as fd:
            json.dump(self.cfg, fd)

    def show(self):
        if self.cfg is None or self.cfgPath is None:
            Msg.showWarning("No information found for cfg file. Did you load it?")
            return
        pprint(self.cfg)
        Msg.flush()

    def verify(self):
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

class CfgEditor(object):

    def __init__(self):
        self.cfg = None
        self.cfgPath = None

    def deleteCfg(self):
        if Text.isNone(self.cfgPath):
            return
        File.delete(self.cfgPath)

    def getCfg(self):
        return copy.deepcopy(self.cfg)

    def loadCfg(self, cfgPath):
        self.cfgPath = cfgPath
        with open(cfgPath) as fd:
            self.cfg = json.load(fd)

    def saveCfg(self, cfgPath=None):
        if cfgPath is not None:
            self.cfgPath = cfgPath
        if cfgPath is None and self.cfgPath is None:
            Error.raiseException("You must specify a path to save cfg file")
        if self.cfg is None:
            Error.raiseException("No cfg loaded or set")
        with open(self.cfgPath, "w") as fd:
            json.dump(self.cfg, fd)

    def setCfg(self, cfg):
        self.cfg = cfg
        self.cfgPath = None

    def setDatabase(self, cfg):
        for name, value in cfg.items():
            self.cfg["Database"][name] = value

    def setDatabaseName(self, name):
        self.cfg["Database"]["Name"] = name

    def setProjectID(self, projectID):
        self.cfg["ProjectID"] = projectID

    def setWorkflowInputSource(self, path):
        self.cfg["Workflow"]["Input"]["Source"] = path

    def setWorkflowOutputTarget(self, path):
        self.cfg["Workflow"]["Output"]["Target"] = path

    def setWorkflowPlugin(self, pluginType, cfg):
        for name, value in cfg.items():
            self.cfg["Workflow"][pluginType][name] = value
