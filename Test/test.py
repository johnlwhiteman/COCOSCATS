import os
import sys
import unittest
import warnings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from Core.Cfg import Cfg, CfgEditor
from Core.Cli import Cli
from Core.Cocoscats import Cocoscats
from Core.Error import Error
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg

class Test(unittest.TestCase):

    def setUp(self):
        self.testDir = Framework.getTestDir()
        self.databaseName = "CocoscatsTest"
        self.databasePath = "{0}/{1}".format(Framework.getDatabaseDir(), self.databaseName)
        self.cfgPath = "{0}/test.json".format(self.testDir)
        self.tmpCfgPath = "{0}/Tmp/tmp.json".format(self.testDir)
        warnings.simplefilter("ignore", category=DeprecationWarning)
        warnings.simplefilter("ignore", category=ImportWarning)

    def tearDown(self):
        pass

    def testCfgLoad(self):
        cfg = Cfg(self.cfgPath)
        cfg.load(False)

    def testCfgLoadAndVerify(self):
        cfg = Cfg(self.cfgPath)
        cfg.load(True)
        cfg = Cfg(self.cfgPath)
        cfg.load(False)
        cfg.verify()

    def testCfgShow(self):
        cfg = Cfg(self.cfgPath)
        cfg.load()
        cfg.show()

    def testCocoscatsInitialize(self):
        cocoscats = Cocoscats(self.cfgPath)
        cocoscats.initialize()

    def testCocoscatsOutputPlugins(self):
        File.delete(self.databasePath)
        plugins = []
        plugins.append(
            {
                "ProjectID": "TestTextFileOutput",
                "InputSource": "{0}/house.txt".format(self.testDir),
                "Database":
                {
                    "Name": self.databaseName,
                    "Enable": True,
                    "Debug": False,
                    "Rebuild": False
                },
                "Workflow":
                {
                    "Plugin": "TextFile",
                    "Method": "runOutput",
                    "Target": "{0}/Tmp/houseResults.txt".format(self.testDir),
                    "Edit": False,
                    "Debug": False
                }
            }
        )
        plugins.append(
            {
                "ProjectID": "TestHtmlFileOutput",
                "InputSource": "{0}/house.txt".format(self.testDir),
                "Database":
                {
                    "Name": self.databaseName,
                    "Enable": True,
                    "Debug": False,
                    "Rebuild": False
                },
                "Workflow":
                {
                    "Plugin": "HtmlFile",
                    "Method": "runOutput",
                    "Target": "{0}/Tmp/houseResults.html".format(self.testDir),
                    "Edit": False,
                    "Debug": False
                }
            }
        )
        plugins.append(
            {
                "ProjectID": "TestJsonFileOutput",
                "InputSource": "{0}/house.txt".format(self.testDir),
                "Database":
                {
                    "Name": self.databaseName,
                    "Enable": True,
                    "Debug": False,
                    "Rebuild": False
                },
                "Workflow":
                {
                    "Plugin": "JsonFile",
                    "Method": "runOutput",
                    "Target": "{0}/Tmp/houseResults.json".format(self.testDir),
                    "Edit": False,
                    "Debug": False
                }
            }
        )
        for plugin in plugins:
            cfgEditor = CfgEditor()
            cfgEditor.loadCfg(self.cfgPath)
            cfgEditor.setDatabase(plugin["Database"])
            cfgEditor.setProjectID(plugin["ProjectID"])
            cfgEditor.setWorkflowInputSource(plugin["InputSource"])
            cfgEditor.setWorkflowPlugin("Output", plugin["Workflow"])
            cfgEditor.saveCfg(self.tmpCfgPath)
            cocoscats = Cocoscats(self.tmpCfgPath)
            cocoscats.initialize()
            Cli.run(cocoscats)

    def testFrameworkGetInstallDir(self):
        installDir = Framework.getInstallDir()
        self.assertTrue(
            os.path.isdir(installDir),
            "Incorrect installation directory")

if __name__ == '__main__':
    unittest.main()
