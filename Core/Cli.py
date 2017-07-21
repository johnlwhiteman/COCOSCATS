from Core.Editor import Editor
from Core.Msg import Msg

class Cli():

    cocoscats = None

    def run(cocoscats):
        Cli.cocoscats = cocoscats
        Cli.cocoscats.purgeContent()
        Cli.__runInput()
        Cli.__runAnalyzer()
        Cli.__runTranslator()
        Cli.__runOutput()
        Cli.cocoscats.runDatabase()

    def __runAnalyzer():
        content = Cli.cocoscats.runAnalyzer()
        if Cli.cocoscats.isWorkflowEditTrue("Analyzer"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["analyzerPath"],
                            Cli.cocoscats.frameworkParams["analyzerPath"])
        if Cli.cocoscats.isWorkflowVerboseTrue("Analyzer"):
            Msg.showRaw(content)

    def __runEditor(inputPath, outputPath):
        editor = Editor()
        editor.run(inputPath, outputPath)

    def __runInput():
        content = Cli.cocoscats.runInput()
        if Cli.cocoscats.isWorkflowEditTrue("Input"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["inputPath"],
                            Cli.cocoscats.frameworkParams["inputPath"])
        if Cli.cocoscats.isWorkflowVerboseTrue("Input"):
            Msg.showRaw(content)

    def __runOutput():
        content = Cli.cocoscats.runOutput()
        if Cli.cocoscats.isWorkflowEditTrue("Output"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["outputPath"],
                            Cli.cocoscats.frameworkParams["outputPath"])
        if Cli.cocoscats.isWorkflowVerboseTrue("Output"):
            Msg.showRaw(content)

    def __runTranslator():
        content = Cli.cocoscats.runTranslator()
        if Cli.cocoscats.isWorkflowEditTrue("Translator"):
            Cli.__runEditor(Cli.cocoscats.frameworkParams["translatorPath"],
                            Cli.cocoscats.frameworkParams["translatorPath"])
        if Cli.cocoscats.isWorkflowVerboseTrue("Translator"):
            Msg.showRaw(content)
