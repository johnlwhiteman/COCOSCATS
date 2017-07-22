import argparse
import os
import sys
from Core.Cli import Cli
from Core.Cocoscats import Cocoscats
from Core.Error import Error
from Core.Msg import Msg
from Core.Web import Web

if __name__ == "__main__":
    step = 1
    title = "Input"
    cfgPath = "cfg.json"
    parser = argparse.ArgumentParser( \
        prog=os.path.basename(__file__),
        description="Does something useful",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--cfg", metavar="'cfg'", type=str,
                        default=cfgPath,
                        help="JSON configuration file")
    parser.add_argument("-C", "--cli",
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
        if args.cli:
            Cli.run(cocoscats)
        elif args.web:
            Web.run(cocoscats)
        else:
            Error.handleError("You must specify either -C or -W to run in cli or web mode respectively", True)
    except Exception as e:
        Error.handleException(e, True)
    Msg.show("Script Completed")
