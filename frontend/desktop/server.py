"""
MCP Protocol Studio Desktop Local Embedded HTTP Server
======================================================
Multithreaded local server with SPA fallback support, MIME types registration,
and caching prevention for client-side Vue routing.
"""

import os
import urllib.parse
import mimetypes
import socketserver
import http.server
from desktop.config import get_dist_dir


def init_mime_types():
    """Ensure standard web MIME types are recognized on Windows."""
    mimetypes.init()
    mimetypes.add_type('text/html', '.html')
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('application/javascript', '.mjs')
    mimetypes.add_type('text/css', '.css')
    mimetypes.add_type('image/svg+xml', '.svg')
    mimetypes.add_type('image/png', '.png')
    mimetypes.add_type('image/jpeg', '.jpg')
    mimetypes.add_type('image/x-icon', '.ico')
    mimetypes.add_type('font/woff2', '.woff2')
    mimetypes.add_type('font/woff', '.woff')
    mimetypes.add_type('font/ttf', '.ttf')
    mimetypes.add_type('application/json', '.json')


# Auto-initialize on module import
init_mime_types()


class SPAHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP Request Handler with SPA fallback support and caching prevention.
    Routes all missing file requests to index.html for client-side Vue routing.
    """
    def __init__(self, *args, directory=None, **kwargs):
        self.spa_dist_dir = directory or get_dist_dir()
        super().__init__(*args, directory=self.spa_dist_dir, **kwargs)

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging in console
        pass

    def end_headers(self):
        # Prevent aggressive caching in desktop app
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        clean_path = parsed.path.lstrip('/')

        # Handle nested route asset requests (e.g. /plugins/123/assets/...)
        if 'assets/' in clean_path:
            clean_path = clean_path[clean_path.find('assets/'):]
            self.path = '/' + clean_path

        target_file = os.path.join(self.spa_dist_dir, clean_path)

        # If path is empty, points to directory, or file does not exist -> SPA fallback to index.html
        if not clean_path or not os.path.isfile(target_file):
            self.path = '/index.html'

        return super().do_GET()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_local_server(dist_dir: str = None) -> tuple:
    """
    Starts an embedded multithreaded local HTTP server serving the compiled frontend on an ephemeral port.

    Args:
        dist_dir (str, optional): Target directory to serve. Defaults to dist folder.

    Returns:
        tuple[ThreadedTCPServer, int]: The active server instance and its bound TCP port.
    """
    target_dir = dist_dir or get_dist_dir()
    server = ThreadedTCPServer(('127.0.0.1', 0), lambda *args, **kwargs: SPAHTTPRequestHandler(*args, directory=target_dir, **kwargs))
    port = server.server_address[1]
    import threading
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port
