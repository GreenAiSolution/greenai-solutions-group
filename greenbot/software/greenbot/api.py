"""Local REST API (stdlib only). The GreenAI Digital app / cloud relay talks to this.

GET  /status          POST /start   POST /pause   POST /dock   POST /clear_error
GET  /schedule        POST /schedule {"weekday":0,"time":"09:00"}
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def make_handler(robot, scheduler, token):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _authed(self):
            if self.headers.get("Authorization") != f"Bearer {token}":
                self._send(401, {"error": "unauthorized"})
                return False
            return True

        def do_GET(self):
            if not self._authed():
                return
            if self.path == "/status":
                self._send(200, robot.status())
            elif self.path == "/schedule":
                self._send(200, {"entries": scheduler.as_list()})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            if not self._authed():
                return
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/start":
                self._send(200, {"ok": robot.start()})
            elif self.path == "/pause":
                robot.pause(); self._send(200, {"ok": True})
            elif self.path == "/dock":
                robot.go_dock(); self._send(200, {"ok": True})
            elif self.path == "/clear_error":
                robot.clear_error(); self._send(200, {"ok": True})
            elif self.path == "/schedule":
                scheduler.add(int(body["weekday"]), str(body["time"]))
                self._send(200, {"entries": scheduler.as_list()})
            else:
                self._send(404, {"error": "not found"})

        def log_message(self, *a):
            pass

    return H


def serve(robot, scheduler, token, host="0.0.0.0", port=8080):
    HTTPServer((host, port), make_handler(robot, scheduler, token)).serve_forever()
