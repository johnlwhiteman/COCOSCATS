from Plugin.Interface import Interface
import re
import requests
from xml.etree import ElementTree

class Azure(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Azure, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __chaffAndLog(self, inputContent, translatedInputContent, analyzerContent, analyzerTokensStr, translatedAnalyzerTokensStr):
        acceptedTokens = []
        rejectedTokens = []
        analyzerTokens = analyzerTokensStr.lower().strip().split(".")
        analyzerTokensCnt = len(analyzerTokens)
        analyzerContentTokens = analyzerContent.split("\n")
        analyzerContentTokensCnt = len(analyzerContentTokens)
        translatedAnalyzerTokens = translatedAnalyzerTokensStr.lower().strip().split(".")
        translatedAnalyzerTokensCnt = len(translatedAnalyzerTokens)
        translatedInputContent = translatedInputContent.lower()
        if analyzerTokensCnt != translatedAnalyzerTokensCnt:
            self.raiseExecption("Unexpected mismatched translation counts. Don't know what belongs to what")
        for i in range(0, translatedAnalyzerTokensCnt):
            l1a = analyzerTokens[i].replace("'","")
            l2a = translatedAnalyzerTokens[i].replace("'","")
            if re.search(l2a, translatedInputContent, re.IGNORECASE):
                acceptedTokens.append(self.__getAnalyzerMatch(l1a, l2a, analyzerContentTokens))
            else:
                rejectedTokens.append(self.__getAnalyzerMatch(l1a, l2a, analyzerContentTokens))
        content = """[VOCABULARY]
{0}

[REJECTED]
{1}

[L1]
{2}

[L2]
{3}
""".format(
"\n".join(acceptedTokens), "\n".join(rejectedTokens),
inputContent, translatedInputContent)
        self.setTranslatorContent(content)
        return content

    def __checkResponse(self, response, msg):
        if response is None or response.status_code != 200:
            self.raiseException("Azure: {0}\n{1}\nStatus Code: {2}\n{3}".format(
                response.headers, response.text, response.status_code, msg))

    def __getAccessToken(self):
        response = None
        try:
            url = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": self.getPluginParamValue("AccessKey")
            }
            response = requests.post(url, headers=headers)
            self.__checkResponse(response, "Failed to get access token")
        except Exception as e:
            self.raiseException(e)
        return response.text.strip()

    def __getAccessTokenX(self):
        return None

    def __getAnalyzerMatch(self, l1, l2, analyzerContentTokens):
        match = None
        for token in analyzerContentTokens:
            l1b, pos, freq = token.strip().split(",")
            if l1 == l1b:
                match = "{0},{1},{2},{3}".format(l1, l2, pos, freq)
                break
        if match is None:
            self.raiseException("Missing analyzer token somewhere")
        return match

    def __getAnalyzerTokensStr(self, analyzerContent):
        tokens = analyzerContent.split("\n")
        content = ""
        for token in tokens:
            content = "{0}'{1}'.".format(content, token.split(",")[0])
        return content[:-1].strip().lower()

    def __getInputTranslationStr(self, inputContent, accessToken):
        return self.__getTranslation(inputContent, accessToken)

    def __getSupportedLanguages(self, accessToken):
        languages = []
        try:
            url = "https://api.microsofttranslator.com/v2/http.svc/GetLanguagesForTranslate"
            headers = {
                "Accept": "application/xml",
                "Authorization": "Bearer {0}".format(accessToken)
            }
            response = requests.get(url, headers=headers)
            self.__checkResponse(response, "Failed to get supported language list")
            root =  ElementTree.fromstring(response.text.encode('utf-8'))
            for child in root.getchildren():
                languages.append(child.text)
            languages.sort()
        except Exception as e:
            self.raiseException(e)
        return languages

    def __getTranslation(self, content, accessToken):
        url = "https://api.microsofttranslator.com/v2/http.svc/Translate?text={0}&from={1}&to={2}&contentType=text%2Fplain".format(
            content, self.getPluginParamValue("L1"), self.getPluginParamValue("L2"))
        headers = {
            "Accept": "application/xml",
            "Authorization": "Bearer {0}".format(accessToken)
        }
        response = requests.get(url, headers=headers)
        self.__checkResponse(response, "Failed to get translation")
        root =  ElementTree.fromstring(response.text.encode('utf-8'))
        translatedContent = root.text.strip()
        return translatedContent

    def __getTranslatedAnalyzerContent(self, analyzerContent, accessToken):
        return self.__getTranslation(analyzerContent, accessToken).strip()

    def __getTranslatedAnalyzerTokensStr(self, analyzerTokensStr, accessToken):
        raw = self.__getTranslation(analyzerTokensStr, accessToken).strip().lower().split(".")
        content = ""
        for r in raw:
            r = r.replace("'", "").strip()
            content = "{0}'{1}'.".format(content, r.replace("'", "").strip())
        return content[:-1]

    def __getTranslatedAnalyzerTokensStrOneByOne(self, analyzerTokensStr, accessToken):
        tokens = analyzerTokensStr.split(".")
        content = ""
        for token in tokens:
            content = "{0}'{1}'.".format(content, self.__getTranslation(token.replace("'", "").strip(), accessToken))
        content = content[:-1]
        return content

    def __getTranslatedInputContent(self, inputContent, accessToken):
        return self.__getTranslation(inputContent, accessToken)

    def __getTranslatedAnalyzerTokensStrX(self, analyzerTokensStr, accessToken):
        content = """'kami'.'itu'.'rumah'.'dan'.'adalah'.'hidup'.'hijau'.'tahun'.'memiliki'.'dapur'.'tapi'.'adalah'.'anjing'.'berlantai dua'.'membeli'.'kamar tidur'.'kamar mandi'.'hidup'.'kamar'.'windows'.'bersih'.'dua-mobil'.'garasi'.'kotor'.'tetangga'.'bagus'.'mereka'.'kulit'.'banyak'.'memiliki'"""
        return content

    def __getTranslatedAnalyzerTokensStrOneByOneX(self, inputContent, accessToken):
        return self.__getTranslatedAnalyzerTokensStrX(sinputContent, accessToken)

    def __getTranslatedInputContentX(self, inputContent, accessToken):
        content = """Aku tinggal di sebuah rumah dua lantai, hijau. Kami membeli dua puluh tahun yang lalu. Ini memiliki tiga kamar tidur, 2 Kamar mandi, dapur dan ruang tamu. Jendela bersih, tetapi dua-mobil garasi kotor. Tetangga bagus, tapi kulit anjing mereka terlalu banyak. Aku harus memotong rumput setiap minggu. Anjing-anjing ingin buang air kecil pada rumput hijau yang menjadikannya kuning. Kami direnovasi dapur bulan lalu. Ini memiliki wastafel, kulkas, oven dan kompor. Hipotek adalah affortable. Pajak properti dan asuransi yang terlalu tinggi walaupun. Anak-anak saya dibesarkan di rumah ini. Mereka meninggalkan rumah untuk perguruan beberapa tahun yang lalu. Sekarang kita hidup oleh diri kita sendiri di rumah. Kami mengunci pintu setiap malam."""
        return content

    def __removeUnexpectedCharacters(self, content):
        chars = ["#"]
        for c in chars:
            content = content.replace(c, "")
        return content

    def runTranslate(self):
        analyzerContent = self.getAnalyzerContent()
        try:
            accessToken = self.__getAccessToken()
            inputContent = self.__removeUnexpectedCharacters(self.getInputContent())
            translatedInputContent = self.__getTranslatedInputContent(inputContent, accessToken)
            analyzerContent = self.getAnalyzerContent()
            analyzerTokensStr = self.__getAnalyzerTokensStr(analyzerContent)
            if self.getPluginParamValue("SearchOneByOne").lower() == "false":
                translatedAnalyzerTokensStr = self.__getTranslatedAnalyzerTokensStr(analyzerTokensStr, accessToken)
            else:
                translatedAnalyzerTokensStr = self.__getTranslatedAnalyzerTokensStrOneByOne(analyzerTokensStr, accessToken)
            return self.__chaffAndLog(inputContent, translatedInputContent, analyzerContent, analyzerTokensStr, translatedAnalyzerTokensStr)
        except Exception as e:
            self.raiseException(e)