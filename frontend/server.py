import http.server
import socketserver

PORT = 8080
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🌐 Фронтенд запущен на http://localhost:{PORT}")
    print("Нажми Ctrl+C для остановки")
    httpd.serve_forever()
