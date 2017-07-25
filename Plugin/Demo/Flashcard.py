from Plugin.Interface import Interface
import re
import sys

class Flashcard(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Flashcard, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)


    def run(self):
        print("Flashcard")

        return 1