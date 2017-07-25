from Plugin.Interface import Interface
import re
import sys

class Browser(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Browser, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)


    def run(self):
        print("Browser")
        return 1