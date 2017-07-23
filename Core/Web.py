from beaker.middleware import SessionMiddleware
import bottle
#from bottle_sslify import SSLify
import json
import re
import ssl
import sys
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
        self.__certificatePath = "./Security/Certificate.pem"
        self.__privateKeyPath = "./Security/PrivateKey.pem"
        self.__publicKeyPath = "./Security/PublicKey.pem"

    def run(self, handler):
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
            srv.socket,
            keyfile = self.__privateKeyPath,
            certfile = self.__certificatePath,
            server_side = True)
        srv.serve_forever()

    def setupCertificate(self):
        if not Text.isTrue(Web.cocoscats.cfg["Web"]["UseHttps"]):
            return
        if Text.isTrue(Web.cocoscats.cfg["Web"]["RefreshCertificate"]):
            File.deletes([self.__certificatePath,
                          self.__publicKeyPath,
                          self.__privateKeyPath])
        if not File.exist([self.__certificatePath,
                           self.__publicKeyPath,
                           self.__privateKeyPath]):
            Security.generateKeysAndCertificate(self.__privateKeyPath,
                                                self.__publicKeyPath,
                                                self.__certificatePath)

    def setupPassword(self):
        if not Text.isTrue(Web.cocoscats.cfg["Web"]["UseAuthentication"]):
            return
        path = "./Security/Password.json"
        if Text.isTrue(Web.cocoscats.cfg["Web"]["RefreshPassword"]):
            File.delete(path)
        if not File.exists(path):
            Security.createPasswordFile(path)

class Web(object):

    cocoscats = NotImplemented
    useHttps = NotImplemented
    useAuthentication = NotImplemented
    url = NotImplemented
    schema = NotImplemented

    def run(cocoscats):
        Web.cocoscats = cocoscats
        Web.useHttps = Text.isTrue(Web.cocoscats.cfg["Web"]["UseHttps"])
        Web.useAuthentication = Text.isTrue(Web.cocoscats.cfg["Web"]["UseAuthentication"])
        sessionOptions = {
            "session.type": "memory",
            "session.cookie_expires": 300,
            "session.auto": True
        }
        if Web.useHttps:
            Web.schema = "https"
            Web.url = "{0}://{1}:{2}/".format(Web.schema,
                                                Web.cocoscats.cfg["Web"]["Host"],
                                                Web.cocoscats.cfg["Web"]["Port"])
            server = WebSecurity(host=Web.cocoscats.cfg["Web"]["Host"],
                                 port=Web.cocoscats.cfg["Web"]["Port"])
            server.setupCertificate()
            server.setupPassword()
            threading.Thread(target=bottle.run,
                kwargs=dict(
                app = SessionMiddleware(bottle.app(), sessionOptions),
                debug = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Debug"]),
                reloader = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Reloader"]),
                server = server
                )).start()
        else:
            Web.schema = "http"
            Web.url = "{0}://{1}:{2}/".format(Web.schema,
                                              Web.cocoscats.cfg["Web"]["Host"],
                                              Web.cocoscats.cfg["Web"]["Port"])
            threading.Thread(target=bottle.run,
                kwargs=dict(
                app = SessionMiddleware(bottle.app(), sessionOptions),
                debug = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Debug"]),
                host = Web.cocoscats.cfg["Web"]["Host"],
                port = Web.cocoscats.cfg["Web"]["Port"],
                reloader = Text.toTrueOrFalse(Web.cocoscats.cfg["Web"]["Reloader"])
                )).start()
        for client in Web.cocoscats.cfg["Web"]["Browser"]:
            if Text.isNothing(client) or client == "default":
                if webbrowser.open(Web.url):
                    break
            else:
                if webbrowser.get(client).open(Web.url):
                    break


class WebApp(object):

    inputTainted = False
    analyzerTainted = False
    translatorTainted = False
    outputTainted = False

    @staticmethod
    def checkAuthentication():
        if not Web.useAuthentication:
            return
        if not Text.isTrue(WebApp.__getSession("Authenticated")):
            WebApp.__redirect("/Login")

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
        replaceHeader = {
            "title": title,
            "meta": meta,
            "css": css,
            "js": js
        }
        replaceMenu = {"LoginStatus": ""}
        if Web.useAuthentication:
            if Text.isTrue(WebApp.__getSession("Authenticated")):
                replaceMenu["LoginStatus"] = """ | <a href="/Logout">Logout</a>"""
            else:
                replaceMenu["LoginStatus"] = """ | <a href="/Login">Login</a>"""
        return """{0}{1}""".format(
            bottle.template("Web/Tpl/Header.tpl", replaceHeader),
            bottle.template("Web/Tpl/Menu.tpl", replaceMenu))

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

    @staticmethod
    def __getSession(name):
        session = bottle.request.environ.get('beaker.session')
        if name not in session:
            return None
        return session[name]

    @staticmethod
    def __redirect(path, delay=None):
        url = "{0}://{1}:{2}{3}".format(Web.schema,
                                      Web.cocoscats.cfg["Web"]["Host"],
                                      Web.cocoscats.cfg["Web"]["Port"],
                                      path)
        if delay is None:
            bottle.redirect(url)
            return
        bottle.response.set_header("REFRESH", "{0};{1}".format(delay, url))

    @bottle.route("/Analyzer")
    @bottle.route("/Analyzer/<action>")
    @bottle.route("/Analyzer/<action>", method="POST")
    def __runAnalyzer(action=None):
        WebApp.checkAuthentication()
        header = WebApp.getHeader("Analyzer")
        footer = WebApp.getFooter()
        navigation = WebApp.getNavigation("Analyzer", 2)
        path = Web.cocoscats.frameworkParams["analyzerPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            WebApp.analyzerTainted = True
            WebApp.translatorTainted = False
            WebApp.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if WebApp.analyzerTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runAnalyzer()
        editor = WebApp.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Input")
    @bottle.route("/Input/<action>")
    @bottle.route("/Input/<action>", method="POST")
    def __runInput(action=None):
        WebApp.checkAuthentication()
        header = WebApp.getHeader("Input")
        footer = WebApp.getFooter()
        navigation = WebApp.getNavigation("Input", 1)
        path = Web.cocoscats.frameworkParams["inputPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            WebApp.inputTainted = True
            WebApp.analyzerTainted = False
            WebApp.translatorTainted = False
            WebApp.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if WebApp.inputTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runInput()
        editor = WebApp.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/Output")
    @bottle.route("/Output/<action>")
    @bottle.route("/Output/<action>", method="POST")
    def __runOutput(action=None):
        WebApp.checkAuthentication()
        header = WebApp.getHeader("Output")
        footer = WebApp.getFooter()
        navigation = WebApp.getNavigation("Output", 4)
        path = Web.cocoscats.frameworkParams["outputPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            WebApp.outputTainted = True
            Web.cocoscats.runDatabase()
            return "Successfully saved to '" + path + "'"
        content = None
        if WebApp.outputTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runOutput()
            Web.cocoscats.runDatabase()
        editor = WebApp.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @staticmethod
    @bottle.route("/Reset")
    def __runReset():
        WebApp.checkAuthentication()
        WebApp.inputTainted = False
        WebApp.analyzerTainted = False
        WebApp.translatorTainted = False
        WebApp.outputTainted = False
        Web.cocoscats.purgeContent()
        #bottle.redirect(Web.url)
        WebApp.__redirect("/Input")

    @bottle.route("/Translator")
    @bottle.route("/Translator/<action>")
    @bottle.route("/Translator/<action>", method="POST")
    def __runTranslator(action=None):
        WebApp.checkAuthentication()
        header = WebApp.getHeader("Translator")
        footer = WebApp.getFooter()
        navigation = WebApp.getNavigation("Translator", 3)
        path = Web.cocoscats.frameworkParams["translatorPath"]
        if not action is None and action == "Save":
            File.setContent(path, bottle.request.forms.Content)
            WebApp.translatorTainted = True
            WebApp.outputTainted = False
            return "Successfully saved to '" + path + "'"
        content = None
        if WebApp.translatorTainted:
            content = File.getContent(path)
        else:
            content = Web.cocoscats.runTranslator()
        editor = WebApp.getEditor(content)
        body = """{0}{1}""".format(navigation, editor)
        return "{0}{1}{2}".format(header, body, footer)

    @bottle.route("/View")
    @bottle.route("/View/<action>")
    @bottle.route("/View/<action>", method="POST")
    def __runView(action=None):
        WebApp.checkAuthentication()
        header = WebApp.getHeader("View")
        footer = WebApp.getFooter()
        navigation = WebApp.getNavigation("View", 4)
        body = """{0}""".format(navigation)
        return "{0}{1}{2}".format(header, body, footer)

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

    @staticmethod
    def __setSession(name, value):
        session = bottle.request.environ.get('beaker.session')
        session.httponly = True
        session.secure = True
        session[name] = value
        session.save()

    @bottle.route("/Admin")
    @bottle.route("/Administration")
    def __showAdministration():
        WebApp.checkAuthentication()
        session = bottle.request.environ.get('beaker.session')
        body  = """
<h2>Session Variables</h2>
{0}
""".format(session)
        return """{0}{1}{2}""".format(
            WebApp.getHeader("Documentation"),
            body,
            WebApp.getFooter())

    @bottle.route("/Doc")
    @bottle.route("/Docs")
    @bottle.route("/Documentation")
    def __showDocumentation():
        WebApp.checkAuthentication()
        return """{0}{1}{2}""".format(
            WebApp.getHeader("Documentation"),
            bottle.template("Web/Tpl/Documentation.tpl", {}),
            WebApp.getFooter())

    @bottle.route("/")
    @bottle.route("/<path>")
    def __showIndex(path="index.html"):
        #WebApp.__checkAuthentication()
        #return bottle.static_file(path, root="Web/html")
        return """{0}{1}{2}""".format(
            WebApp.getHeader("Welcome to Cocoscats"),
            bottle.template("Web/Tpl/Index.tpl", {}),
            WebApp.getFooter())

    @bottle.route("/Login")
    @bottle.route("/Login", method="POST")
    def __showLogin():
        p = bottle.request.forms.get("password")
        if p is not None:
            if Security.verifyPasswordByFile(p, "./Security/Password.json"):
                bottle.request.environ.get('beaker.session').invalidate()
                WebApp.__setSession("Authenticated", "True")
                WebApp.__redirect("/Input")
                return ""
            else:
                WebApp.__setSession("authenticated", "False")
        return """{0}{1}{2}""".format(
            WebApp.getHeader("Login"),
            bottle.template("Web/Tpl/Login.tpl", {}),
            WebApp.getFooter())

    @bottle.route("/Logout")
    def __showLogout():
        bottle.request.environ.get('beaker.session').invalidate()
        WebApp.__redirect("/", 2)
        return """{0}{1}{2}""".format(
            WebApp.getHeader("Login"),
            bottle.template("Web/Tpl/Logout.tpl", {}),
            WebApp.getFooter())

class WebApi(WebApp):

    @bottle.route("/Api/GetPlugins")
    @bottle.route("/Api/GetPlugins/<pluginType>")
    def __getPlugins(pluginType=None):
        WebApi.checkAuthentication()
        if pluginType == None:
            return Web.cocoscats.getPlugins()
        return Web.cocoscats.getPluginsByType(pluginType)