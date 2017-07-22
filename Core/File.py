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
    def deletes(paths):
        for path in paths:
            File.delete(path)

    @staticmethod
    def exist(paths):
        for path in paths:
            if not File.exists(path):
                return False
        return True

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
    def getParentDirectory(path):
        return os.path.abspath(os.path.join(path, os.pardir))

    @staticmethod
    def makeDirectories(path):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def setContent(path, content, asBytes=False, mkdirs=False):
        try:
            if mkdirs:
                File.makeDirectories(File.getParentDirectory(path))
            if asBytes:
                with open(path, "wb") as fd:
                    fd.write(content)
            else:
                with open(path, "w", encoding="utf8") as fd:
                    fd.write(content)
        except IOError as e:
            Error.handleException(e, True)
