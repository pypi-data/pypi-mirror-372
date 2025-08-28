import argparse

from hivebox.networking.dhcp import DHCPSetup


def main():
    parser = argparse.ArgumentParser(description='Install DHCP server')
    parser.add_argument('--rpi5', help='Install on RaspberryPi 5', action='store_true')
    parser.add_argument('--orangepi5b', help='Install on OrangePi 5b', action='store_true')
    args = vars(parser.parse_args())

    if args.get('rpi5'):
        DHCPSetup.install_rpi5()
    elif args.get('orangepi5b'):
        DHCPSetup.install_orangepi5b()
    else:
        raise RuntimeError('You must specify either --rpi5 or --orangepi5b')

if __name__ == '__main__':
    main()