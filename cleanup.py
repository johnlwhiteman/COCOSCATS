import argparse
import os
from Core.Cfg import Cfg
from Core.Directory import Directory
from Core.Error import Error
from Core.File import File

PATHS = ["./COCOSCATS.egg-info", "./build",
         "./Core/__pycache__",  "./dist",
         "./Plugin/__pycache__", "./Plugin/Analyzer/__pycache__",
         "./Plugin/IO/__pycache__", "./Plugin/Translator/__pycache__",
         "./Demo/Simple/houseTranslated.html"]

def deletePaths(paths):
    for path in paths:
        if os.path.isfile(path):
            File.delete(path)
        elif os.path.isdir(path):
            Directory.delete(path)

def deleteProtectedPaths(cfgPath):
    try:
        cfg = Cfg()
        cfg.load(cfgPath)
        paths = [
            cfg.cfg["Database"]["Path"],
            "./Security/Certificate.pem",
            "./Security/Password.json",
            "./Security/PrivateKey.pem",
            "./Security/PublicKey.pem"
        ]
        deletePaths(paths)
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
    deletePaths(PATHS)
    if args.force:
        deleteProtectedPaths(cfgPath)
