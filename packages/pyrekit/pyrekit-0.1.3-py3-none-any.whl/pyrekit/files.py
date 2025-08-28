# File definitions

INDEX_TSX = """import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';

const container = document.getElementById('root');
const root = createRoot(container!);
root.render(<App />);
"""

APP_TSX = """import React from 'react';

export function App() {
    return <h1>Hello from PyReact 👋</h1>;
}
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>APP_NAME</title>
    <link href="./output.css" rel="stylesheet">
</head>
<body>
    <div onload="pollServerAndReload()" id="root"></div>
    <script id="bundle" src="bundle.js"></script>
    <script id="DEV_RELOAD">
        async function shouldReload() {
          const res = await fetch("/dev/reload");

          const data = await res.json();
          const reload = data.reload;

          if (reload) {
            window.location.reload()
          }
        }

        setInterval(shouldReload, 500)
    </script>
</body>
</html>"""

TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
export default {
   content: ["./src/**/*.{html,js}"],
   theme: {
     extend:{},
   },
   plugins: [],
}"""

INPUT_CSS = """@import "tailwindcss";"""

MAIN_PY = """from flask import jsonify
from pyrekit.server import Server, ServerProcess, pack_app
import webview

# don't rename this class
class AppServer(Server):
    def index(self):
        return pack_app(self.DEV)

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5000
    
    app_server = AppServer(host=HOST, port=PORT)
    server_proc = ServerProcess(server=app_server)
    server_proc.start()
    
    webview.create_window("AppServer", f"http://{HOST}:{PORT}/")
    webview.start()

    server_proc.close()"""

# Support functions

def create_files(AppName: str = "PyReact"):
    """
    Creates base files for the app
    """

    with open("src/index.tsx", "w") as fd:
        fd.write(INDEX_TSX)

    with open("src/App.tsx", "w") as fd:
        fd.write(APP_TSX)

    with open("build/index.html", "w") as fd:
        fd.write(INDEX_HTML.replace("APP_NAME", AppName))

    with open("tailwind.config.js", "w") as fd:
        fd.write(TAILWIND_CONFIG)

    with open("src/input.css", "w") as fd:
        fd.write(INPUT_CSS)

    with open("main.py", "w") as fd:
        fd.write(MAIN_PY)


def read_file(path: str) -> str:
    """
        Read file and return content, if not exists, print error and returns empty string
    """

    try:
        with open(path, "r") as fd:
            return fd.read()
    except FileNotFoundError:
        print("File not Found! ", path)
        return ""
