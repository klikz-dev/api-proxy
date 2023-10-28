from http.server import BaseHTTPRequestHandler
import os
import requests
import environ

env = environ.Env()
environ.Env.read_env(os.path.join('', '.env'))
BASE_URL = env.get_value('BASE_URL')
API_USERNAME = env.get_value('API_USERNAME')
API_TOKEN = env.get_value('API_TOKEN')


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        session = requests.Session()
        session.auth = (API_USERNAME, API_TOKEN)

        response = session.get(f"{BASE_URL}/conversations/")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response.text.encode('utf-8'))
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length).decode('utf-8')

        session = requests.Session()
        session.auth = (API_USERNAME, API_TOKEN)

        response = session.post(
            f"{BASE_URL}/conversations/",
            headers={'Content-Type': 'application/json'},
            data=request_body
        )

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response.text.encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version')
        self.end_headers()
        return
