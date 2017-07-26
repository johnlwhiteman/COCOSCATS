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
            for i in range(0, len(tc["wordlist"])):
                tc["wordlist"][i] = str(base64.b64encode(bytes(tc["wordlist"][i], "utf-8")))
        content = {"l1l2": tc["l1l2"], "l1": tc["l1"], "l2": tc["l2"], "vocabulary": tc["wordlist"]}
        self.setOutputContent(json.dumps(content))
        return content