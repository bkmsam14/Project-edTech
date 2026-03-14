from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .service import AgentValidationError, handle_assessment_request, handle_tutor_request


class AgentHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "EdTechAgentsHTTP/1.0"

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"error": "Route not found", "available_routes": ["/health", "/tutor", "/assessment"]},
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "status": "ok",
                "service": "edtech-agents",
                "routes": ["/health", "/tutor", "/assessment"],
            },
        )

    def do_POST(self) -> None:
        try:
            payload = self._read_json_body()
        except ValueError as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return

        try:
            if self.path == "/tutor":
                response = handle_tutor_request(payload)
                self._send_json(HTTPStatus.OK, response)
                return
            if self.path == "/assessment":
                response = handle_assessment_request(payload)
                self._send_json(HTTPStatus.OK, response)
                return
        except AgentValidationError as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return

        self._send_json(
            HTTPStatus.NOT_FOUND,
            {"error": "Route not found", "available_routes": ["/health", "/tutor", "/assessment"]},
        )

    def log_message(self, format: str, *args) -> None:
        return

    def _read_json_body(self) -> dict:
        content_length = self.headers.get("Content-Length", "0").strip()
        if not content_length.isdigit():
            raise ValueError("Content-Length header must be a positive integer")

        body = self.rfile.read(int(content_length)) if int(content_length) > 0 else b""
        if not body:
            raise ValueError("Request body must contain JSON")

        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("Request body must be valid JSON") from error

        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_http_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), AgentHTTPRequestHandler)


def run_http_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = build_http_server(host=host, port=port)
    print(f"EdTech agent API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_http_server()