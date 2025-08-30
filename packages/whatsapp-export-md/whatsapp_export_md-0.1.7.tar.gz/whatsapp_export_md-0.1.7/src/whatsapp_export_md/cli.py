#!/usr/bin/env python3
"""
whatsapp-export-md: Convert an exported WhatsApp chat .txt (Android/iOS) into Markdown or HTML.

- Parses Android/iOS formats, multi-line messages, system lines
- Markdown or HTML output
- Media linking (relative) or Base64 embedding via --embed (+ size cap)
- Recognizes <attached: FILENAME> and bare filenames
- Robust filename matching (case/spacing/brackets-insensitive)
- Correct MIME for .opus, .m4a, .pdf
- Prints a summary for unresolved media tokens
"""

import argparse, re, os, json, html, pathlib, base64, mimetypes, sys
from dateutil import tz
from dateutil.parser import parse as dtparse
from urllib.parse import quote

# ---------------- Parsing ----------------

LINE_PATTERNS = [
    r'^\[(?P<ts>.+?)\]\s(?P<name>[^:]+?):\s(?P<msg>.*)$',  # iOS
    r'^(?P<ts>\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?:\s?[AP]M)?)\s-\s(?P<name>[^:]+?):\s(?P<msg>.*)$',  # Android
    r'^(?P<ts>\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?:\s?[AP]M)?)\s-\s(?P<msg>.*)$',  # system w/o name
]
COMPILED = [re.compile(p) for p in LINE_PATTERNS]

SYSTEM_HINTS = (
    "Messages to this chat are now", "added", "left", "changed", "created group",
    "security code", "end-to-end encrypted", "missed voice call", "video call",
)

def parse_chat(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        lines = f.read().splitlines()
    messages, cur = [], None
    def flush():
        nonlocal cur
        if cur:
            cur["msg"] = cur["msg"].rstrip("\n")
            messages.append(cur); cur = None
    for raw in lines:
        line = raw.rstrip("\n")
        matched = None
        for rx in COMPILED:
            m = rx.match(line)
            if m:
                matched = m; break
        if matched:
            flush()
            gd = matched.groupdict()
            ts_raw = gd.get("ts"); name = gd.get("name"); msg = gd.get("msg", "")
            if name is None: name = ""
            cur = {"ts_raw": ts_raw, "name": name.strip(), "msg": msg + "\n"}
        else:
            if cur is None:
                cur = {"ts_raw": None, "name": "", "msg": line + "\n"}
            else:
                cur["msg"] += line + "\n"
    flush()
    return messages

def normalize_times(messages, tz_name):
    to_tz = tz.gettz(tz_name) if tz_name else None
    for m in messages:
        ts_raw = m.get("ts_raw"); dt = None
        if ts_raw:
            try:
                dt = dtparse(ts_raw, dayfirst=True, fuzzy=True)
                if to_tz:
                    dt = dt.replace(tzinfo=to_tz) if dt.tzinfo is None else dt.astimezone(to_tz)
            except Exception:
                dt = None
        m["ts"] = dt
        m["is_system"] = (not m["name"]) or any(h.lower() in m["msg"].lower() for h in SYSTEM_HINTS)
    return messages

def by_day_key(dt):
    if not dt: return "Unknown Date"
    return dt.strftime("%Y-%m-%d (%A)")

# ---------------- Markdown ----------------

def escape_md(text):
    return text.replace("_", r"\_").replace("*", r"\*").replace("|", r"\|")

FILENAME_RE = re.compile(
    r'(?P<attached><\s*attached\s*:\s*(?P<fname1>[^>]+)>)|'
    r'(?P<bare>(?P<fname2>[\w\-\s\(\)\[\]@!~&\',]+\.(?:jpg|jpeg|png|gif|webp|bmp|svg|mp4|m4v|mov|webm|ogv|mp3|m4a|aac|opus|ogg|wav|flac|pdf)))',
    flags=re.I
)

def link_media_in_md(msg, media_dir):
    if not media_dir:
        return msg
    def repl(m):
        fname = (m.group("fname1") or m.group("fname2") or "").strip()
        if not fname: return m.group(0)
        candidate = find_media_candidate(media_dir, fname)
        if candidate:
            rel = os.path.relpath(candidate, start=os.getcwd())
            rel = "/".join(pathlib.Path(rel).parts)
            return f"[{fname}]({rel})"
        return m.group(0)
    return FILENAME_RE.sub(repl, msg)

def render_markdown(messages, title, media_dir):
    out = [f"# {escape_md(title)}\n"]
    first = next((m["ts"] for m in messages if m["ts"]), None)
    last  = next((m["ts"] for m in reversed(messages) if m["ts"]), None)
    if first and last: out.append(f"_Export range_: {first:%Y-%m-%d} → {last:%Y-%m-%d}\n")
    day_groups = {}
    for m in messages: day_groups.setdefault(by_day_key(m["ts"]), []).append(m)
    for day in sorted(day_groups.keys()):
        out.append(f"\n## {escape_md(day)}\n")
        for m in day_groups[day]:
            time_s = m["ts"].strftime("%H:%M") if m["ts"] else "??:??"
            name = m["name"] or "_system_"
            msg = link_media_in_md(m["msg"].rstrip("\n"), media_dir)
            out.append(f"- `{time_s}` **{escape_md(name)}**: {msg}")
    return "\n".join(out) + "\n"

# ---------------- HTML + media ----------------

MEDIA_EXTS = {
    "img": (".jpg",".jpeg",".png",".gif",".webp",".bmp",".svg"),
    "aud": (".mp3",".m4a",".aac",".opus",".ogg",".wav",".flac"),
    "vid": (".mp4",".m4v",".mov",".webm",".ogv"),
    "doc": (".pdf",),
}

EXTRA_MIME = {
    ".opus": "audio/ogg",
    ".m4a":  "audio/mp4",
    ".oga":  "audio/ogg",
    ".ogv":  "video/ogg",
    ".webm": "video/webm",
    ".pdf":  "application/pdf",
}

def guess_mime(path_abs):
    ext = pathlib.Path(path_abs).suffix.lower()
    if ext in EXTRA_MIME: return EXTRA_MIME[ext]
    mt, _ = mimetypes.guess_type(path_abs)
    if mt: return mt
    if ext in MEDIA_EXTS["img"]: return "image/jpeg"
    if ext in MEDIA_EXTS["aud"]: return "audio/mpeg"
    if ext in MEDIA_EXTS["vid"]: return "video/mp4"
    if ext in MEDIA_EXTS["doc"]: return "application/pdf"
    return "application/octet-stream"

def url_for_relpath(src_path, out_html_path):
    rel = os.path.relpath(src_path, start=os.path.dirname(out_html_path))
    parts = [quote(p) for p in pathlib.Path(rel).parts]
    return "/".join(parts)

def data_uri_for_file(path_abs, max_bytes=None):
    try:
        size = os.path.getsize(path_abs)
        if max_bytes is not None and size > max_bytes:
            return None
        with open(path_abs, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:{guess_mime(path_abs)};base64,{b64}"
    except Exception:
        return None

def media_tag(path_abs, out_html_path, embed=False, embed_max_bytes=None):
    ext = pathlib.Path(path_abs).suffix.lower()
    src = data_uri_for_file(path_abs, embed_max_bytes) if embed else None
    if not src: src = url_for_relpath(path_abs, out_html_path)
    if ext in MEDIA_EXTS["img"]:
        return f'<img src="{src}" alt="{html.escape(os.path.basename(path_abs))}" loading="lazy" style="max-width:100%;height:auto;">'
    if ext in MEDIA_EXTS["aud"]:
        return f'<audio controls src="{src}" style="width:100%"></audio>'
    if ext in MEDIA_EXTS["vid"]:
        return f'<video controls src="{src}" style="max-width:100%;height:auto"></video>'
    if ext in MEDIA_EXTS["doc"]:
        return f'<embed src="{src}" type="application/pdf" style="width:100%;height:80vh" />'
    return f'<a href="{src}">{html.escape(os.path.basename(path_abs))}</a>'

# --- smarter filename resolution ---

def _canon(s: str) -> str:
    s = s.lower()
    s = s.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    s = re.sub(r"[^a-z0-9\.\s_\-]", "", s)
    s = re.sub(r"[\s_\-]+", "", s)
    return s

def find_media_candidate(media_dir, fname):
    abs1 = os.path.join(media_dir, fname)
    if os.path.isfile(abs1):
        return abs1
    target_lower = fname.lower()
    try:
        for entry in os.listdir(media_dir):
            if entry.lower() == target_lower and os.path.isfile(os.path.join(media_dir, entry)):
                return os.path.join(media_dir, entry)
    except Exception:
        pass
    canon_target = _canon(fname)
    ext_target = pathlib.Path(fname).suffix.lower()
    best = None
    try:
        for entry in os.listdir(media_dir):
            p = os.path.join(media_dir, entry)
            if not os.path.isfile(p): continue
            if pathlib.Path(entry).suffix.lower() != ext_target:
                continue
            ce = _canon(entry)
            if ce == canon_target:
                return p
            if ce.startswith(canon_target) or canon_target in ce:
                best = p if best is None else best
    except Exception:
        pass
    return best

def replace_media_tokens(text, media_dir, out_html_path, embed=False, embed_max_bytes=None, miss_log=None):
    pieces = []
    last = 0
    for m in FILENAME_RE.finditer(text):
        pieces.append(html.escape(text[last:m.start()]))
        fname = (m.group("fname1") or m.group("fname2") or "").strip()
        if not fname:
            pieces.append(html.escape(m.group(0)))
        else:
            cand = find_media_candidate(media_dir, fname) if media_dir else None
            if cand:
                pieces.append(media_tag(cand, out_html_path, embed=embed, embed_max_bytes=embed_max_bytes))
            else:
                if miss_log is not None: miss_log.add(fname)
                pieces.append(html.escape(m.group(0)))
        last = m.end()
    pieces.append(html.escape(text[last:]))
    html_out = "".join(pieces)
    html_out = re.sub(r'(?P<u>https?://\S+)', r'<a href="\g<u>">\g<u></a>', html_out)
    return html_out

def render_html(messages, title, media_dir, out_html_path, embed=False, embed_max_bytes=None, miss_log=None):
    def esc(x): return html.escape(x)
    css = """
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.5}
      h1{margin:0 0 1rem}
      .day{margin-top:2rem}
      .msg{display:grid;grid-template-columns:4.5rem 12rem 1fr;gap:.75rem;padding:.4rem .2rem;border-bottom:1px solid #eee}
      .time{color:#666;font-variant-numeric:tabular-nums}
      .name{font-weight:600}
      .system .name{color:#a00}
      .system .text{color:#a00}
      .text pre{white-space:normal;margin:0}
      a{word-break:break-all}
    </style>
    """
    out = [f"<!doctype html><meta charset='utf-8'><title>{esc(title)}</title>{css}<h1>{esc(title)}</h1>"]
    first = next((m["ts"] for m in messages if m["ts"]), None)
    last  = next((m["ts"] for m in reversed(messages) if m["ts"]), None)
    if first and last: out.append(f"<p><em>Export range</em>: {esc(first.strftime('%Y-%m-%d'))} → {esc(last.strftime('%Y-%m-%d'))}</p>")
    day_groups = {}
    for m in messages: day_groups.setdefault(by_day_key(m["ts"]), []).append(m)
    for day in sorted(day_groups.keys()):
        out.append(f"<div class='day'><h2>{esc(day)}</h2>")
        for m in day_groups[day]:
            time_s = m["ts"].strftime("%H:%M") if m["ts"] else "??:??"
            name = m["name"] or "system"
            msg_html = replace_media_tokens(
                m["msg"].rstrip('\n'),
                media_dir,
                out_html_path,
                embed=embed,
                embed_max_bytes=embed_max_bytes,
                miss_log=miss_log
            )
            out.append(
                f"<div class='msg {'system' if m['is_system'] else ''}'>"
                f"<div class='time'>{esc(time_s)}</div>"
                f"<div class='name'>{esc(name)}</div>"
                f"<div class='text'><pre>{msg_html}</pre></div></div>"
            )
        out.append("</div>")
    return "".join(out)

# ---------------- CLI ----------------

def main():
    import sys
    mimetypes.init()
    mimetypes.add_type("audio/ogg", ".opus")
    mimetypes.add_type("application/pdf", ".pdf")

    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--media-dir", default="", help="Path to exported media folder (optional)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--format", choices=["md","html"], default="md")
    ap.add_argument("--split", choices=["daily"], default="daily")
    ap.add_argument("--tz", default="Asia/Kolkata")
    ap.add_argument("--title", default="WhatsApp Chat Export")
    ap.add_argument("--json", default="")
    ap.add_argument("--embed", action="store_true", help="Inline media as Base64 data URIs (HTML only)")
    ap.add_argument("--embed-max-mb", type=float, default=8.0, help="Max per-file embed size (MB); larger files are linked.")
    args = ap.parse_args()

    messages = parse_chat(args.input)
    messages = normalize_times(messages, args.tz)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as jf:
            json.dump(messages, jf, ensure_ascii=False, indent=2, default=str)

    media_dir = args.media_dir if args.media_dir and os.path.isdir(args.media_dir) else ""

    if args.format == "md":
        doc = render_markdown(messages, args.title, media_dir)
        with open(args.out, "w", encoding="utf-8") as f: f.write(doc)
    else:
        embed_max_bytes = int(args.embed_max_mb * 1024 * 1024) if args.embed else None
        miss_log = set()
        doc = render_html(
            messages, args.title, media_dir, args.out,
            embed=args.embed, embed_max_bytes=embed_max_bytes, miss_log=miss_log
        )
        with open(args.out, "w", encoding="utf-8") as f: f.write(doc)
        if miss_log:
            print("\n[Note] Could not resolve these media tokens (check --media-dir and filenames):", file=sys.stderr)
            for x in sorted(miss_log):
                print("  -", x, file=sys.stderr)

if __name__ == "__main__":
    main()
