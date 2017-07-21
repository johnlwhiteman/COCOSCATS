from Plugin.Interface import Interface
import re
import sys

class HtmlFile(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(HtmlFile, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def runOutput(self):
        inputContent = self.getInputContent()
        translatorContent = self.getTranslatorContent()
        tc = self.getTranslatorContentAsSections()
        tc["L1L2"] = inputContent
        for token in tc["VOCABULARY"].split("\n"):
            l1, l2, pos, freq = token.split(",")
            tc["L1L2"] = re.sub(r"\b{0}\b".format(l1), '<span class="l2">{0}</span>'.format(l2), tc["L1L2"], re.IGNORECASE)
        content = """<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Welcome to Cocostats</title>
    <style>
        body {{
            color: #000000;
            font-family: "Arial", "Helvetica";
            font-size: 14px;
            letter-spacing: 1px;
        }}
        pre {{
            color: inherit;
            font-family: inherit;
            font-size: inherit;
            letter-spacing: inherit;
        }}
        .l2 {{
            color: blue;
            font-weight: bold;
            font-style: italic;
        }}
    </style>
</head>
<body>
<h1>COCOSCATS</h1>
<h2>[L1L2]</h2>
{0}

<h2>[L1]</h2>
{1}

<h2>[L2]</h2>
{2}

<h2>[VOCABULARY]</h2>
<pre>{3}</pre>

</body>
</html>
""".format(tc["L1L2"].strip(), tc["L1"], tc["L2"], tc["VOCABULARY"])
        self.setOutputContent(content)
        return content