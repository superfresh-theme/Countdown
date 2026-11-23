# Live countdown GIF

Ends **10:00 AM Pacific (PST), November 27, 2026**. To change it, edit `END` in `countdown.py`.

Each time `/countdown.gif` is opened, the server draws a new 60-second GIF from the current time. That keeps it accurate in emails and on web pages.

## Deploy (Render.com example, free tier works)
1. Put this folder in a GitHub repo (keep `fonts/digital-7.ttf` in it).
2. On Render: **New → Web Service** → pick the repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
3. In the service's **Settings → Custom Domains**, add your subdomain, e.g. `countdown.yourstore.com`.
4. At your DNS provider, add the **CNAME** record Render shows you
   (`countdown` → `your-service.onrender.com`).

Railway, Fly.io or any server that runs Python works the same way.

## Use it
```html
<img src="https://countdown.yourstore.com/countdown.gif" width="600" height="170" alt="Sale ends Nov 27">
```
To change colors, add hex values without the `#`:
`/countdown.gif?bg=000000&fg=ff2b2b&label=bbbbbb`

## Test locally
```
pip install -r requirements.txt
python app.py        # open http://localhost:8080/countdown.gif
```
Note: on Render's free tier the service sleeps when idle, so the first open after a quiet period can take a few seconds. A paid instance stays awake.
