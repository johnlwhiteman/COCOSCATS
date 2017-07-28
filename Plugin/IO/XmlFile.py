from Plugin.Interface import Interface
import base64

class XmlFile(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(XmlFile, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runOutput(self):
        tc = self.getTranslatorContentAsJson()
        if self.getPluginParamValueAsTrueOrFalse("EncodeWithBase64"):
            tc["l1l2"] = str(base64.b64encode(bytes(tc["l1l2"], "utf-8")))
            tc["l1"] = str(base64.b64encode(bytes(tc["l1"], "utf-8")))
            tc["l2"] = str(base64.b64encode(bytes(tc["l1"], "utf-8")))
            for i in range(0, len(tc["Wordlist"])):
                tc["Vocabulary"][i] = str(base64.b64encode(bytes(tc["Vocabulary"][i], "utf-8")))
        content = """<?xml version="1.0" encoding="UTF-8"?>
<CONTENT><L1L2>{0}</L1L2><L1>{1}</L1><L2>{2}</L2><VOCABULARY>{3}</VOCABULARY></CONTENT>
""".format(tc["L1L2"].strip(), tc["L1"], tc["L2"], tc["Vocabulary"])
        content = content.strip()
        self.setOutputContent(content)
        return content