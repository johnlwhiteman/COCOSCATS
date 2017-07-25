from Plugin.Interface import Interface
import platform
import sys

class TextEditor(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(TextEditor, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __isWindows(self):
        return platform.system().upper() == "WINDOWS"

    def run(self):

        print(self.getWorkflowSource())
        print(self.getWorkflowTarget())


        #if self.__isWindows():
         #   pass

       # else:
        #    pass

        return 1