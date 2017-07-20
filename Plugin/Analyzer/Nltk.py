from Plugin.Interface import Interface
import nltk
from nltk.collocations import *
from nltk.tokenize import word_tokenize
import string

class Nltk(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Nltk, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runSingleWords(self):
        percentage = float(self.getPluginParamValue("Percentage")) / 100.0
        minCharLength = int(self.getPluginParamValue("MinCharLength"))
        posFilter = self.getPluginParamValue("POS")
        inputContent = self.getInputContent().lower()
        punctuation = string.punctuation.replace("-", "")
        puncFilter = dict((ord(char), None) for char in punctuation)
        tokens = nltk.word_tokenize(inputContent.translate(puncFilter))
        tokensCnt = len(tokens)
        if tokensCnt < 1:
            self.raiseException("No words found")
        maxTokensCnt = int(percentage * tokensCnt)
        tags = nltk.pos_tag(tokens)
        pos = [(token, nltk.map_tag('en-ptb', 'universal', tag)) for token, tag in tags]
        filteredTokens1 = []
        for p in pos:
            if len(p[0]) < minCharLength:
                continue
            if p[1] not in posFilter:
                continue
            filteredTokens1.append(p)
        freqTokens = nltk.FreqDist(tokens)
        content = ""
        cnt = 0
        for freqToken in freqTokens.most_common(tokensCnt):
            for token in filteredTokens1:
                if freqToken[0] == token[0]:
                    content = "{0}\n{1},{2},{3}".format(content, token[0], token[1], freqToken[1])
                    cnt += 1
                    break
            if cnt >= maxTokensCnt:
                break
        content = content.strip()
        self.setAnalyzerContent(content)
        return content