import ast
import base64
import re

class Text():

    @staticmethod
    def encodeBase64(something):
        return str(base64.b64encode(bytes(something, "utf-8")))

    @staticmethod
    def getTextOnly(something):
        if Text.isNothing(something):
            return ""
        return something.strip()

    @staticmethod
    def isInt(something):
        try:
            int(something)
            return True
        except ValueError:
            return False

    @staticmethod
    def isNothing(something):
        return something is None or str(something).strip() == ""

    @staticmethod
    def isValidPathName(something):
         return not re.search(r'[^A-Za-z0-9_\-\\]', something)

    @staticmethod
    def isTrue(something):
        if isinstance(something, bool):
            return something
        if Text.isNothing(something):
            return False
        return Text.toTrueOrFalse(something) == True

    @staticmethod
    def toTrueOrFalse(something):
        if isinstance(something, bool):
            return something
        return ast.literal_eval(something)