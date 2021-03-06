from pprint import pprint
import sys

class Msg():

    @staticmethod
    def flush(flushFlag=True):
        sys.stdout.flush()
        sys.stderr.flush()

    @staticmethod
    def show(msg):
        sys.stdout.write("\CoCoScatS: {0}\n".format(msg))

    @staticmethod
    def showAbort(msg):
        sys.stderr.write("\CoCoScatS: Abort: {0}\n".format(msg))

    @staticmethod
    def showError(msg):
        sys.stderr.write("\CoCoScatS: Error: {0}\n".format(msg))

    @staticmethod
    def showPretty(msg):
        sys.stdout.write("\n")
        pprint(msg)
        sys.stdout.write("\n")

    @staticmethod
    def showRaw(msg):
        sys.stdout.write("\n{0}\n".format(msg))

    @staticmethod
    def showWarning(msg):
        sys.stderr.write("\CoCoScatS: Warning: {0}\n".format(msg))
