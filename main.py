from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("templates/index.html")
        elif pr_url.path == "/contact":
            self.send_html_file("templates/contact.html")
        elif pr_url.path == "/read":
            self.send_read_page()
        elif pr_url.path == "/message":
            self.send_html_file("templates/message.html")
        elif pr_url.path.startswith("/static/"):
            self.send_static_file(pr_url.path[1:])
        else:
            self.send_html_file("templates/error.html", 404)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode("utf-8"))
            message = {"username": data["username"][0], "message": data["message"][0]}
            self.save_message(message)
            self.send_html_file("templates/message.html")
        else:
            self.send_html_file("templates/error.html", 404)

    def send_html_file(self, filename, status=200, message=None):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            content = fd.read()
            if message:
                content = content.replace(b"{{ message }}", message.encode("utf-8"))
            self.wfile.write(content)

    def send_static_file(self, filename):
        file_path = filename
        if os.path.exists(file_path):
            self.send_response(200)
            if filename.endswith(".css"):
                self.send_header("Content-type", "text/css")
            elif filename.endswith(".png"):
                self.send_header("Content-type", "image/png")
            self.end_headers()
            with open(file_path, "rb") as fd:
                self.wfile.write(fd.read())
        else:
            self.send_html_file("templates/error.html", 404)

    def save_message(self, message):
        timestamp = datetime.now().isoformat()
        data_file = "storage/data.json"
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data[timestamp] = message
        with open(data_file, "w") as f:
            json.dump(data, f, indent=4)

    def send_read_page(self):
        data_file = "storage/data.json"
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                messages = json.load(f)
        else:
            messages = {}
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("read.html")
        content = template.render(messages=messages)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 8000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
