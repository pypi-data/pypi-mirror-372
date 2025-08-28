import argparse

from hivebox.networking.web import WebServer


def main():
    parser = argparse.ArgumentParser(description='Run web server')
    args = vars(parser.parse_args())

    server = WebServer()
    server.start()
    try:
        while True:
            pass
    finally:
        server.stop()

if __name__ == '__main__':
    main()