import requests
from typing import List


def get_country(ip=requests.get("https://ipinfo.io/json", timeout=10).json()["ip"]):

    url = f"https://ipapi.co/{ip}/json/"
    response = requests.get(url).json()
    return response.get("country_name", "Unknown")


def _run_server(html_path, port, auto_open):
    import http.server
    import socketserver
    import webbrowser

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/":
                try:
                    with open(html_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_error(404, f"File not found: {html_path}")
            else:
                self.send_error(404, "Page not found")

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Serving {html_path} at http://127.0.0.1:{port}")
        if auto_open:
            webbrowser.open(f"http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def serve_html(html_path, port, background=True, auto_open=False):
    from multiprocessing import Process
    import os

    html_path = os.path.abspath(html_path)

    if background:
        process = Process(target=_run_server, args=(html_path, port, auto_open))
        process.start()
        return process
    else:
        _run_server(html_path, port, auto_open)


def fetch_url(
    main_url: str, backup_urls: List[str] = [], retries: int = 3, timeout: int = 5
):
    all_urls = [main_url] + backup_urls

    for idx, url in enumerate(all_urls):
        for attempt in range(retries + 1):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == retries:
                    if url != all_urls[-1]:
                        pass
                    break
    raise TimeoutError


del List
