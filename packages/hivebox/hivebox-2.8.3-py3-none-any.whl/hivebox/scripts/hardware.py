import argparse
from pathlib import Path
from hivebox.hardware.gpio import  GPIOSetup

path = Path(__file__).resolve().parent
print(path)

def main():
    parser = argparse.ArgumentParser(description='Install GPIO interface')
    parser.add_argument('--orangepi5b',  help='Install on OrangePi 5b', action='store_true')
    args = vars(parser.parse_args())

    if args.get('orangepi5b'):
        GPIOSetup.install_orangepi5b(library_path=path)
    else:
        raise RuntimeError('You must specify --orangepi5b')

if __name__ == '__main__':
    main()