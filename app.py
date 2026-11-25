"""Tiny web server: every request to /countdown.gif returns a fresh, accurate GIF.

Optional colors via query string, e.g. /countdown.gif?bg=000000&fg=ff2b2b&label=bbbbbb
Health check: /ping returns "ok" instantly.
"""
import re

from flask import Flask, Response, request

from countdown import render_gif

app = Flask(__name__)
HEX = re.compile(r"^[0-9a-fA-F]{6}$")


def _color(name, default):
    v = request.args.get(name, "")
    return "#" + v if HEX.match(v) else default


@app.route("/ping")
def ping():
    return "ok"


@app.route("/")
@app.route("/countdown.gif")
def countdown():
    gif = render_gif(bg=_color("bg", "#000000"), fg=_color("fg", "#ff2b2b"),
                     label=_color("label", "#bbbbbb"))
    return Response(gif, mimetype="image/gif", headers={
        # no caching, so each email open / page load gets the current time
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "Content-Length": str(len(gif)),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
