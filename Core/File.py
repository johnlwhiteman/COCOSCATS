import json
import os
from shutil import copyfile
from Core.Directory import Directory
from Core.Error import Error

class File():

    @staticmethod
    def copy(src, tgt):
        try:
            copyfile(src, tgt)
        except IOError as e:
            Error.handleException(e, True, True)

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
    def find(name):
        paths = []
        if File.exist(name):
            paths.append("{0}/{1}".format(File.getCanonicalPath(os.getcwd()), name))
        for directory in os.environ["PATH"].split(os.pathsep):
            path = "{0}/{1}".format(File.getCanonicalPath(directory), name)
            if File.exists(path):
                paths.append(path)
        if len(paths) < 1:
            return None
        return list(set(paths))

    @staticmethod
    def finds(names):
        paths = []
        for name in names:
            p = File.find(name)
            if p is not None:
                paths.extend(p)
        if len(paths) < 1:
            return None
        return list(set(paths))

    @staticmethod
    def getAbsPath(path):
        return File.getCanonicalPath(os.path.abspath(path))

    @staticmethod
    def getBasename(path):
        return os.path.basename(path)

    @staticmethod
    def getCanonicalPath(path):
        return path.replace('\\', '/')

    @staticmethod
    def getContent(path, asJson=False):
        content = None
        try:
            if asJson:
                with open(path, "r",  encoding="utf8") as fd:
                    content = json.load(fd)
            else:
                with open(path, "r",  encoding="utf8") as fd:
                    content = fd.read()
        except IOError as e:
            Error.handleException(e, True, True)
        return content

    @staticmethod
    def getName(path):
        return File.getCanonicalPath(os.path.basename(os.path.splitext(path)[0]))

    @staticmethod
    def getDirectory(path):
        return File.getCanonicalPath(os.path.abspath(os.path.join(path, os.pardir)))

    @staticmethod
    def setContent(path, content, asJson=False, asBytes=False, mkdirs=False):
        try:
            if mkdirs:
                Directory.make(File.getDirectory(path))
            if asJson:
                with open(path, "w", encoding="utf8") as fd:
                    json.dump(sample, fd)
            elif asBytes:
                with open(path, "wb") as fd:
                    fd.write(content)
            else:
                with open(path, "w", encoding="utf8") as fd:
                    fd.write(content)
        except IOError as e:
            Error.handleException(e, True, True)
