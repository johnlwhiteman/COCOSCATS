import argparse
import glob
import os
from Core.Cfg import Cfg
from Core.Directory import Directory
from Core.Error import Error
from Core.File import File

def deleteSafe():
    try:
        for path in [
            "./",
            "./Core",
            "./Plugin",
            "./Plugin/Analyzer",
            "./Plugin/Demo",
            "./Plugin/IO",
            "./Plugin/Test",
            "./Plugin/Translator"]:
            Directory.delete("{0}/__pycache__".format(path))
            for path in glob.glob("./Test/Tmp/*"):
                File.delete(File.getCanonicalPath(path))
    except Exception as e:
        Error.handleException(e, True)

def deleteProtected(cfgPath):
    try:
        cfg = Cfg(cfgPath)
        cfg.load()
        for path in [
            "./Database/{0}.db".format(cfg.cfg["Database"]["Name"]),
            "./Database/CocoscatsTest.db",
            "./Vault/Certificate.pem",
            "./Vault/Password.json",
            "./Vault/PrivateKey.pem",
            "./Vault/PublicKey.pem"]:
            File.delete(path)
    except Exception as e:
        Error.handleException(e, True)

if __name__ == "__main__":
    cfgPath = "cfg.json"
    parser = argparse.ArgumentParser( \
        prog=os.path.basename(__file__),
        description="Cocoscats directory cleanup script",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--cfg", metavar="'cfg'", type=str,
                        default=cfgPath,
                        help="JSON configuration file")
    parser.add_argument("-F", "--force",
                        action="store_true",
                        help="Delete EVERYTHING including certificates, content files and content database")
    args = parser.parse_args()
    if args.cfg:
        cfgPath = args.cfg
    if not os.path.isfile(cfgPath):
        Error.handleError("Can't find JSON configuration file: {0}".format(cfgPath), True)
    if args.force:
        deleteProtected(cfgPath)
    deleteSafe()
