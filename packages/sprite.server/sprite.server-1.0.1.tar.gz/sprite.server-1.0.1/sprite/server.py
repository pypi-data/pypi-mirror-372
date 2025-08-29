from http.server import HTTPServer
from netifaces import interfaces, ifaddresses, AF_INET
from .lib.util.constants import PROJECT_VERSION
from .lib.sprite_server import create_server


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=PROJECT_VERSION,
                        help='Show version number')
    parser.add_argument('port', action='store',
                        default=6060, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 6060]')
    args = parser.parse_args()
    sprite = create_server(args)
    HOST, PORT = '0.0.0.0', args.port
    with HTTPServer((HOST, PORT), sprite) as httpd:
        try:
            print('\u001b[33mSprite server is running.\nVersion: %s\nAvailable on:\u001b[0m' % PROJECT_VERSION)
            names = interfaces()
            for name in names:
                addresses = ifaddresses(name)
                if AF_INET in addresses.keys():
                    print('\u001b[32m  http://%s:%d\u001b[0m' % (addresses[AF_INET][0]['addr'], PORT))
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\u001b[33mSprite Server has been terminated.\u001b[0m')
            pass