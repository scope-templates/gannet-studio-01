# Gannet Studio

Gannet Studio, a small web app that turns a short brief into a poster. A user types the brief, clicks Generate, and the page comes back with the finished image. Generation runs the studio's image model inside the request handler, and a full generation takes 10 to 40 minutes depending on the brief.

## Run locally

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
STUDIO_STEP_SECONDS=0.01 flask --app app run    # a full generation finishes in seconds
```

Open http://127.0.0.1:5000, type a brief and click Generate. Without `STUDIO_STEP_SECONDS` the model paces itself the way it does in production, one pass per second, and the request takes 10 to 40 minutes.

## How a generation works

| Piece             | What it does                                                                                                   |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| `app.py`          | the web app: `GET /` the form, `POST /generate` runs the model and returns the poster page, `GET /posters/<id>.png` serves a poster, `GET /health` |
| `studio/model.py` | `generate(brief)`: starts from noise seeded by the brief and refines it over `steps_for(brief)` passes (blur, contrast, palette, typesetting), one pass per `STUDIO_STEP_SECONDS` |
| `studio/store.py` | writes finished posters under `STUDIO_OUT_DIR` and lists them for the front page                                |

The number of passes grows with the brief: a one-line brief takes about 600 passes, a paragraph about 2,400. At the production pace of one pass per second that is 10 to 40 minutes, during which the process serving the request does nothing else.

## Environment

| Variable              | Default                | Purpose                                                   |
| --------------------- | ---------------------- | --------------------------------------------------------- |
| `STUDIO_STEPS`        | derived from the brief | passes per generation; set it to force a fixed length     |
| `STUDIO_STEP_SECONDS` | `1.0`                  | pacing per pass                                           |
| `STUDIO_OUT_DIR`      | `./posters`            | where finished posters and their briefs are written       |
| `PORT`                | `5000`                 | the port `gunicorn app:app` binds when run that way       |
