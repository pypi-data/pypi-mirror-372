# ruff: noqa: T201
# Python 3 server example
import contextlib
import os.path
from http.server import BaseHTTPRequestHandler, HTTPServer
from inspect import getsourcefile

HERE = os.path.dirname(getsourcefile(lambda: 0))

hostname = "localhost"
serverport = 22222


class WaveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_path = os.path.abspath(os.path.join(HERE, "wave_home.html"))
            with open(html_path, mode="rb") as f:
                sign_in = f.read()
                f.close()
            self.wfile.write(sign_in)
        elif self.path == "/customers/sign_in":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_path = os.path.abspath(os.path.join(HERE, "wave_login.html"))
            with open(html_path, mode="rb") as f:
                sign_in = f.read()
                f.close()
            self.wfile.write(sign_in)
        elif self.path.startswith("/products/search_list"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_path = os.path.abspath(os.path.join(HERE, "wave_search_result.html"))
            with open(html_path, mode="rb") as f:
                sign_in = f.read()
                f.close()
            self.wfile.write(sign_in)
        elif self.path.startswith("/products/view/4636"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_path = os.path.abspath(os.path.join(HERE, "wave_item_page.html"))
            with open(html_path, mode="rb") as f:
                sign_in = f.read()
                f.close()
            self.wfile.write(sign_in)
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                bytes("<html><head><title>WaveServer</title></head>", "utf-8")
            )
            self.wfile.write(bytes(f"<p>Request: {self.path}</p>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(
                bytes("<p>This path is not mapped to any content.</p>", "utf-8")
            )
            self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):
        if self.path == "/customers/sign_in":
            self.send_response(301)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            message = "Hello, World! Here is a POST response"
            self.wfile.write(bytes(message, "utf8"))


if __name__ == "__main__":
    webserver = HTTPServer((hostname, serverport), WaveServer)
    print(f"Server started http://{hostname}:{serverport}", flush=True)

    with contextlib.suppress(KeyboardInterrupt):
        webserver.serve_forever()

    webserver.server_close()
    print("Server stopped.")
