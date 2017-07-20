# -*- coding: utf8 -*-
import os
from shutil import copyfile
from Core.Error import Error

class File():

    @staticmethod
    def copy(src, tgt):
        try:
            copyfile(src, tgt)
        except IOError as e:
            Error.handleException(e, True)

    @staticmethod
    def delete(path):
        if not os.path.isfile(path):
            return
        os.unlink(path)

    @staticmethod
    def exists(path):
        return os.path.isfile(path)

    @staticmethod
    def getContent(path):
        content = None
        try:
            with open(path, "r",  encoding="utf8") as fd:
                content = fd.read()
        except IOError as e:
            Error.handleException(e, True)
        return content

    @staticmethod
    def setContent(path, content):
        try:
            with open(path, "w", encoding="utf8") as fd:
                fd.write(content)
        except IOError as e:
            Error.handleException(e, True)
