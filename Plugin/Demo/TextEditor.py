from Plugin.Interface import Interface
from Core.File import File
import os
import platform
import sys
import tempfile

class TextEditor(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(TextEditor, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __isWindows(self):
        return platform.system().upper() == "WINDOWS"

    def run(self):
        application = self.getPluginParamValue("Application").lower()
        source = self.getPluginParamValue("Source").lower()    
        content = None
        fd = None
        path = None
        if source == "database":
            content = self.getOutputContentDB()
            fd = tempfile.NamedTemporaryFile(mode="w", delete=True)
            print(content["Content"])
        #elif source == "path" or source == "target":
            pass
        if self.getPluginParamValue("Application").lower() == "default":
            if self.__isWindows():
                pass
            else:
                print("THIS IS LINUX")

        return 1