#!/usr/bin/env python3
"""Static file server + data.gov API proxy for datagov-explorer."""
import http.server
import os
import sys
import urllib.request

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3456
DATAGOV_BASE = 'https://catalog.data.gov'

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/datagov/'):
            self.proxy_datagov()
        else:
            super().do_GET()

    def proxy_datagov(self):
        # Strip /datagov/ prefix and forward to catalog.data.gov
        rest = self.path[len('/datagov'):]  # keep leading slash
        target = DATAGOV_BASE + rest
        try:
            req = urllib.request.Request(target, headers={
                'User-Agent': 'Mozilla/5.0 DataGovExplorer/1.0',
                'Accept': 'application/json',
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'{{"error": "{e}"}}'.encode())

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    print(f'Data.gov Explorer running at http://localhost:{PORT}')
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        httpd.serve_forever()
