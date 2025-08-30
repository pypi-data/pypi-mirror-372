"""Generic OAuth callback server for handling OAuth redirects."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import threading
import time
from typing import Callable, Optional
from urllib.parse import parse_qs, urlparse

from shared.oauth.template_loader import TemplateLoader


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callbacks."""

    def __init__(
        self,
        callback_func: Callable[[str, str], None],
        provider_name: str = "OAuth",
        *args,
        **kwargs,
    ):
        self.callback_func = callback_func
        self.provider_name = provider_name
        self.template_loader = TemplateLoader()
        super().__init__(*args, **kwargs)

    def do_GET(self):  # noqa: N802
        """Handle GET requests to the callback endpoint."""
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/auth/callback":
            # Parse query parameters
            query_params = parse_qs(parsed_url.query)

            # Extract code and state
            code = query_params.get("code", [None])[0]
            state = query_params.get("state", [None])[0]
            error = query_params.get("error", [None])[0]

            if error:
                self._send_error_response(error)
                self.callback_func(None, error)
            elif code and state:
                self._send_success_response()
                self.callback_func(code, state)
            else:
                self._send_error_response("Missing code or state parameter")
                self.callback_func(None, "invalid_request")
        elif parsed_url.path in {"/", "/status"}:
            self._send_status_page()
        else:
            self._send_404_response()

    def _send_success_response(self):
        """Send success response to browser."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_response = self.template_loader.render_success(self.provider_name)
        self.wfile.write(html_response.encode())

    def _send_status_page(self):
        """Send status page showing server is ready."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_response = self.template_loader.render_status(self.provider_name)
        self.wfile.write(html_response.encode())

    def _send_error_response(self, error_message: str):
        """Send error response to browser."""
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_response = self.template_loader.render_error(
            error_message, self.provider_name
        )
        self.wfile.write(html_response.encode())

    def _send_404_response(self):
        """Send 404 response."""
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_response = self.template_loader.render_404()
        self.wfile.write(html_response.encode())

    def log_message(self, format, *args):
        """Override to suppress default HTTP server logging."""


class OAuthCallbackServer:
    """Generic OAuth callback server for handling redirects from OAuth providers."""

    def __init__(self, port: int = 8080, provider_name: str = "OAuth"):
        self.port = port
        self.provider_name = provider_name
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.callback_result: Optional[tuple[str, str]] = None
        self.callback_error: Optional[str] = None
        self.running = False

        # Configure logging
        logging.basicConfig(level=logging.WARNING)

    def start(self, timeout: int = 300) -> tuple[Optional[str], Optional[str]]:
        """
        Start the server and wait for OAuth callback.

        Args:
            timeout: Maximum time to wait for callback in seconds

        Returns:
            tuple: (code, state) if successful, (None, error) if failed
        """
        try:
            # Create server with callback handler
            def handle_callback(code: Optional[str], error_or_state: str):
                if code:
                    self.callback_result = (code, error_or_state)
                else:
                    self.callback_error = error_or_state
                self.stop()

            # Create handler class with callback
            def handler_class(*args, **kwargs):
                return OAuthCallbackHandler(
                    handle_callback, self.provider_name, *args, **kwargs
                )

            # Start HTTP server on all interfaces
            self.server = HTTPServer(
                ("0.0.0.0", self.port),
                handler_class,  # noqa: S104
            )
            self.running = True

            # Start server in separate thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()

            # Wait for callback or timeout
            start_time = time.time()
            while self.running and (time.time() - start_time) < timeout:
                time.sleep(0.1)

                # Check if we got a result
                if self.callback_result:
                    return self.callback_result
                if self.callback_error:
                    return None, self.callback_error

            # Timeout
            self.stop()
            return None, "timeout"

        except OSError as e:
            if "Address already in use" in str(e):
                return None, f"port_{self.port}_in_use"
            return None, f"server_error: {e}"
        except (RuntimeError, ValueError) as e:
            return None, f"unexpected_error: {e}"

    def _run_server(self):
        """Run the HTTP server."""
        import contextlib

        with contextlib.suppress(OSError, RuntimeError):
            self.server.serve_forever()

    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=1)

    def get_callback_url(self) -> str:
        """Get the callback URL for this server."""
        return f"http://0.0.0.0:{self.port}/auth/callback"
