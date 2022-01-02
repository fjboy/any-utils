import sys

from anycode.common import cliparser
from anycode.common import log
from anyutils.base import fs
from anyutils.base import setpip
from anyutils.base import code
from anyutils.base import confeditor

LOG = log.getLogger(__name__)


def main():
    cli_parser = cliparser.SubCliParser('Fluent Python Utils Base')
    cli_parser.register_clis(fs.PyTac, fs.PyZip, setpip.SetPip,
                             code.JsonGet, code.Md5Sum,
                             confeditor.ConfigList,
                             code.GeneratePassword)
    try:
        cli_parser.call()
        return 0
    except KeyboardInterrupt:
        LOG.error("user interrupt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
