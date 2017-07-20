from Plugin.Interface import Interface
import re

class XmlFile(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(XmlFile, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runOutput(self):
        inputContent = self.getInputContent()
        translatorContent = self.getTranslatorContent()
        tc = self.getTranslatorContentAsSections()
        tc["L1L2"] = inputContent
        for token in tc["VOCABULARY"].split("\n"):
            l1, l2, pos, freq = token.split(",")
            tc["L1L2"] = re.sub(r"\b{0}\b".format(l1), "[{0}]".format(l2), tc["L1L2"], re.IGNORECASE)
        content = """<?xml version="1.0" encoding="UTF-8"?>
<OUTPUT>
<L1L2>
{0}
</L1L2>
<L1>
{1}
</L1>
<L2>
{2}
</L2>
<VOCABULARY>
{3}
</VOCABULARY>
</OUTPUT>
""".format(tc["L1L2"].strip(), tc["L1"], tc["L2"], tc["VOCABULARY"])
        content = content.strip()
        self.setOutputContent(content)
        return content