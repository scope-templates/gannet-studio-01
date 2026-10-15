import uuid

from flask import Flask, abort, render_template, request, send_from_directory

from studio.model import generate as generate_poster, steps_for
from studio.store import OUT_DIR, list_posters, save

app = Flask(__name__)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def index():
    return render_template("index.html", posters=list_posters())


@app.post("/generate")
def generate():
    brief = request.form.get("brief", "").strip()
    if not brief:
        abort(400, "a brief is required")
    poster_id = uuid.uuid4().hex[:12]
    image = generate_poster(brief)
    save(poster_id, brief, image)
    return render_template("result.html", poster_id=poster_id, brief=brief, steps=steps_for(brief))


@app.get("/posters/<poster_id>.png")
def poster(poster_id):
    return send_from_directory(OUT_DIR, f"{poster_id}.png")
