from Core.File import File
from Plugin.Interface import Interface
import json
import re
import requests

class Quizlet(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Quizlet, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __createSet(self):
        title = "Cocoscats Test"
        with open("l1.txt", "r",  encoding="utf8") as fd:
            l1 = fd.readlines()
            for i in range(0, len(l1)):
                l1[i] = l1[i].strip()
        with open("l2.txt", "r",  encoding="utf8") as fd:
            l2 = fd.readlines()
            for i in range(0, len(l2)):
                l2[i] = l2[i].strip()
        title = "Counting to 10 in English/Indonesian"
        lang_terms = "en"
        lang_definitions = "id"
        payload = {
            "title": title,
            "terms": l1,
            'definitions': l2,
            'lang_terms': "en",
            'lang_definitions': "en"
        }
        url = "https://api.quizlet.com/2.0/sets"
        response = requests.post(url, headers=headers, json=payload)
        print(response)

    def __getSets(self):
        response = self.queryMyself()
        if response is None:
            return None
        return response["sets"]

    def __queryMyself(self):
        credentials = File.getContent("./Security/QuizletCredentials.json", asJson=True)
        url = "{0}/users/{1}".format(credentials["Url"], credentials["User"])
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(credentials["AccessToken"])
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Bad status")
            return None
        return json.loads(response.text)

    def setExist(title="Counting to 10 in English/Indonesian"):
        sets = getSets()
        if sets is None:
            return None
        for s in sets:
            print(s["title"])

    def runOutput(self):
        return ""