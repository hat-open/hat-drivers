import sys

from hat.drivers.iec61850.manager.main import main


if __name__ == '__main__':
    sys.argv[0] = 'hat-iec61850-manager'
    sys.exit(main())
