# src/df_gallery/cli.py
from __future__ import annotations
import argparse, csv, json, os, sys, time, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, List

HTML_TEMPLATE = """<!doctype html>
<html lang="en" class="{meta_class}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>
  :root {{
    --tile: {tile_px}px;
    --gap: 10px;
    --bg: #0e0f12;
    --fg: #eaeaea;
    --muted: #9aa0a6;
    --card: #171922;
    --accent: #3ea6ff;
    --radius: 12px;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; margin: 0; background: var(--bg); color: var(--fg); font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, sans-serif; }}
  header {{
    position: sticky; top: 0; z-index: 10;
    background: linear-gradient(180deg, #0e0f12 85%, #0e0f12cc 100%);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid #22242d;
  }}
  .wrap {{ max-width: 1400px; margin: 0 auto; padding: 12px 16px; }}
  .bar {{ display: grid; grid-template-columns: 1fr auto auto auto auto auto; grid-gap: 12px; align-items: center; }}
  .bar2 {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-top: 8px; }}
  h1 {{ font-size: 18px; margin: 0; font-weight: 650; letter-spacing: 0.2px; }}
  button, input[type="range"], input[type="text"], select {{
    appearance: none;
    background: var(--card);
    color: var(--fg);
    border: 1px solid #2a2d39;
    border-radius: 10px;
    padding: 8px 12px;
    font-weight: 600;
  }}
  button {{ cursor: pointer; }}
  button:hover {{ border-color: var(--accent); }}
  input[type="text"] {{ width: 100%; font-weight: 500; }}
  .hint {{ color: var(--muted); font-size: 12px; }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--tile), 1fr));
    gap: var(--gap);
    padding: 16px;
    max-width: 1600px; margin: 0 auto;
  }}
  .tile {{
    background: var(--card);
    border: 1px solid #1f2230;
    border-radius: var(--radius);
    overflow: hidden;
    position: relative;
    display: flex; flex-direction: column;
  }}
  .imgwrap {{
    aspect-ratio: 1 / 1;
    background: #0b0c10;
    border-bottom: 1px solid #262b3a;
    display:flex; align-items:center; justify-content:center;
  }}
  .tile a.__imglink {{ position: absolute; inset: 0; }}
  .tile img {{
    width: 100%; height: 100%;
    object-fit: cover; display: block;
    transition: transform .2s ease;
    background: #fff;
  }}
  .tile:hover img {{ transform: scale(1.02); }}
  .meta {{
    padding: 8px 10px; font-size: 12px; line-height: 1.35;
    display: grid; grid-template-columns: 1fr; gap: 4px;
  }}
  .kv {{ display:flex; gap: 6px; }}
  .k {{ color: var(--muted); white-space: nowrap; }}
  .v {{ overflow-wrap:anywhere; }}
  html.meta-hidden .meta {{ display: none; }}

  .counter {{ font-size: 13px; color: var(--muted); }}
  .err {{ color: #ff7a7a; font-size: 12px; margin-left: 8px; }}

  .pager {{ display:flex; gap:8px; align-items:center; font-size: 13px; }}
  .pager .nums {{ opacity: .8; }}
  .footer-space {{ height: 24px; }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="bar">
      <h1>{title}</h1>
      <span class="counter" id="counter">0 / 0</span>
      <label class="hint">Tile size</label>
      <input id="size" type="range" min="120" max="360" value="{tile_px}" />
      <button id="toggle-meta">{toggle_text}</button>
      <div class="pager">
        <button id="first">⏮</button>
        <button id="prev">◀</button>
        <span class="nums"><span id="page-cur">1</span>/<span id="page-total">1</span></span>
        <button id="next">▶</button>
        <button id="last">⏭</button>
        <label class="hint">Page size</label>
        <select id="page-size">
          <option>50</option>
          <option>100</option>
          <option selected>{page_size}</option>
          <option>500</option>
          <option>1000</option>
        </select>
      </div>
    </div>
    <div class="bar2">
      <input id="filter" type="text" placeholder="pandas-style filter, e.g. extension in ['.png','.jpg'] and unique_colors < 500" />
      <button id="apply">Apply</button>
      <button id="clear">Clear</button>
      <button id="shuffle">Shuffle</button>
      <select id="examples">
        <option value="">Examples…</option>
        <option value="extension in ['.png', '.jpg', '.jpeg']">extension in ['.png', '.jpg', '.jpeg']</option>
        <option value="unique_colors < 500">unique_colors < 500</option>
        <option value="uses_transparency == True">uses_transparency == True</option>
        <option value="filename.str.icontains('icon')">filename.str.icontains('icon')</option>
        <option value="(extension == '.gif') and unique_colors < 256">extension == '.gif' and unique_colors < 256</option>
        <option value="(!uses_transparency) and (unique_colors > 500)">(!uses_transparency) and (unique_colors > 500)</option>
      </select>
      <span class="err" id="err"></span>
    </div>
  </div>
</header>

<main>
  <div id="grid" class="grid"></div>
  <div class="footer-space"></div>
</main>

<script>
  const DATA = {rows_json};
  const DEFAULT_PAGE_SIZE = {page_size};
  const CHUNK_SIZE = {chunk_size};
  const SHOW_COLS = {show_cols_json};

  const grid = document.getElementById('grid');
  const counter = document.getElementById('counter');
  const err = document.getElementById('err');
  const filterInput = document.getElementById('filter');
  const toggleMetaBtn = document.getElementById('toggle-meta');

  const firstBtn = document.getElementById('first');
  const prevBtn = document.getElementById('prev');
  const nextBtn = document.getElementById('next');
  const lastBtn = document.getElementById('last');
  const pageCur = document.getElementById('page-cur');
  const pageTotal = document.getElementById('page-total');
  const pageSizeSel = document.getElementById('page-size');

  let filtered = DATA.slice();
  let order = filtered.map(r => r.src);
  let rendered = 0;

  let pageIndex = 0; // 0-based
  let pageSize = parseInt(pageSizeSel.value || DEFAULT_PAGE_SIZE, 10) || DEFAULT_PAGE_SIZE;

  function contains(s, sub) {{ s = (s ?? '').toString(); return s.indexOf(sub) !== -1; }}
  function icontains(s, sub) {{ s = (s ?? '').toString().toLowerCase(); return s.indexOf((sub ?? '').toString().toLowerCase()) !== -1; }}
  function lower(s) {{ return (s ?? '').toString().toLowerCase(); }}
  function upper(s) {{ return (s ?? '').toString().toUpperCase(); }}
  function list(...a) {{ return a; }}
  function includes(val, arr) {{ return (arr || []).includes(val); }}

  function strAccessor(value) {{
    const s = (value ?? '').toString();
    return {{
      contains: (needle) => contains(s, needle),
      icontains: (needle) => icontains(s, needle),
      lower: () => lower(s),
      upper: () => upper(s),
      len: () => s.length,
    }};
  }}

  function makeScope(row) {{
    return new Proxy({{}}, {{
      has: () => true,
      get: (_, key) => {{
        if (key === 'str') return strAccessor;
        if (key in row) return row[key];
        return undefined;
      }}
    }});
  }}

  function translate(expr) {{
    let e = expr.trim();
    e = e.replace(/\\bis\\s+null\\b/gi, ' == null');
    e = e.replace(/\\bis\\s+not\\s+null\\b/gi, ' != null');
    e = e.replace(/\\band\\b/gi, '&&');
    e = e.replace(/\\bor\\b/gi, '||');
    e = e.replace(/\\bnot\\b/gi, '!');
    e = e.replace(/\\bTrue\\b/g, 'true').replace(/\\bFalse\\b/g, 'false').replace(/\\bNone\\b/g, 'null');
    e = e.replace(/(\\b[\\w\\.]+)\\.str\\.icontains\\(/g, 'str($1).icontains(');
    e = e.replace(/(\\b[\\w\\.]+)\\.str\\.contains\\(/g, 'str($1).contains(');
    e = e.replace(/(\\b[\\w\\.]+)\\.str\\.lower\\(\\)/g, 'str($1).lower()');
    e = e.replace(/(\\b[\\w\\.]+)\\.str\\.upper\\(\\)/g, 'str($1).upper()');
    e = e.replace(/(\\b[\\w\\.]+)\\s+in\\s+(\\[[^\\]]*\\])/gi, 'includes($1, $2)');
    return e;
  }}

  function compileFilter(expr) {{
    const js = translate(expr);
    const fn = new Function('scope', `with (scope) {{ return (${{js}}); }}`);
    return (row) => !!fn(makeScope(row));
  }}

  function bounds() {{
    const total = order.length;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    pageIndex = Math.max(0, Math.min(pageIndex, totalPages - 1));
    const start = pageIndex * pageSize;
    const end = Math.min(start + pageSize, total);
    return {{ total, totalPages, start, end }};
  }}

  function applyFilter(expr) {{
    if (!expr || !expr.trim()) {{
      filtered = DATA.slice();
    }} else {{
      const pred = compileFilter(expr);
      const out = [];
      for (const r of DATA) {{ try {{ if (pred(r)) out.push(r); }} catch (e) {{ throw e; }} }}
      filtered = out;
    }}
    order = filtered.map(r => r.src);
    pageIndex = 0;
    renderAll();
  }}

  function updateCounter() {{
    const b = bounds();
    const visible = b.end - b.start;
    const kept = order.length;
    const removed = DATA.length - kept;
    const pct = kept ? ((kept / DATA.length) * 100).toFixed(1) : '0.0';
    counter.textContent = `${{rendered}} / ${{visible}} • page ${{b.totalPages ? (pageIndex + 1) : 1}}/${{b.totalPages}} • kept ${{kept}} of ${{DATA.length}} (${{pct}}%) • removed ${{removed}}`;
    pageCur.textContent = (b.totalPages ? (pageIndex + 1) : 1);
    pageTotal.textContent = b.totalPages;
    firstBtn.disabled = prevBtn.disabled = (pageIndex <= 0);
    nextBtn.disabled = lastBtn.disabled = (pageIndex >= b.totalPages - 1);
  }}

  function clearGrid() {{
    grid.innerHTML = '';
    rendered = 0;
    updateCounter();
  }}

  function kvRow(k, v) {{
    const div = document.createElement('div');
    div.className = 'kv';
    const kk = document.createElement('span'); kk.className = 'k'; kk.textContent = k + ':';
    const vv = document.createElement('span'); vv.className = 'v'; vv.textContent = (v == null) ? '' : String(v);
    div.append(kk, vv);
    return div;
  }}

  function createTile(row) {{
    const tile = document.createElement('div'); tile.className = 'tile';
    const imgwrap = document.createElement('div'); imgwrap.className = 'imgwrap';
    const img = document.createElement('img'); img.loading = 'lazy'; img.decoding = 'async'; img.src = row.src; img.alt = '';
    imgwrap.appendChild(img); tile.appendChild(imgwrap);

    const meta = document.createElement('div'); meta.className = 'meta';
    const cols = (SHOW_COLS && SHOW_COLS.length) ? SHOW_COLS : Object.keys(row).filter(k => k !== 'src');
    for (const k of cols) {{ if (k !== 'src') meta.appendChild(kvRow(k, row[k])); }}
    tile.appendChild(meta);

    const a = document.createElement('a'); a.href = row.src; a.target = '_blank'; a.rel = 'noopener'; a.className = '__imglink';
    tile.appendChild(a);
    return tile;
  }}

  function renderChunk(start, end) {{
    if (rendered >= end - start) return;
    const upto = Math.min(start + rendered + CHUNK_SIZE, end);
    const frag = document.createDocumentFragment();
    const idx = new Map(filtered.map(r => [r.src, r]));
    for (let i = start + rendered; i < upto; i++) {{
      const row = idx.get(order[i]);
      if (row) frag.appendChild(createTile(row));
    }}
    grid.appendChild(frag);
    rendered = upto - start;
    updateCounter();
    if (start + rendered < end) {{ (window.requestIdleCallback || window.requestAnimationFrame)(() => renderChunk(start, end)); }}
  }}

  function renderAll() {{
    const b = bounds();
    clearGrid(); err.textContent = '';
    renderChunk(b.start, b.end);
    window.scrollTo({{top: 0}});
  }}

  function shuffleInPlace(arr) {{
    for (let i = arr.length - 1; i > 0; i--) {{
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }}
  }}

  document.getElementById('shuffle').addEventListener('click', () => {{ shuffleInPlace(order); pageIndex = 0; renderAll(); }});
  document.getElementById('size').addEventListener('input', (e) => {{ const px = parseInt(e.target.value, 10) || {tile_px}; document.documentElement.style.setProperty('--tile', px + 'px'); }});
  document.getElementById('apply').addEventListener('click', () => {{ try {{ applyFilter(filterInput.value); }} catch (e) {{ err.textContent = e.message; }} }});
  document.getElementById('clear').addEventListener('click', () => {{ filterInput.value = ''; applyFilter(''); }});
  document.getElementById('examples').addEventListener('change', (e) => {{ if (e.target.value) {{ filterInput.value = e.target.value; e.target.selectedIndex = 0; }} }});

  function setMetaHidden(hidden) {{
    document.documentElement.classList.toggle('meta-hidden', hidden);
    toggleMetaBtn.textContent = hidden ? 'Show meta' : 'Hide meta';
  }}
  toggleMetaBtn.addEventListener('click', () => {{
    const hidden = !document.documentElement.classList.contains('meta-hidden'); setMetaHidden(hidden);
  }});

  window.addEventListener('load', () => {{
    setMetaHidden(document.documentElement.classList.contains('meta-hidden'));
    [...pageSizeSel.options].forEach(o => {{ if (parseInt(o.value,10) === DEFAULT_PAGE_SIZE) o.selected = true; }});
    applyFilter('');
  }});
</script>
</body>
</html>
"""

# ---------- helpers (Python) ----------

def _coerce_value(v: str):
    s = (v or "").strip()
    if s == "":
        return None
    lo = s.lower()
    if lo in ("true", "false"):
        return lo == "true"
    if lo in ("none", "null", "nan"):
        return None
    try:
        return int(s)
    except Exception:
        pass
    try:
        return float(s)
    except Exception:
        pass
    return v

def _rel_to(base: Path, target: Path) -> str:
    try:
        return os.path.relpath(target.resolve(), base).replace("\\", "/")
    except Exception:
        return str(target).replace("\\", "/")

def _read_rows(csv_path: Path, path_col: str, img_root: str, out_dir: Path, relative_to_html: bool) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if path_col not in (reader.fieldnames or []):
            raise SystemExit(f"Column '{path_col}' not found. Available: {reader.fieldnames}")
        for r in reader:
            raw = (r.get(path_col) or "").strip()
            if not raw:
                continue
            row = {k: _coerce_value(v if v is not None else "") for k, v in r.items()}
            if raw.startswith(("http://", "https://", "data:")):
                src = raw
            else:
                p = Path(raw)
                if img_root:
                    p = Path(img_root) / p
                src = _rel_to(out_dir, p) if relative_to_html else str(p).replace("\\", "/")
            row["src"] = src
            rows.append(row)
    return rows

def _render_html(*, title: str, rows: List[Dict[str, Any]], chunk_size: int, tile_px: int,
                 show_cols: List[str] | None, collapse_meta: bool, page_size: int) -> str:
    return HTML_TEMPLATE.format(
        title=title,
        rows_json=json.dumps(rows, ensure_ascii=False),
        chunk_size=max(1, int(chunk_size)),
        tile_px=max(80, int(tile_px)),
        show_cols_json=json.dumps(show_cols or []),
        meta_class=("meta-hidden" if collapse_meta else ""),
        toggle_text=("Show meta" if collapse_meta else "Hide meta"),
        page_size=max(1, int(page_size)),
    )

class _NoCacheHandler(SimpleHTTPRequestHandler):
    html_name: str = "index.html"
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()
    def log_message(self, fmt, *args):
        sys.stderr.write("[http] " + fmt % args + "\n")
    def do_GET(self):
        if self.path in ("/", ""):
            self.path = "/" + self.html_name
        return super().do_GET()

def _serve_file(html_path: Path, host: str, port: int, open_browser: bool):
    root = html_path.parent.resolve()
    handler_cls = _NoCacheHandler
    handler_cls.directory = str(root)
    handler_cls.html_name = html_path.name  # type: ignore[attr-defined]
    httpd = ThreadingHTTPServer((host, port), handler_cls)
    url = f"http://{host}:{port}/{html_path.name}"
    print(f"Serving {html_path} at {url} (Ctrl+C to stop)")
    # only try to open if there looks to be a display (avoid headless SSH spam)
    if open_browser and os.environ.get("DISPLAY") and not os.environ.get("SSH_CONNECTION"):
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

# ---------- subcommands ----------

def cmd_build(args) -> int:
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def build_once() -> List[Dict[str, Any]]:
        rows = _read_rows(
            csv_path=Path(args.csv),
            path_col=args.path_col,
            img_root=args.img_root,
            out_dir=out_path.parent,
            relative_to_html=args.relative_to_html,
        )
        if not rows:
            raise SystemExit("No image paths found.")
        html = _render_html(
            title=args.title,
            rows=rows,
            chunk_size=args.chunk,
            tile_px=args.tile,
            show_cols=args.show_cols,
            collapse_meta=args.collapse_meta,
            page_size=args.page_size,
        )
        out_path.write_text(html, encoding="utf-8")
        print(f"Wrote {out_path} with {len(rows)} items. Columns: {list(rows[0].keys())}")
        return rows

    # initial build
    build_once()

    # serve/watch if requested
    if not (args.serve or args.watch):
        return 0

    if args.watch:
        last_mtime = Path(args.csv).stat().st_mtime
        import threading
        def watch_loop():
            nonlocal last_mtime
            print(f"Watching {args.csv} for changes…")
            while True:
                try:
                    m = Path(args.csv).stat().st_mtime
                    if m != last_mtime:
                        last_mtime = m
                        print("Change detected, rebuilding…")
                        try:
                            build_once()
                        except Exception as e:
                            print(f"Rebuild error: {e}", file=sys.stderr)
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break
        t = threading.Thread(target=watch_loop, daemon=True)
        t.start()
        _serve_file(out_path, args.host, args.port, args.open_browser)
        return 0
    else:
        _serve_file(out_path, args.host, args.port, args.open_browser)
        return 0

def cmd_serve(args) -> int:
    html_path = Path(args.html).resolve()
    if not html_path.exists():
        print(f"error: file not found: {html_path}", file=sys.stderr)
        return 2
    _serve_file(html_path, args.host, args.port, args.open_browser)
    return 0

def main() -> int:
    ap = argparse.ArgumentParser(prog="df-gallery", description="Build and serve filterable, paginated HTML image galleries.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # build subcommand
    b = sub.add_parser("build", help="Build gallery HTML from CSV (optionally serve/watch).")
    b.add_argument("csv", help="Path to CSV with an image path column (default 'filename').")
    b.add_argument("--out", "-o", default="gallery.html", help="Output HTML file")
    b.add_argument("--path-col", default="filename", help="CSV column containing image paths/URLs")
    b.add_argument("--img-root", default="", help="Optional prefix joined before each filename (e.g. /data/images)")
    b.add_argument("--relative-to-html", action="store_true", help="Make paths relative to the output HTML's folder")
    b.add_argument("--chunk", type=int, default=500, help="Tiles to add per render batch (default: 500)")
    b.add_argument("--tile", type=int, default=200, help="Base tile size in px (default: 200)")
    b.add_argument("--title", default="Image Gallery", help="HTML page title")
    b.add_argument("--show-cols", nargs="*", default=None, help="Subset of columns to show (defaults to all except 'src').")
    b.add_argument("--collapse-meta", action="store_true", help="Start with metadata hidden (global toggle controls all).")
    b.add_argument("--page-size", type=int, default=250, help="Initial page size (user can change in UI).")
    # serve/watch options for build
    b.add_argument("--serve", action="store_true", help="Start a local HTTP server after building")
    b.add_argument("--watch", action="store_true", help="Rebuild when the CSV changes (implies --serve)")
    b.add_argument("--host", default="127.0.0.1", help="Host for the server (default: 127.0.0.1)")
    b.add_argument("--port", type=int, default=8000, help="Port for the server (default: 8000)")
    b.add_argument("--open", dest="open_browser", action="store_true", help="Open browser after starting server")
    b.add_argument("--no-open", dest="open_browser", action="store_false", help="Do not open browser")
    b.set_defaults(open_browser=True, func=cmd_build)

    # serve subcommand
    s = sub.add_parser("serve", help="Serve an existing gallery HTML without rebuilding.")
    s.add_argument("html", help="Path to gallery.html")
    s.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    s.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    s.add_argument("--open", dest="open_browser", action="store_true", help="Open browser after starting server")
    s.add_argument("--no-open", dest="open_browser", action="store_false", help="Do not open browser")
    s.set_defaults(open_browser=True, func=cmd_serve)

    args = ap.parse_args()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())