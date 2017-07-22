import os
import shutil
from Core.Error import Error

class Directory():

    @staticmethod
    def delete(path):
        shutil.rmtree(path)

    @staticmethod
    def deletes(paths):
        for path in paths:
            Directory.delete(path)

    @staticmethod
    def exist(paths):
        for path in paths:
            if not Directory.exists(path):
                return False
        return True

    @staticmethod
    def exists(path):
        return os.path.isdir(path)

    @staticmethod
    def getCanonicalPath(path):
        return path.replace('\\', '/')

    @staticmethod
    def make(path):
        os.makedirs(path, exist_ok=True)