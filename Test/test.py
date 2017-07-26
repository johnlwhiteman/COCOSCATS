import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from Core.Cfg import Cfg
from Core.Cocoscats import Cocoscats
from Core.Error import Error
from Core.Framework import Framework
from Core.Msg import Msg

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCfgLoad(self):
        cfg = Cfg()
        cfg.load("cfg.json", False)

    def testCfgLoadAndVerify(self):
        cfg = Cfg()
        cfg.load("cfg.json", True)
        cfg = Cfg()
        cfg.load("cfg.json", False)
        cfg.verify()

    def testCfgShow(self):
        cfg = Cocoscats()
        cfg.load()
        cfg.show()

    def testCocoscatsInitialize(self):
        cocoscats = Cocoscats()
        cocoscats.initialize("cfg.json")

    def testFrameworkGetInstallDir(self):
        installDir = Framework.getInstallDir()
        self.assertTrue(
            os.path.isdir(installDir),
            "Incorrect installation directory")

if __name__ == '__main__':
    unittest.main()
