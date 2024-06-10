import sys

from hat.drivers.snmp.manager.cli import main


if __name__ == '__main__':
    sys.argv[0] = 'hat-snmp-manager'
    sys.exit(main())
