from Plugin.Interface import Interface
from wikiapi import WikiApi
import re
# Thanks and references
# https://github.com/sambrightman/wiki-api
# http://wikipedia.readthedocs.io/en/latest/quickstart.html

class Wikipedia(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(Wikipedia, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runSearchInput(self):
        searchFor = self.getPluginParamValue("SearchFor")
        locale = self.getPluginParamValue("Locale")
        limitResultsTo = self.getPluginParamValueAsInt("LimitResultsTo")
        includeContent = self.getPluginParamValueAsTrueOrFalse("IncludeContent")
        includeHeading = self.getPluginParamValueAsTrueOrFalse("IncludeHeading")
        includeSummary = self.getPluginParamValueAsTrueOrFalse("IncludeSummary")
        includeURL = self.getPluginParamValueAsTrueOrFalse("IncludeURL")
        wiki = WikiApi({"locale": locale})
        content = ""
        cnt = 0
        for result in wiki.find(searchFor):
            article = wiki.get_article(result)
            if includeHeading:
                content = "{0}\n{1}".format(content, article.heading)
            if includeURL:
                content = "{0}\n{1}".format(content, article.url)
            if includeSummary:
                content = "{0}\n{1}".format(content, article.summary)
            if includeContent:
                content = "{0}\n{1}".format(content, article.content)
            content = "{0}\n\n".format(content)
            cnt += 1
            if cnt >= limitResultsTo:
                break
        content = content.strip()
        self.setInputContent(content)
        return content
