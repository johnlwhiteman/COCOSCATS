from Core.Editor import Editor
from Core.Msg import Msg

class Cmd():

    cocoscats = None

    def run(cocoscats):
        Cmd.cocoscats = cocoscats
        Cmd.cocoscats.purgeContent()
        Cmd.__runInput()
        Cmd.__runAnalyzer()
        Cmd.__runTranslator()
        Cmd.__runOutput()
        Cmd.cocoscats.updateDatabase()

    def __runAnalyzer():
        content = Cmd.cocoscats.runAnalyzer()
        if Cmd.cocoscats.isWorkflowEditTrue("Analyzer"):
            Cmd.__runEditor(Cmd.cocoscats.frameworkParams["analyzerPath"],
                            Cmd.cocoscats.frameworkParams["analyzerPath"])
        if Cmd.cocoscats.isWorkflowVerboseTrue("Analyzer"):
            Msg.showRaw(content)

    def __runEditor(inputPath, outputPath):
        editor = Editor()
        editor.run(inputPath, outputPath)

    def __runInput():
        content = Cmd.cocoscats.runInput()
        if Cmd.cocoscats.isWorkflowEditTrue("Input"):
            Cmd.__runEditor(Cmd.cocoscats.frameworkParams["inputPath"],
                            Cmd.cocoscats.frameworkParams["inputPath"])
        if Cmd.cocoscats.isWorkflowVerboseTrue("Input"):
            Msg.showRaw(content)

    def __runOutput():
        content = Cmd.cocoscats.runOutput()
        if Cmd.cocoscats.isWorkflowEditTrue("Output"):
            Cmd.__runEditor(Cmd.cocoscats.frameworkParams["outputPath"],
                            Cmd.cocoscats.frameworkParams["outputPath"])
        if Cmd.cocoscats.isWorkflowVerboseTrue("Output"):
            Msg.showRaw(content)

    def __runTranslator():
        content = Cmd.cocoscats.runTranslator()
        if Cmd.cocoscats.isWorkflowEditTrue("Translator"):
            Cmd.__runEditor(Cmd.cocoscats.frameworkParams["translatorPath"],
                            Cmd.cocoscats.frameworkParams["translatorPath"])
        if Cmd.cocoscats.isWorkflowVerboseTrue("Translator"):
            Msg.showRaw(content)
