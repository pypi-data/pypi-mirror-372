"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import json
import requests
from flask import Blueprint, render_template, jsonify, request, current_app, Response
from flask import stream_with_context


bp = Blueprint("studio", __name__)


@bp.get("/")
def studio_home():
    return render_template("studio/index.html")


# ---- Config management ----

def _qalita_home():
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    try:
        return cfg.qalita_home  # type: ignore[attr-defined]
    except Exception:
        return os.path.expanduser("~/.qalita")


def _studio_config_path() -> str:
    root = _qalita_home()
    try:
        os.makedirs(root, exist_ok=True)
    except Exception:
        pass
    return os.path.join(root, ".studio")


@bp.get("/status")
def studio_status():
    p = _studio_config_path()
    exists = os.path.isfile(p)
    data: dict | None = None
    if exists:
        try:
            with open(p, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if raw:
                    data = json.loads(raw)
        except Exception:
            data = None
    return jsonify({"configured": exists, "config": data})


@bp.post("/config")
def studio_save_config():
    payload = request.get_json(silent=True) or {}
    p = _studio_config_path()
    try:
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=2))
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc)}), 500


@bp.get("/check-ollama")
def check_ollama():
    url = "http://127.0.0.1:11434/api/tags"
    try:
        r = requests.get(url, timeout=2)
        ok = r.status_code == 200
        return jsonify({"ok": ok})
    except Exception:
        return jsonify({"ok": False})


@bp.get("/check-backend")
def check_backend():
    """Proxy healthcheck against the remote backend URL from current context.
    Avoids CORS issues in the browser and standardizes the response shape.
    """
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    backend_url: str | None = None
    try:
        backend_url = getattr(cfg, "url", None)
    except Exception:
        backend_url = None
    # Fallback: read selected env pointer and parse URL from env file
    try:
        if not backend_url:
            home = _qalita_home()
            pointer = os.path.join(home, ".current_env")
            if os.path.isfile(pointer):
                with open(pointer, "r", encoding="utf-8") as f:
                    env_path = (f.read() or "").strip()
                if env_path and os.path.isfile(env_path):
                    with open(env_path, "r", encoding="utf-8") as ef:
                        for raw in ef.readlines():
                            line = (raw or "").strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = (k or "").strip().upper()
                            v = (v or "").strip().strip('"').strip("'")
                            if k in ("QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"):
                                backend_url = v
                                break
    except Exception:
        pass
    if not backend_url:
        return jsonify({"ok": False, "status": None, "url": None}), 200
    try:
        url = str(backend_url).rstrip("/") + "/api/v1/healthcheck"
    except Exception:
        url = str(backend_url) + "/api/v1/healthcheck"
    try:
        r = requests.get(url, timeout=3)
        ok = 200 <= r.status_code < 300
        return jsonify({"ok": ok, "status": r.status_code, "url": str(backend_url).rstrip("/")})
    except Exception:
        return jsonify({"ok": False, "status": None, "url": str(backend_url).rstrip("/")}), 200


@bp.post("/chat")
def studio_chat():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    # Prefer model from request; else fall back to saved Studio config; else default
    model = (data.get("model") or "").strip()
    if not model:
        try:
            cfg_path = _studio_config_path()
            if os.path.isfile(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    if raw:
                        cfg = json.loads(raw)
                        model = (cfg.get("model") or "").strip()
        except Exception:
            # Ignore config read errors and continue to use default below
            pass
    if not model:
        model = "gpt-oss:20b"
    if not prompt:
        return jsonify({"ok": False, "message": "Missing prompt"}), 400
    # Streaming toggle via query or body
    stream_flag_raw = (request.args.get("stream") or data.get("stream") or "").strip().lower()
    stream_enabled = stream_flag_raw in ("1", "true", "yes", "on")
    if stream_enabled:
        def generate_stream():
            req = None
            try:
                req = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={"model": model, "prompt": prompt, "stream": True},
                    stream=True,
                    timeout=300,
                )
                if req.status_code != 200:
                    try:
                        body = req.json()
                        msg = (
                            (body.get("error") if isinstance(body, dict) else None)
                            or (body.get("message") if isinstance(body, dict) else None)
                            or str(body)
                        )
                    except Exception:
                        msg = f"Ollama error: {req.status_code}"
                    yield f"[ERROR] {msg}"
                    return
                for line in req.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if obj.get("response"):
                            yield obj["response"]
                        if obj.get("done"):
                            break
                    except Exception:
                        # Fallback: passthrough raw line
                        yield line
            except GeneratorExit:
                # Client disconnected/aborted
                if req is not None:
                    try:
                        req.close()
                    except Exception:
                        pass
                raise
            except Exception as exc:
                yield f"[ERROR] Failed to reach Ollama: {exc}"
            finally:
                if req is not None:
                    try:
                        req.close()
                    except Exception:
                        pass

        return Response(stream_with_context(generate_stream()), mimetype="text/plain; charset=utf-8")
    try:
        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        if r.status_code == 200:
            out = r.json().get("response", "")
            return jsonify({"ok": True, "response": out})
        if r.status_code == 404:
            return (
                jsonify(
                    {
                        "ok": False,
                        "message": f"Model not found in Ollama: '{model}'. Install it with 'ollama pull {model}' or update your Studio model.",
                    }
                ),
                500,
            )
        # Try to surface error body if available
        try:
            err_body = r.json()
        except Exception:
            err_body = {"detail": r.text[:200]}
        return jsonify({"ok": False, "message": f"Ollama error: {r.status_code}", "error": err_body}), 500
    except Exception as exc:
        return jsonify({"ok": False, "message": f"Failed to reach Ollama: {exc}"}), 502


