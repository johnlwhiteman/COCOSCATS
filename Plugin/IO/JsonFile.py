from Plugin.Interface import Interface
import base64
import re

class JsonFile(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(JsonFile, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runOutput(self):
        inputContent = self.getInputContent()
        translatorContent = self.getTranslatorContent()
        encodeWithBase64 = self.getPluginParamValueAsTrueOrFalse("EncodeWithBase64")
        tc = self.getTranslatorContentAsSections()
        tc["L1L2"] = inputContent
        for token in tc["VOCABULARY"].split("\n"):
            l1, l2, pos, freq = token.split(",")
            tc["L1L2"] = re.sub(r"\b{0}\b".format(l1), "[{0}]".format(l2), tc["L1L2"], re.IGNORECASE)
        content = '{L1L2: "' + tc["L1L2"].strip() + \
                  '", L1: "' + tc["L1"] + '"' + \
                  '", L2: "' + tc["L2"] + '"' + \
                  '", VOCABULARY: "' + tc["VOCABULARY"] + '"}'
        content = content.strip()
        if encodeWithBase64:
            content = str(base64.b64encode(bytes(content, "utf-8")))
        self.setOutputContent(content)
        return content