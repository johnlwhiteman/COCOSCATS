import glob
import importlib
import json
import os
from Core.Msg import Msg

class Framework():

    @staticmethod
    def getDatabaseDir():
        return "{0}/Database".format(Framework.getInstallDir())

    @staticmethod
    def getInstallDir():
        return os.path.dirname(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/')

    @staticmethod
    def getPluginMethod(pluginInstance, methodName):
        method = None
        try:
            method = getattr(pluginInstance, methodName)
        except Exception as e:
            Error.handleException(
                "Unknown class/method {0}/{1}".format(
                    pluginInstance.__class__,
                    methodName), True)
        return method

    @staticmethod
    def getPluginsDir():
        return "{0}/Plugin".format(Framework.getInstallDir())

    @staticmethod
    def getWebDir():
        return "{0}/Web".format(Framework.getInstallDir())

    @staticmethod
    def getPluginFiles(pluginDirName):
        installDir = Framework.getInstallDir()
        pluginDir = "{0}/Plugin/{1}".format(installDir, pluginDirName)
        if not os.path.isdir(pluginDir):
            raise Exception("Unknown plugin directory: {0}".format(pluginDir))
        exclude = ["__init__.py", "Interface.py"]
        plugins = []
        for fileName in os.listdir(pluginDir):
            if fileName.endswith(".py") and not fileName in exclude:
                name = os.path.splitext(fileName)[0]
                plugin = {"Class": fileName,
                          "Import": "Plugin.{0}.{1}".format(pluginDirName, name),
                          "Name": name,
                          "Path": "{0}/{1}".format(pluginDir, fileName)}
                plugins.append(plugin)
        if len(plugins) < 1:
            return None
        return plugins

    @staticmethod
    def hasPluginClass(pluginType, pluginName):
        try:
            plugin = getattr(importlib.import_module(
                "Plugin.{0}.{1}".format(pluginType, pluginName)), pluginName)
        except Exception as e:
            return False
        return True

    @staticmethod
    def hasPluginClassMethod(pluginType, pluginName, pluginMethod):
        plugin = None
        try:
            plugin = getattr(importlib.import_module(
                "Plugin.{0}.{1}".format(pluginType, pluginName)), pluginName)
        except Exception as e:
            print(e)
            return False
        return pluginMethod in dir(plugin)

    @staticmethod
    def showAllPluginFiles():
        Msg.show("Plugins")
        Framework.showPluginFiles("IO")
        Framework.showPluginFiles("Analyzer")
        Framework.showPluginFiles("Translator")

    @staticmethod
    def showPluginFiles(pluginDirName):
        print("\n[{0}]".format(pluginDirName))
        plugins = Framework.getPluginFiles(pluginDirName)
        if plugins is None:
            Msg.showWarning("Can't find an plugins")
            return
        for plugin in plugins:
            print("  {0}".format(plugin["Name"]))
