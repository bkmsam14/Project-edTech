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
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        if self.path == "/tutor":
            try:
                result = handle_tutor_request(payload)
                self._send_json(HTTPStatus.OK, result)
            except AgentValidationError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        elif self.path == "/assessment":
            try:
                result = handle_assessment_request(payload)
                self._send_json(HTTPStatus.OK, result)
            except AgentValidationError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        else:
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"error": "Route not found", "available_routes": ["/health", "/tutor", "/assessment"]},
            )

    def log_message(self, format: str, *args) -> None:
        pass

    def _read_json_body(self) -> dict:
        raw_length = self.headers.get("Content-Length")
        if not raw_length or not raw_length.strip().isdigit() or int(raw_length) <= 0:
            raise ValueError("Content-Length header must be a positive integer")
        try:
            raw_body = self.rfile.read(int(raw_length))
        except Exception:
            raise ValueError("Request body must contain JSON")
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Request body must be valid JSON")
        if not isinstance(body, dict):
            raise ValueError("JSON body must be an object")
        return body

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
    server = build_http_server(host, port)
    print(f"EdTech agent API listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_http_server()
