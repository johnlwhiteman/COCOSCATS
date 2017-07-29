from Plugin.Interface import Interface
from Core.File import File

class TextFile(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(TextFile, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runInput(self):
        content = File.getContent(self.getWorkflowSource())
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
""".format(tc["L1L2"], tc["L1"], tc["L2"], "\n".join(tc["Vocabulary"])).strip()
        self.setOutputContent(content)
        return content