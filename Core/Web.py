import bottle
import json
import threading
import webbrowser

class Web(object):

    cocoscats = None
    inputTainted = False
    analyzerTainted = False
    translatorTainted = False
    outputTainted = False

    @bottle.route("/Api/GetCfg")
    def __getCfg():
        if self.cocoscats.cfg is None:
            return "{}"
        return self.cocoscats.cfg

    @bottle.get("/Web/css/<path:re:.*\.css>")
    def __getCssPath(path):
        return bottle.static_file(path, root="Web/css")

    @staticmethod
    def getEditor(content):
        return """
<table>
<tr>
<td><textarea id="content">{0}</textarea></td>
</tr><tr>
<td align="center"><div id="cfgMsg">&nbsp;</div></td>
</tr><tr>
<td align="right">
<button type="button" id="editorSave">Save</button>
</td>
</tr>
</table>
""".format(content)

    @staticmethod
    def getFooter():
        return """
<script src="/Web/js/jquery.js"></script>
<script src="/Web/js/cocoscats.js"></script>
</body>
</html>"""

    @staticmethod
    def getHeader(title):
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Cocoscats: {0}</title>
    <link rel="stylesheet" href="/Web/css/cocoscats.css">
</head>
<body>
<a href="/">Home</a> | <a href="/Reset">Reset</a>""".format(title)

    @bottle.get("/Web/html/<path:re:.*\.html>")
    def getHtmlPath(path):
        return bottle.static_file(path, root="Web/html")

    @bottle.get("/Web/img/<path:re:.*\.(jpg|png)>")
    def getImgPath(path):
        return bottle.static_file(path, root="Web/img")

    @bottle.get("/Web/js/<path:re:.*\.js>")
    def getJsPath(path):
        return bottle.static_file(path, root="Web/js")

    @staticmethod
    def getNavigation(title):
        if title == "Configuration":
            content = """
<h2>Step 1: Configuration</h2>
<table>
<tr>
<td><span id="navTitle">Configuration</span></td>
<td>|</td>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td>Analyzer</td>
<td>|</td>
<td>Translator</td>
<td>|</td>
<td>Output</td>
</tr>
</table>"""
        elif title == "Input":
            content = """
<h2>Step 2: Input</h2>
<table>
<tr>
<td><a href="/Configuration">Configuration</a></td>
<td>|</td>
<td><span id="navTitle">Input</span></td>
<td>|</td>
<td><a href="/Analyzer">Analyzer</a></td>
<td>|</td>
<td>Translator</td>
<td>|</td>
<td>Output</td>
</tr>
</table>"""
        elif title == "Analyzer":
            content = """
<h2>Step 3: Analyzer</h2>
<table>
<tr>
<td><a href="/Configuration">Configuration</a></td>
<td>|</td>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td><span id="navTitle">Analyzer</span></td>
<td>|</td>
<td><a href="/Translator">Translator</a></td>
<td>|</td>
<td>Output</td>
</tr>
</table>"""
        elif title == "Translator":
            content = """
<h2>Step 4: Translator</h2>
<table>
<tr>
<td><a href="/Configuration">Configuration</a></td>
<td>|</td>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td><a href="/Analyzer">Analyzer</a></td>
<td>|</td>
<td><span id="navTitle">Translator</span></td>
<td>|</td>
<td><a href="/Output">Output</a></td>
</tr>
</table>"""
        elif title == "Output":
            content = """
<h2>Step 4: Output</h2>
<table>
<tr>
<td><a href="/Configuration">Configuration</a></td>
<td>|</td>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td><a href="/Analyzer">Analyzer</a></td>
<td>|</td>
<td><a href="/Translator">Translator</a></td>
<td>|</td>
<td><span id="navTitle">Output</span></td>
</tr>
</table>"""
        return content

    @bottle.route("/Api/GetPlugins/<pluginType>")
    def __getPlugins(pluginType):
        return self.cocoscats.getPlugins(pluginType)

    def run(cocoscats):
        Web.cocoscats = cocoscats
        browser = webbrowser.get(Web.cocoscats.cfg["Browser"])
        browser.open("http://{0}:{1}/".format(Web.cocoscats.cfg["Host"],
                                              Web.cocoscats.cfg["Port"]))
        threading.Thread(target=bottle.run,
                         kwargs=dict(host=Web.cocoscats.cfg["Host"],
                         port=Web.cocoscats.cfg["Port"])).start()

    @bottle.route("/Analyzer")
    @bottle.route("/Analyzer/<action>")
    @bottle.route("/Analyzer/<action>", method="POST")
    def __runAnalyzer(action=None):
        header = Content.getHeader("Analyzer")
        footer = Content.getFooter()
        navigation = Content.getNavigation("Analyzer")
        path = Web.cocoscats.frameworkParams["analyzerPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Content.analyzerTainted = True
            Content.translatorTainted = False
            Content.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if Content.analyzerTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runAnalyzer()
        editor = Content.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Configuration")
    @bottle.route("/Configuration/<action>")
    @bottle.route("/Configuration/<action>", method="POST")
    def __runConfiguration(action=None):
        header = Content.getHeader("Configuration")
        footer = Content.getFooter()
        navigation = Content.getNavigation("Configuration")
        path = Web.cocoscats.cfgPath
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content);
            return "Successfully saved to '" + path + "'"
        content = File.getContent(path)
        editor = Content.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Input")
    @bottle.route("/Input/<action>")
    @bottle.route("/Input/<action>", method="POST")
    def __runInput(action=None):
        header = Content.getHeader("Input")
        footer = Content.getFooter()
        navigation = Content.getNavigation("Input")
        path = Web.cocoscats.frameworkParams["inputPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Content.inputTainted = True
            Content.analyzerTainted = False
            Content.translatorTainted = False
            Content.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if Content.inputTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runInput()
        editor = Content.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Output")
    @bottle.route("/Output/<action>")
    @bottle.route("/Output/<action>", method="POST")
    def __runOutput(action=None):
        header = Content.getHeader("Output")
        footer = Content.getFooter()
        navigation = Content.getNavigation("Output")
        path = Web.cocoscats.frameworkParams["outputPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Content.outputTainted = True
            Web.cocoscats.updateDatabase()
            return "Successfully saved to '" + path + "'"
        content = None
        if Content.outputTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runOutput()
        editor = Content.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @staticmethod
    @bottle.route("/Reset")
    def __runReset():
        Content.inputTainted = False
        Content.analyzerTainted = False
        Content.translatorTainted = False
        Content.outputTainted = False
        Web.cocoscats.purgeContent()
        bottle.redirect("/")

    @bottle.route("/Translator")
    @bottle.route("/Translator/<action>")
    @bottle.route("/Translator/<action>", method="POST")
    def __runTranslator(action=None):
        header = Content.getHeader("Translator")
        footer = Content.getFooter()
        navigation = Content.getNavigation("Translator")
        path = Web.cocoscats.frameworkParams["translatorPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Content.translatorTainted = True
            Content.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if Content.translatorTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runTranslator()
        editor = Content.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/")
    @bottle.route("/Home")
    @bottle.route("/<path>")
    def __showHome(path="index.html"):
        return bottle.static_file(path, root="Web/html")

    @bottle.route("/Api/Test")
    def __test():
        return """{"Say":"testing, testing, testing ..."}"""
