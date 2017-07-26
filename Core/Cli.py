from Core.Editor import Editor
from Core.Msg import Msg
from Core.Text import Text

class Cli():

    cocoscats = None

    def run(cocoscats):
        Cli.cocoscats = cocoscats
        Cli.cocoscats.purgeContent()
        Cli.__runInput()
        Cli.__runAnalyzer()
        Cli.__runTranslator()
        Cli.__runOutput()
        Cli.cocoscats.updateDatabase()
        #Cli.__runDemo()

    def __runAnalyzer():
        Msg.show("Execute: Analyzer Stage")
        content = Cli.cocoscats.runAnalyzer()
        if Cli.cocoscats.isWorkflowEditTrue("Analyzer"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["analyzerPath"],
                            Cli.cocoscats.frameworkParams["analyzerPath"])
        if Cli.cocoscats.isWorkflowDebugTrue("Analyzer"):
            Msg.showRaw(content)

    def __runDemo():
        if not Cli.cocoscats.isWorkflowDemoEnabled() or \
            Cli.cocoscats.getWorkflowDemoPluginCount() < 1:
            return
        Msg.show("Execute: Demo Stage")
        choices = Cli.cocoscats.getWorkflowDemoPluginChoices()
        menu = """-----------------------------------------------
Please make a selection to run demo or 'x' to exit.\n"""
        i = 1
        for choice in choices:
            menu = """{0}
[{1}]: {2}::{3}()""".format(menu, i, choice["Name"], choice["Method"])
            i += 1
        menu = """{0}
[x]: Exit
""".format(menu)
        errMsg = "Error: Valid options are: [1-{0}]".format(i-1)
        while True:
            Msg.showRaw(menu)
            response = input()
            if response == "x" or response == "X":
                break
            if not Text.isInt(response):
                Msg.showRaw(errMsg)
                continue
            response = int(response)
            if response < 1 or response >= i:
                Msg.showRaw(errMsg)
                continue
            j = response - 1
            ret = Cli.cocoscats.runDemo(choices[j]["Name"],
                                        choices[j]["Method"])
            if ret:
                Msg.showWarning("Demo returned an error")

    def __runEditor(inputPath, outputPath):
        editor = Editor()
        editor.run(inputPath, outputPath)

    def __runInput():
        Msg.show("Execute: Input Stage")
        content = Cli.cocoscats.runInput()
        if Cli.cocoscats.isWorkflowEditTrue("Input"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["inputPath"],
                            Cli.cocoscats.frameworkParams["inputPath"])
        if Cli.cocoscats.isWorkflowDebugTrue("Input"):
            Msg.showRaw(content)

    def __runOutput():
        Msg.show("Execute: Output Stage")
        content = Cli.cocoscats.runOutput()
        if Cli.cocoscats.isWorkflowEditTrue("Output"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["outputPath"],
                            Cli.cocoscats.frameworkParams["outputPath"])
        if Cli.cocoscats.isWorkflowDebugTrue("Output"):
            Msg.showRaw(content)

    def __runTranslator():
        Msg.show("Execute: Translation Stage")
        content = Cli.cocoscats.runTranslator()
        if Cli.cocoscats.isWorkflowEditTrue("Translator"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["translatorPath"],
                            Cli.cocoscats.frameworkParams["translatorPath"])
        if Cli.cocoscats.isWorkflowDebugTrue("Translator"):
            Msg.showRaw(content)
