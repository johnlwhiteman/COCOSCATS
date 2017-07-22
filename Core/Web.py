import bottle
#from bottle_sslify import SSLify
import json
import re
import ssl
import threading
import time
import webbrowser
from wsgiref.simple_server import make_server, WSGIRequestHandler
from Core.File import File
from Core.Security import Security
from Core.Text import Text

# Reference: http://www.socouldanyone.com/2014/01/bottle-with-ssl.html
# Use: C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s
class WebSecurity(bottle.ServerAdapter):

    def __init__(self, *args, **kwargs):
        super(WebSecurity, self).__init__(*args, **kwargs)
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

    def setupCertificate(self):
        certificatePath = Web.cocoscats.cfg["Web"]["Security"]["Certificate"]
        publicKeyPath = Web.cocoscats.cfg["Web"]["Security"]["PublicKey"]
        privateKeyPath = Web.cocoscats.cfg["Web"]["Security"]["PrivateKey"]
        if Text.isTrue(Web.cocoscats.cfg["Web"]["Security"]["AlwaysGenerate"]):
            File.deletes([certificatePath, publicKeyPath, privateKeyPath])
        if not File.exist([certificatePath, publicKeyPath, privateKeyPath]):
            Security.generateKeysAndCertificate(privateKeyPath, publicKeyPath, certificatePath)

class Web(object):

    cocoscats = None
    inputTainted = False
    analyzerTainted = False
    translatorTainted = False
    outputTainted = False

    # Get Methods ###########################
    @staticmethod
    def getEditor(content):
        replace = {"content": content}
        return bottle.template("Web/Tpl/Editor.tpl", replace)

    @staticmethod
    def getFooter():
        replace = {"year": "2017"}
        year = time.strftime("%Y")
        if year != replace["year"]:
            replace["year"] = "{0}-{1}".format(replace["year"], year)
        return bottle.template("Web/Tpl/Footer.tpl", replace)

    @staticmethod
    def getHeader(title,  meta="", css="", js=""):
        replace = {
            "title": title,
            "meta": meta,
            "css": css,
            "js": js
        }
        return """{0}{1}""".format(
            bottle.template("Web/Tpl/Header.tpl", replace),
            bottle.template("Web/Tpl/Menu.tpl", replace))

    @staticmethod
    def getNavigation(title, step):
        replace = {
            "title": title,
            "step": step,
            "Input": "Input",
            "Analyzer": "Analyzer",
            "Translator": "Translator",
            "Output": "Output",
            "View": "View"
        }
        if title == "Input":
            replace["Input"] = """<span id="navTitle">Input</span>"""
            replace["Analyzer"] = """<a href="/Analyzer">Analyzer</a>"""
        elif title == "Analyzer":
            replace["Input"]  = """<a href="/Input">Input</a>"""
            replace["Analyzer"] = """<span id="navTitle">Analyzer</span>"""
            replace["Translator"]  = """<a href="/Translator">Translator</a>"""
        elif title == "Translator":
            replace["Input"] = """<a href="/Input">Input</a>"""
            replace["Analyzer"] = """<a href="/Analyzer">Analyzer</a>"""
            replace["Translator"] = """<span id="navTitle">Translator</span>"""
            replace["Output"] = """<a href="/Output">Output</a>"""
        elif title == "Output":
            replace["Input"] = """<a href="/Input">Input</a>"""
            replace["Analyzer"] = """<a href="/Analyzer">Analyzer</a>"""
            replace["Translator"] = """<a href="/Translator">Translator</a>"""
            replace["Output"] = """<span id="navTitle">Output</span>"""
            replace["View"] = """<a href="/View">View</a>"""
        elif title == "View":
            replace["Input"] = """<a href="/Input">Input</a>"""
            replace["Analyzer"] = """<a href="/Analyzer">Analyzer</a>"""
            replace["Translator"] = """<a href="/Translator">Translator</a>"""
            replace["Output"] = """<a href="/Output">Output</a>"""
            replace["View"] = """<span id="navTitle">View</span>"""
        return bottle.template("Web/Tpl/Navigation.tpl", replace)


    # Set Methods ###########################
    @bottle.get("/Web/Css/<path:re:.*\.css>")
    def __setCssPath(path):
        return bottle.static_file(path, root="Web/Css")

    @bottle.get("/Web/Html/<path:re:.*\.html>")
    def __setHtmlPath(path):
        return bottle.static_file(path, root="Web/Html")

    @bottle.get("/Web/Img/<path:re:.*\.(jpg|png)>")
    def __setImgPath(path):
        return bottle.static_file(path, root="Web/Img")

    @bottle.get("/Web/Js/<path:re:.*\.js>")
    def __setJsPath(path):
        return bottle.static_file(path, root="Web/Js")

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

    def run(cocoscats):
        Web.cocoscats = cocoscats
        Web.useHttps = Text.isTrue(Web.cocoscats.cfg["Web"]["Security"]["UseHttps"])
        schema = None
        if Web.useHttps:
            server = WebSecurity(host=Web.cocoscats.cfg["Web"]["Host"],
                                 port=Web.cocoscats.cfg["Web"]["Port"])
            server.setupCertificate()
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
        navigation = Web.getNavigation("Analyzer", 2)
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
        navigation = Web.getNavigation("Input", 1)
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
        navigation = Web.getNavigation("Output", 4)
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
        navigation = Web.getNavigation("Translator", 3)
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
        navigation = Web.getNavigation("View", 4)
        body = """{0}""".format(navigation)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Documentation")
    @bottle.route("/Documentation")
    def __showDocumentation():
        return """{0}{1}{2}""".format(
            Web.getHeader("Documentation"),
            bottle.template("Web/Tpl/Documentation.tpl", {}),
            Web.getFooter())

    @bottle.route("/")
    @bottle.route("/<path>")
    def __showIndex(path="index.html"):
        return """{0}{1}{2}""".format(
            Web.getHeader("Welcome to Cocoscats"),
            bottle.template("Web/Tpl/Index.tpl", {}),
            Web.getFooter())


        #return bottle.static_file(path, root="Web/html")


class WebApi(object):

    @bottle.route("/Api/GetPlugins/<pluginType>")
    def __getPlugins(pluginType):
        return Web.cocoscats.getPlugins(pluginType)


class WebApp(object):
    pass
    # The actual content goes here
