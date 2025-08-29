from http.server import HTTPServer
import psutil, socket
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
            items = psutil.net_if_addrs().items()
            for iface, addrs in items:
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        print('\u001b[32m  http://%s:%d\u001b[0m' % (addr.address, PORT))
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\u001b[33mSprite Server has been terminated.\u001b[0m')
            pass