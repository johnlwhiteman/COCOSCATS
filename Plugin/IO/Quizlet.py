from Core.Msg import Msg
from Core.File import File
from Plugin.Interface import Interface
import json
import re
import requests
import sys

#https://quizlet.com/api/2.0/docs/sets
class Quizlet(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Quizlet, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __checkResponse(self, response, msg):
        validStatusCodes = [200, 201, 204]
        if response is None or response.status_code not in validStatusCodes:
            self.raiseException("Quizlet: {0}\n{1}\nStatus Code: {2}\n{3}".format(
                response.headers, response.text, response.status_code, msg))

    def __getSetByID(self, ID):
        sets = self.__getSets()
        if sets is None:
            return None
        for s in sets:
            if s["id"] == ID:
                return s
        return None

    def __getSetsByTitle(self, title, sets=None):
        matches = []
        if sets is None:
            sets = self.__getSets()
        if sets is None:
            return None
        for s in sets:
            if s["title"].lower() == title.lower():
                matches.append(s)
        if len(matches) < 1:
            return None
        return matches

    def __getSets(self):
        response = self.__queryMe()
        if response is None:
            return None
        return response["sets"]

    def __createSet(self):
        url = "{0}/sets".format(self.getPluginParamValue("URL"))
        L1 = []
        L2 = []
        for word in self.getTranslatorContentAsJson()["VocabularyParsed"]:
            L1.append(word["L1"])
            L2.append(word["L2"])
        content = {
            "title": self.getPluginParamValue("Title"),
            "terms": L1,
            "definitions": L2,
            "lang_terms": self.getPluginParamValue("L1"),
            "lang_definitions": self.getPluginParamValue("L2")
        }
        response = requests.post(url, headers=self.__getHeaders(), json=content)
        self.__checkResponse(response, "Something went wrong while creating a set")
        id = ""
        quizletURL = ""
        sets = self.__getSetsByTitle(self.getPluginParamValue("Title"))
        if sets is not None and len(sets) == 1:
            id = sets[0]["id"]
            quizletURL = "https://quizlet.com{0}".format(sets[0]["url"])
        return {
            "id": id,
            "url": quizletURL,
            "content": content,
            "header": "",
            "response": "Flashcard generation successful. Go check them out at: https://quizlet.com/latest"
        }

    def __deleteSet(self, ID):
        url = "{0}/sets/{1}".format(self.getPluginParamValue("URL"), ID)
        response = requests.delete(url, headers=self.__getHeaders())
        self.__checkResponse(response, "Something went wrong while deleting a set")

    def __deleteSets(self, sets):
        if sets is None:
            return
        for s in sets:
           self. __deleteSet(s["id"])

    def __getHeaders(self):
        credentials = self.getCredentials()
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(credentials["AccessToken"])
        }

    def __queryMe(self):
        credentials = self.getCredentials()
        url = "{0}/users/{1}".format(self.getPluginParamValue("URL"), credentials["User"])
        response = requests.get(url, headers=self.__getHeaders())
        self.__checkResponse(response, "Can't query Quizlet account")
        return json.loads(response.text)

    def runOutput(self):
        self.__deleteSets(self.__getSetsByTitle(self.getPluginParamValue("Title")))
        content = json.dumps(self.__createSet())
        self.setOutputContent(content)
        return content

    def __setExists(self, title="Counting to 10 in English/Indonesian"):
        sets = self.__getSets()
        if sets is None:
            return None
        for s in sets:
            if s["title"] == title:
                return True
        return False
