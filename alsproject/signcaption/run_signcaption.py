#!/usr/bin/env python3
"""Run SignCaption on your laptop.

Put this file in the same folder as asl-captions.html, then run:
    python3 run_signcaption.py

The first run downloads the hand-tracking files (~15 MB) into a "vendor" folder.
After that it works with no internet. It then opens the page in your browser.
"""
import http.server, os, socketserver, subprocess, sys, threading, urllib.request, webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")
CDN = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14"
FILES = {
    "vision_bundle.mjs": CDN + "/vision_bundle.mjs",
    "wasm/vision_wasm_internal.js": CDN + "/wasm/vision_wasm_internal.js",
    "wasm/vision_wasm_internal.wasm": CDN + "/wasm/vision_wasm_internal.wasm",
    "wasm/vision_wasm_nosimd_internal.js": CDN + "/wasm/vision_wasm_nosimd_internal.js",
    "wasm/vision_wasm_nosimd_internal.wasm": CDN + "/wasm/vision_wasm_nosimd_internal.wasm",
    "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
}
PORT = 8000


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    try:
        with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
            f.write(r.read())
    except Exception:
        # Python on some Macs lacks SSL certificates; curl always has them.
        subprocess.run(["curl", "-fsSL", url, "-o", tmp], check=True)
    os.replace(tmp, dest)


def main():
    page = os.path.join(HERE, "asl-captions.html")
    if not os.path.exists(page):
        sys.exit("Put this script in the same folder as asl-captions.html, then run it again.")

    for name, url in FILES.items():
        dest = os.path.join(VENDOR, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        print(f"Downloading {name} ...")
        try:
            download(url, dest)
        except Exception as e:
            sys.exit(f"\nCouldn't download {name}: {e}\n"
                     "Your network may block this site. Try a different Wi-Fi or a phone hotspot,\n"
                     "just for this first run. After that no internet is needed.")
    print("Hand-tracking files ready.")

    os.chdir(HERE)
    handler = http.server.SimpleHTTPRequestHandler
    handler.extensions_map.update({".mjs": "text/javascript", ".wasm": "application/wasm"})
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}/asl-captions.html"
        print(f"\nSignCaption is running at {url}")
        print("Leave this window open while you use it. Press Ctrl+C to stop.")
        threading.Timer(1, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
