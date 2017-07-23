import sys
import traceback
from Core.Msg import Msg

class Error():

    def handleError(msg, abortFlag=True):
        Msg.showError(str(msg))
        if abortFlag:
            sys.stderr.flush()
            sys.exit(1)

    def handleException(msg, showStackTraceFlag=True, abortFlag=True):
        Msg.showError(str(msg))
        if showStackTraceFlag:
            traceback.print_exc()
        if abortFlag:
            sys.stderr.flush()
            sys.exit(1)

    def raiseException(msg):
        raise Exception("COCOSCATS Exception: {0}".format(msg))