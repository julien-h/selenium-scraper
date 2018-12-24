import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from os.path import join
from random import randint


HOST = 'localhost'
PORT = 8889
HTML_DIR = 'html'


class FileHandler(BaseHTTPRequestHandler):

    # Match between endpoints and local files
    def do_GET(self):
        responses = {
            '/login': 'login.html',
            '/submit': 'welcome.html',
            '/welcome': 'welcome.html',
            '/list': 'list.html',
            '/resource1': 'ok.html',
            '/resource2': 'ok.html',
            '/resource3': 'ok.html',
            '/img': 'img.jpg'
        }
        endpoint = self.path.split('?')[0]
        if endpoint in responses:
            self.serve(endpoint, responses[endpoint])
        else:
            self.send_error(404, 'Not found')

    # Serve the response for a matched endpoint
    def serve(self, endpoint, filename):
        self.send_response(200)
        self.send_content(filename)

    # Send the content of `filename` to client
    def send_content(self, filename):
        mime_type = 'image/jpg' if filename.endswith('jpg') else 'text/html'
        self.send_header('Content-type', mime_type)
        self.end_headers()
        self.wfile.write(open(join(HTML_DIR, filename), 'rb').read())


class CookieHandler(FileHandler):

    # Add cookie logic to super().serve
    def serve(self, endpoint, filename):
        logged_in = self.is_logged_in()
        still_valid = randint(0, 5)
        bypass_invalidation = endpoint in ['/img', '/welcome']

        if logged_in and (still_valid or bypass_invalidation):
            self.serve_when_logged_in(endpoint, filename)
        else:
            self.serve_when_not_logged_in(endpoint, filename)

    def serve_when_logged_in(self, endpoint, filename):
        if endpoint in ['/login', '/submit']:
            self.send_response(302)
            self.send_header('Location', '/welcome')
            self.end_headers()
        else:
            super().serve(endpoint, filename)

    def serve_when_not_logged_in(self, endpoint, filename):
        if endpoint == '/login':
            super().serve(endpoint, filename)
            return
        elif endpoint == '/submit':
            self.send_response(302)
            self.send_header('Location', '/welcome')
            self.send_header('Set-Cookie', 'login=1')
            self.end_headers()
        else:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.send_header('Set-Cookie', 'login=0')
            self.end_headers()

    def is_logged_in(self):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        cookie_logged_in = int(cookies['login'].value) if 'login' in cookies else 0
        return cookie_logged_in


if __name__ == '__main__':
    httpd = HTTPServer((HOST, PORT), CookieHandler)
    print(time.asctime(), f'Starting server - http://{HOST}:{PORT}/login')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), f'Server Stopped - http://{HOST}:{PORT}/')
