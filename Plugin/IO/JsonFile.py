from Plugin.Interface import Interface
import base64
import json
import re

class JsonFile(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(JsonFile, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runOutput(self):
        #inputContent = self.getInputContent()
        #translatorContent = self.getTranslatorContent()
        tc = self.getTranslatorContentAsJson()
        if self.getPluginParamValueAsTrueOrFalse("EncodeWithBase64"):
            tc["l1l2"] = str(base64.b64encode(bytes(tc["l1l2"], "utf-8")))
            tc["l1"] = str(base64.b64encode(bytes(tc["l1"], "utf-8")))
            tc["l2"] = str(base64.b64encode(bytes(tc["l1"], "utf-8")))
            for i in range(0, len(tc["Wordlist"])):
                tc["Wordlist"][i] = str(base64.b64encode(bytes(tc["Wordlist"][i], "utf-8")))
        content = {"L1L2": tc["L1L2"], "l1": tc["L1"], "l2": tc["L2"], "Vocabulary": tc["Wordlist"]}
        self.setOutputContent(json.dumps(content))
        return content