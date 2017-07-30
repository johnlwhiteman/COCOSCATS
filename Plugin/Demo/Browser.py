from Plugin.Interface import Interface
from Core.File import File
import os
import platform
import sys
import subprocess

class Browser(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Browser, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __exe(self, cmd):
        print("Execute: {0}".format(cmd))
        proc = subprocess.run(cmd, universal_newlines=True, shell=True, check=False)
        print("Exit Status: {0}".format(proc.returncode))
        return proc.returncode

    def __isWindows(self):
        return platform.system().upper() == "WINDOWS"

    def run(self):
        application = self.getPluginParamValue("Application").lower()
        source = self.getPluginParamValue("Source").lower()
        content = None
        path = None
        cmd = None
        if source == "database":
            content = self.getOutputContentDB()
            path = File.setContentToTempFile(content["Content"].html)
        elif source == "path" or source == "target":
            path = self.getWorkflowTarget()
        elif source == "source":
            path = self.getWorkflowSource()
        if self.getPluginParamValue("Application").lower() == "default":
            if self.__isWindows():
                cmd = "start {0}".format(path)
            else:
                cmd = "open {0}".format(path)
        else:
            cmd = self.getPluginParamValue("Application")
        return self.__exe(cmd)