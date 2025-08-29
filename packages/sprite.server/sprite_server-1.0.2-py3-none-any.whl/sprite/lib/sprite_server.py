import os
import stat
import cgi
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from jinja2 import Environment, PackageLoader
from urllib.parse import unquote
from .util.utils import format_date_time


def create_server(args):
    class SpriteServer(BaseHTTPRequestHandler):

        format = '%Y/%m/%d %H:%M:%S'
        log_format = '%Y-%m-%d %H:%M:%S.%f'

        def do_GET(self):
            root = os.getcwd()
            path = os.path.join(root, unquote(self.path[1:], 'utf-8'))
            if os.path.isfile(path):
                file = open(path, 'rb')
                buffer = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/download')
                self.end_headers()
                self.wfile.write(buffer)
            elif os.path.isdir(path):
                parent = self.__get_parent(path)
                (directories, files) = self.__get_list(path)
                env = Environment(loader=PackageLoader(__package__, '../template'))
                template = env.get_template('list.html')
                page = template.render(
                    parent=parent, directories=directories, files=files)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(page.encode())
            else:
                env = Environment(loader=PackageLoader(__package__, '../template'))
                template = env.get_template('error.html')
                page = template.render(url=self.path)
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(page.encode())

        def do_POST(self):
            try:
                _, pdict = cgi.parse_header(self.headers.get('Content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                multipart_data = cgi.parse_multipart(self.rfile, pdict)
                file_name, file_data = multipart_data.popitem()
                root = os.getcwd()
                path = os.path.join(root, self.path[1:], file_name)
                file = open(path, 'wb')
                file.write(file_data[0])

                self.send_response(200)
                data = {'message': 'Upload successful.'}
            except Exception:
                self.send_response(500)
                data = {'message': 'Upload failed.'}
            
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        def log_message(self, format: str, *args):
            print('[%s] [\u001b[33m%s\u001b[0m] %s' % (datetime.now().strftime(self.log_format)[:-3], self.command, self.headers.get('user-agent')))
            return

        def __get_parent(self, path):
            properties = os.stat(path)
            permission = stat.filemode(properties.st_mode)
            modification = format_date_time(properties.st_mtime, self.format)
            parent = {
                'permission': permission,
                'modification': modification
            }
            return parent

        def __get_list(self, path):
            directories = []
            files = []
            list = os.listdir(path)
            for item in list:
                item_path = os.path.join(path, item)
                properties = os.stat(item_path)
                permission = stat.filemode(properties.st_mode)
                modification = format_date_time(
                    properties.st_mtime, self.format)
                if os.path.isdir(item_path):
                    directories.append({
                        'permission': permission,
                        'modification': modification,
                        'name': item + '/'
                    })
                elif os.path.isfile(item_path):
                    files.append({
                        'permission': permission,
                        'modification': modification,
                        'size': properties.st_size,
                        'name': item
                    })
            return (directories, files)

    return SpriteServer
