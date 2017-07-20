import os
import unittest
from Core.Cfg import Cfg
from Core.Framework import Framework
from Core.Misc import Misc
from Core.Msg import Msg

class Test(unittest.TestCase):

    def test_Cfg_checkIfCfgLoaded(self):
        cfg = Cfg()
        try:
            cfg.checkIfCfgLoaded()
            self.fail("check if loaded should have failed")
        except Exception as e:
            pass
        cfg.load("cfg.json")
        cfg.checkIfCfgLoaded()

    def test_Cfg_getPlugins(self):
        cfg = Cfg()
        cfg.load("cfg.json")
        for pluginType in cfg.pluginTypes:
            plugins = cfg.getPlugins(pluginType)
            self.assertTrue(
                len(plugins) > 0,
                "Found no expected plugins")

    def test_Cfg_getWorkflowPlugin(self):
        cfg = Cfg()
        cfg.load("cfg.json")
        for pluginType in ["Input", "Algorithm", "Output"]:
            plugins = cfg.getWorkflowPlugin(pluginType)
            self.assertTrue(
                len(plugins) > 0,
                "Found no expected plugin modules")

    def test_Cfg_loadCfg(self):
        cfg = Cfg()
        cfg.load("cfg.json")

    def test_Cfg_showCfg(self):
        cfg = Cfg()
        cfg.load("cfg.json")
        cfg.showCfg()

    def test_Cfg_verifyCfg(self):
        cfg = Cfg()
        cfg.load("cfg.json")
        cfg.verifyCfg()

    def test_Framework_getInstallDir(self):
        installDir = Framework.getInstallDir()
        self.assertTrue(
            os.path.isdir(installDir),
            "Incorrect installation directory")

    def test_Framework_getPluginFiles(self):
        pluginTypes = ["IO", "Algorithm", "Translator"]
        for pluginType in pluginTypes:
            plugins = Framework.getPluginFiles(pluginType)
            self.assertFalse(
                Misc.isNothing(plugins),
                "Missing plugins in {0}".format(pluginType)
            )

    def test_Framework_showAllPluginFiles(self):
        Framework.showAllPluginFiles()

    def test_Framework_showPluginFiles(self):
        pluginTypes = ["IO", "Algorithm", "Translator"]
        for pluginType in pluginTypes:
            Framework.showPluginFiles(pluginType)

if __name__ == '__main__':
    unittest.main()