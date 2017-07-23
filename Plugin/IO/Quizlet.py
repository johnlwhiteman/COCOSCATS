from Plugin.Interface import Interface


class Quizlet(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Quizlet, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)





    def runOutput(self):
        print("dork")
        return "dork"