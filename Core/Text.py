import ast

class Text():

    @staticmethod
    def isNothing(something):
        return something is None or str(something).strip() == ""

    @staticmethod
    def isTrue(something):
        return Text.toTrueOrFalse(something) == True

    @staticmethod
    def toTrueOrFalse(something):
        return ast.literal_eval(something)