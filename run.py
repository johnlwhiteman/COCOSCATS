import argparse
import os
import sys
from Core.Cocoscats import Cocoscats
from Core.Error import Error
from Core.Cmd import Cmd
from Core.Database import Database
from Core.Msg import Msg
from Core.Web import Web

if __name__ == "__main__":
    cfgPath = "cfg.json"
    parser = argparse.ArgumentParser( \
        prog=os.path.basename(__file__),
        description="Does something useful",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--cfg", metavar="'cfg'", type=str,
                        default=cfgPath,
                        help="JSON configuration file")
    parser.add_argument("-C", "--cmd",
                        action="store_true",
                        help="Run in command line mode")
    parser.add_argument("-W", "--web",
                        action="store_true",
                        help="Run in web mode")
    args = parser.parse_args()
    if args.cfg:
        cfgPath = args.cfg
    if not os.path.isfile(cfgPath):
        Error.handleError("Can't find JSON configuration file: {0}".format(cfgPath), True)
    try:
        cocoscats = Cocoscats()
        cocoscats.initialize(cfgPath)
        if args.cmd:
            Cmd.run(cocoscats)
        elif args.web:
            Web.run(cocoscats)
        else:
            Error.handleError("You must specify either -C or -W mode to run", True)
    except Exception as e:
        Error.handleException(e, True)
    Msg.show("Script Completed")
