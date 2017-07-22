import bottle
#from bottle_sslify import SSLify
import json
import re
import ssl
import threading
import webbrowser
from wsgiref.simple_server import make_server, WSGIRequestHandler
from Core.File import File
from Core.Security import Security
from Core.Text import Text

# Reference: http://www.socouldanyone.com/2014/01/bottle-with-ssl.html
# Use: C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s
class WebTLS(bottle.ServerAdapter):

    def __init__(self, *args, **kwargs):
        super(WebTLS, self).__init__(*args, **kwargs)
        self._server = None
        self.privateKeyPath = None
        self.certificatePath = None

    def run(self, handler):
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
            srv.socket,
            keyfile = self.privateKeyPath,
            certfile = self.certificatePath,
            server_side = True)
        srv.serve_forever()

class Web(object):

    cocoscats = None
    inputTainted = False
    analyzerTainted = False
    translatorTainted = False
    outputTainted = False

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
        content = ""
        if title == "Configuration":
            content = """
<h2>Step 1: Configuration</h2>
<table>
<tr>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td>Analyzer</td>
<td>|</td>
<td>Translator</td>
<td>|</td>
<td>Output</td>
<td>|</td>
<td>View</td>
</tr>
</table>"""
        elif title == "Input":
            content = """
<h2>Step 2: Input</h2>
<table>
<tr>
<td><span id="navTitle">Input</span></td>
<td>|</td>
<td><a href="/Analyzer">Analyzer</a></td>
<td>|</td>
<td>Translator</td>
<td>|</td>
<td>Output</td>
<td>|</td>
<td>View</td>
</tr>
</table>"""
        elif title == "Analyzer":
            content = """
<h2>Step 3: Analyzer</h2>
<table>
<tr>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td><span id="navTitle">Analyzer</span></td>
<td>|</td>
<td><a href="/Translator">Translator</a></td>
<td>|</td>
<td>Output</td>
<td>|</td>
<td>View</td>
</tr>
</table>"""
        elif title == "Translator":
            content = """
<h2>Step 4: Translator</h2>
<table>
<tr>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td><a href="/Analyzer">Analyzer</a></td>
<td>|</td>
<td><span id="navTitle">Translator</span></td>
<td>|</td>
<td><a href="/Output">Output</a></td>
<td>|</td>
<td>View</td>
</tr>
</table>"""
        elif title == "Output":
            content = """
<h2>Step 4: Output</h2>
<table>
<tr>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td><a href="/Analyzer">Analyzer</a></td>
<td>|</td>
<td><a href="/Translator">Translator</a></td>
<td>|</td>
<td><span id="navTitle">Output</span></td>
<td>|</td>
<td><a href="/View">View</a></td>
</tr>
</table>"""
        elif title == "View":
            content = """
<h2>Step 5: View</h2>
<table>
<tr>
<td><a href="/Input">Input</a></td>
<td>|</td>
<td><a href="/Analyzer">Analyzer</a></td>
<td>|</td>
<td><a href="/Translator">Translator</a></td>
<td>|</td>
<td><a href="/Output">Output</a></td>
<td>|</td>
<td><span id="navTitle">View</span></td>
</tr>
</table>"""
        return content

    @bottle.route("/Api/GetPlugins/<pluginType>")
    def __getPlugins(pluginType):
        return Web.cocoscats.getPlugins(pluginType)

    @staticmethod
    def setupCertificates():
        certificatePath = Web.cocoscats.cfg["Web"]["Security"]["Certificate"]
        publicKeyPath = Web.cocoscats.cfg["Web"]["Security"]["PublicKey"]
        privateKeyPath = Web.cocoscats.cfg["Web"]["Security"]["PrivateKey"]
        if Text.isTrue(Web.cocoscats.cfg["Web"]["Security"]["AlwaysGenerate"]):
            File.setContent("goood.txt", "HERER")
            File.deletes([certificatePath, publicKeyPath, privateKeyPath])
        if not File.exist([certificatePath, publicKeyPath, privateKeyPath]):
            Security.generateKeysAndCertificate(privateKeyPath, publicKeyPath, certificatePath)

    def run(cocoscats):
        Web.cocoscats = cocoscats
        Web.useHttps = Text.isTrue(Web.cocoscats.cfg["Web"]["Security"]["UseHttps"])
        schema = None
        if Web.useHttps:
            Web.setupCertificates()
            server = WebTLS(host=Web.cocoscats.cfg["Web"]["Host"],
                            port=Web.cocoscats.cfg["Web"]["Port"])
            server.privateKeyPath = Web.cocoscats.cfg["Web"]["Security"]["PrivateKey"]
            server.certificatePath = Web.cocoscats.cfg["Web"]["Security"]["Certificate"]
            #bottle.run(server=server)
            threading.Thread(target=bottle.run,
                kwargs=dict(
                debug = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Debug"]),
                reloader = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Reloader"]),
                server = server
                )).start()
            schema = "https"
        else:
            threading.Thread(target=bottle.run,
                kwargs=dict(
                debug = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Debug"]),
                host = Web.cocoscats.cfg["Web"]["Host"],
                port = Web.cocoscats.cfg["Web"]["Port"],
                reloader = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Reloader"])
                )).start()
            schema = "http"
        url = "{0}://{1}:{2}/".format(schema,
                                      Web.cocoscats.cfg["Web"]["Host"],
                                      Web.cocoscats.cfg["Web"]["Port"])
        for client in cocoscats.cfg["Web"]["Browser"]:
            if Text.isNothing(client) or client == "default":
                if webbrowser.open(url):
                    break
            else:
                if webbrowser.get(client).open(url):
                    break

    @bottle.route("/Analyzer")
    @bottle.route("/Analyzer/<action>")
    @bottle.route("/Analyzer/<action>", method="POST")
    def __runAnalyzer(action=None):
        header = Web.getHeader("Analyzer")
        footer = Web.getFooter()
        navigation = Web.getNavigation("Analyzer")
        path = Web.cocoscats.frameworkParams["analyzerPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Web.analyzerTainted = True
            Web.translatorTainted = False
            Web.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if Web.analyzerTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runAnalyzer()
        editor = Web.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Input")
    @bottle.route("/Input/<action>")
    @bottle.route("/Input/<action>", method="POST")
    def __runInput(action=None):
        header = Web.getHeader("Input")
        footer = Web.getFooter()
        navigation = Web.getNavigation("Input")
        path = Web.cocoscats.frameworkParams["inputPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Web.inputTainted = True
            Web.analyzerTainted = False
            Web.translatorTainted = False
            Web.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if Web.inputTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runInput()
        editor = Web.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Output")
    @bottle.route("/Output/<action>")
    @bottle.route("/Output/<action>", method="POST")
    def __runOutput(action=None):
        header = Web.getHeader("Output")
        footer = Web.getFooter()
        navigation = Web.getNavigation("Output")
        path = Web.cocoscats.frameworkParams["outputPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Web.outputTainted = True
            Web.cocoscats.runDatabase()
            return "Successfully saved to '" + path + "'"
        content = None
        if Web.outputTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runOutput()
            Web.cocoscats.runDatabase()
        editor = Web.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @staticmethod
    @bottle.route("/Reset")
    def __runReset():
        Web.inputTainted = False
        Web.analyzerTainted = False
        Web.translatorTainted = False
        Web.outputTainted = False
        Web.cocoscats.purgeContent()
        bottle.redirect("/")

    @bottle.route("/Translator")
    @bottle.route("/Translator/<action>")
    @bottle.route("/Translator/<action>", method="POST")
    def __runTranslator(action=None):
        header = Web.getHeader("Translator")
        footer = Web.getFooter()
        navigation = Web.getNavigation("Translator")
        path = Web.cocoscats.frameworkParams["translatorPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            Web.translatorTainted = True
            Web.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if Web.translatorTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runTranslator()
        editor = Web.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/View")
    @bottle.route("/View/<action>")
    @bottle.route("/View/<action>", method="POST")
    def __runView(action=None):
        header = Web.getHeader("View")
        footer = Web.getFooter()
        navigation = Web.getNavigation("View")
        body = """{0}""".format(navigation)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.hook("after_request")
    def __setSecurityHeaders():
        #bottle.response.set_header("Cache-Control", "no-cache,no-store,max-age=0,must-revalidate")
        bottle.response.set_header("Content-Security-Policy","script-src 'self'")
        bottle.response.set_header("Set-Cookie", "name=value; httpOnly")
        bottle.response.set_header("X-Content-Type-Options", "nosniff")
        bottle.response.set_header("X-Frame-Options", "deny")
        bottle.response.set_header("X-XSS-Protection", "1; mode=block")
        if Web.useHttps:
            bottle.response.set_header("Set-Cookie", "name=value; Secure")
            bottle.response.set_header("Strict-Transport-Security", "max-age=31536000")

    @bottle.route("/")
    @bottle.route("/Home")
    @bottle.route("/<path>")
    def __showHome(path="index.html"):
        return bottle.static_file(path, root="Web/html")

    @bottle.route("/Api/Test")
    def __test():
        return """{"Say":"testing, testing, testing ..."}"""
