#!/usr/bin/env python3
"""Servidor HTTP mínimo para los tests de salkit/http: python3 mock_server.py PUERTO"""
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def reply(self, code, body, headers=None, close=True):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        if close:
            self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/chunked":
            self.send_response(200)
            self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Connection", "close")
            self.end_headers()
            for part in (b"hello ", b"chunked ", b"world"):
                self.wfile.write(b"%x\r\n%s\r\n" % (len(part), part))
            self.wfile.write(b"0\r\n\r\n")
        elif self.path == "/slow":
            time.sleep(3)
            self.reply(200, "late")
        elif self.path == "/big":
            self.reply(200, "x" * 1_000_000)
        elif self.path == "/nolen":
            self.send_response(200)
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(b"until-close")
        elif self.path == "/notfound":
            self.reply(404, json.dumps({"error": "nope"}), {"X-Custom": "Val"})
        else:
            self.reply(200, "ok", {"X-Custom": "Val"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(n).decode()
        out = {
            "len": n,
            "body": body,
            "auth": self.headers.get("Authorization", ""),
            "ctype": self.headers.get("Content-Type", ""),
        }
        if self.path == "/sse":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Connection", "close")
            self.end_headers()
            for part in (b"data: one\n\n", b"data: tw", b"o\r\n\r\ndata: [DONE]\n\n"):
                self.wfile.write(b"%x\r\n%s\r\n" % (len(part), part))
                self.wfile.flush()
                time.sleep(0.05)
            self.wfile.write(b"0\r\n\r\n")
            return
        code = 429 if self.path == "/busy" else 200
        self.reply(code, json.dumps(out))


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
