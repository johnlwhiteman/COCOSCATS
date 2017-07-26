from Plugin.Interface import Interface
import re
import sys

class TextFile(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(TextFile, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __getTextFileContent(self, path):
        content = None
        try:
            with open(path, "r", encoding="utf8") as fd:
                content = fd.read()
        except IOError as e:
            self.raiseException(e)
        return content

    def runInput(self):
        target = self.getWorkflowSource()
        content = self.__getTextFileContent(target).strip()
        self.setInputContent(content)
        return content

    def runOutput(self):
        tc = self.getTranslatorContentAsJson()
        content = """
[L1L2]
{0}

[L1]
{1}

[L2]
{2}

[VOCABULARY]
{3}
""".format(tc["l1l2"], tc["l1"], tc["l2"], "\n".join(tc["wordlist"]))
        content = content.strip()
        self.setOutputContent(content)
        return content