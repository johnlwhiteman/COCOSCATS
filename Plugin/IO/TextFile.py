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
        inputContent = self.getInputContent()
        translatorContent = self.getTranslatorContent()
        tc = self.getTranslatorContentAsSections()
        tc["L1L2"] = inputContent
        for token in tc["VOCABULARY"].split("\n"):
            l1, l2, pos, freq = token.split(",")
            tc["L1L2"] = re.sub(r"\b{0}\b".format(l1), "[{0}]".format(l2), tc["L1L2"], re.IGNORECASE)
        content = """
[L1L2]
{0}

[L1]
{1}

[L2]
{2}

[VOCABULARY]
{3}
""".format(tc["L1L2"].strip(), tc["L1"], tc["L2"], tc["VOCABULARY"])
        content = content.strip()
        self.setOutputContent(content)
        return content