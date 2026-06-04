#!/usr/bin/env python3
"""
把 Claude Agent SDK 19 課課程，產生成一份漂亮的 16:9 HTML 投影片（slides.html）。

- 螢幕：← → / 空白 / 點擊翻頁，自動縮放置中
- 列印：每張投影片一頁（給 Chrome headless --print-to-pdf 產 slides.pdf）
- 自製輕量 Python 語法高亮（離線、不依賴 CDN，PDF 才不會缺色）

內容資料在 slides_data.py；本檔是「引擎」（高亮 / CSS / 模板 / 組裝）。
用法：python gen_slides.py
"""

import html
import re
from pathlib import Path

from slides_data import META, STAGES, FRAMEWORK, LESSONS, CLOSING

HERE = Path(__file__).parent
OUT = HERE / "slides.html"

# ────────────────────────────── Python 語法高亮 ──────────────────────────────

_KW = {
    "async", "await", "def", "class", "return", "with", "for", "if", "elif",
    "else", "try", "except", "finally", "raise", "yield", "import", "from",
    "as", "in", "not", "and", "or", "is", "lambda", "pass", "break",
    "continue", "global", "nonlocal", "assert", "del", "while",
}
_CONST = {"None", "True", "False", "self"}

_TOKEN = re.compile(
    r"""(?P<com>\#[^\n]*)
      | (?P<str>(?:[rbfRBF]{0,2})(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'))
      | (?P<dec>@[\w.]+)
      | (?P<word>[A-Za-z_]\w*)
      | (?P<num>\b\d[\d_]*\.?\d*\b)
    """,
    re.X,
)


def highlight(code: str) -> str:
    """把 Python 程式碼轉成帶 <span class> 的 HTML（已處理跳脫）。"""
    out, last = [], 0
    for m in _TOKEN.finditer(code):
        out.append(html.escape(code[last:m.start()]))
        kind = m.lastgroup
        text = m.group()
        cls = None
        if kind == "com":
            cls = "c-com"
        elif kind == "str":
            cls = "c-str"
        elif kind == "dec":
            cls = "c-dec"
        elif kind == "num":
            cls = "c-num"
        elif kind == "word":
            nxt = code[m.end():m.end() + 1]
            if text in _KW:
                cls = "c-kw"
            elif text in _CONST:
                cls = "c-const"
            elif nxt == "(":
                cls = "c-fn"
            elif text[:1].isupper():
                cls = "c-cls"
        out.append(f'<span class="{cls}">{html.escape(text)}</span>' if cls else html.escape(text))
        last = m.end()
    out.append(html.escape(code[last:]))
    return "".join(out)


def esc(s: str) -> str:
    return html.escape(s)


# ────────────────────────────── 投影片模板 ──────────────────────────────

def _points(points) -> str:
    items = []
    for head, desc in points:
        items.append(
            f'<li><span class="pt-head">{esc(head)}</span>'
            f'<span class="pt-desc">{esc(desc)}</span></li>'
        )
    return f'<ul class="points">{"".join(items)}</ul>'


def _codeblock(code: str, fname: str = "main.py") -> str:
    return (
        '<div class="code">'
        '<div class="code-bar"><span class="dot r"></span><span class="dot y"></span>'
        f'<span class="dot g"></span><span class="code-name">{esc(fname)}</span></div>'
        f'<pre><code>{highlight(code.strip(chr(10)))}</code></pre>'
        '</div>'
    )


def render_cover(s: dict) -> str:
    stats = "".join(
        f'<div class="stat"><span class="stat-n">{esc(n)}</span>'
        f'<span class="stat-l">{esc(l)}</span></div>'
        for n, l in s["stats"]
    )
    return f'''
    <div class="cover">
      <div class="cover-left">
        <div class="kicker">{esc(s["kicker"])}</div>
        <h1 class="cover-title">{esc(s["title"])}</h1>
        <p class="cover-sub">{esc(s["sub"])}</p>
        <div class="stats">{stats}</div>
      </div>
      <div class="cover-right" aria-hidden="true">
        <div class="glyph">&gt;_</div>
        <div class="glyph-cap">{esc(s["badge"])}</div>
      </div>
    </div>'''


def render_section(s: dict) -> str:
    lis = "".join(
        f'<li><span class="sec-no">{esc(no)}</span>'
        f'<span class="sec-name">{esc(name)}</span></li>'
        for no, name in s["lessons"]
    )
    return f'''
    <div class="section">
      <div class="sec-bignum" aria-hidden="true">{esc(s["num"])}</div>
      <div class="sec-body">
        <div class="kicker">{esc(s["kicker"])}</div>
        <h2 class="sec-title">{esc(s["title"])}</h2>
        <p class="sec-lead">{esc(s["lead"])}</p>
        <ul class="sec-list">{lis}</ul>
      </div>
    </div>'''


def render_concept(s: dict) -> str:
    callout = ""
    if s.get("callout"):
        callout = f'<div class="callout">{esc(s["callout"])}</div>'
    lead = f'<p class="lead">{esc(s["lead"])}</p>' if s.get("lead") else ""
    return f'''
    <div class="concept">
      <div class="kicker">{esc(s["kicker"])}</div>
      <h2 class="slide-title">{esc(s["title"])}</h2>
      {lead}
      {_points(s["points"])}
      {callout}
    </div>'''


def render_code(s: dict) -> str:
    caption = f'<p class="lead">{esc(s["caption"])}</p>' if s.get("caption") else ""
    note = f'<div class="code-note">{esc(s["note"])}</div>' if s.get("note") else ""
    return f'''
    <div class="codeslide">
      <div class="kicker">{esc(s["kicker"])}</div>
      <h2 class="slide-title">{esc(s["title"])}</h2>
      {caption}
      {_codeblock(s["code"], s.get("fname", "main.py"))}
      {note}
    </div>'''


def render_split(s: dict) -> str:
    """左要點、右程式碼（或表格）。"""
    right = _codeblock(s["code"], s.get("fname", "main.py")) if s.get("code") else s.get("right_html", "")
    return f'''
    <div class="split">
      <div class="split-left">
        <div class="kicker">{esc(s["kicker"])}</div>
        <h2 class="slide-title">{esc(s["title"])}</h2>
        {_points(s["points"])}
      </div>
      <div class="split-right">{right}</div>
    </div>'''


def render_outline(s: dict) -> str:
    cols = []
    for col in s["columns"]:
        rows = "".join(
            f'<li><span class="ol-no">{esc(no)}</span><span class="ol-t">{esc(t)}</span></li>'
            for no, t in col["items"]
        )
        cols.append(
            f'<div class="ol-col"><div class="ol-head">{esc(col["head"])}</div>'
            f'<ul class="ol-list">{rows}</ul></div>'
        )
    return f'''
    <div class="outline">
      <div class="kicker">{esc(s["kicker"])}</div>
      <h2 class="slide-title">{esc(s["title"])}</h2>
      <div class="ol-grid">{"".join(cols)}</div>
    </div>'''


def render_end(s: dict) -> str:
    links = "".join(f'<li>{esc(x)}</li>' for x in s["links"])
    return f'''
    <div class="cover end">
      <div class="cover-left">
        <div class="kicker">{esc(s["kicker"])}</div>
        <h1 class="cover-title">{esc(s["title"])}</h1>
        <p class="cover-sub">{esc(s["sub"])}</p>
        <ul class="end-links">{links}</ul>
      </div>
      <div class="cover-right" aria-hidden="true">
        <div class="glyph">✦</div>
        <div class="glyph-cap">{esc(s["badge"])}</div>
      </div>
    </div>'''


RENDERERS = {
    "cover": render_cover,
    "section": render_section,
    "concept": render_concept,
    "code": render_code,
    "split": render_split,
    "outline": render_outline,
    "end": render_end,
}


# ────────────────────────────── 組裝 ──────────────────────────────

def collect_slides():
    """把框架頁 + 各階段（分隔頁 + 課程頁）+ 結尾，攤平成一個 slide 列表。"""
    slides = list(FRAMEWORK)
    for stage in STAGES:
        slides.append({"kind": "section", **stage["divider"]})
        for no in stage["lessons"]:
            slides.extend(LESSONS[no])
    slides.extend(CLOSING)
    return slides


def build() -> str:
    slides = collect_slides()
    total = len(slides)
    pieces = []
    for idx, s in enumerate(slides, 1):
        body = RENDERERS[s["kind"]](s)
        chap = esc(s.get("chapter", ""))
        # 進度條寬度
        pct = idx / total * 100
        footer = (
            f'<div class="foot"><span class="foot-chap">{chap}</span>'
            f'<span class="foot-pg">{idx:02d}<span class="foot-sep"> / </span>{total:02d}</span></div>'
            f'<div class="prog"><i style="width:{pct:.2f}%"></i></div>'
        )
        pieces.append(
            f'<section class="slide kind-{s["kind"]}" data-i="{idx}">{body}{footer}</section>'
        )
    deck = "\n".join(pieces)
    return (
        HTML_HEAD
        .replace("__TITLE__", esc(META["doc_title"]))
        .replace("__CSS__", CSS)
        + f'<div id="deck">\n{deck}\n</div>\n'
        + HUD
        + f"<script>{JS.replace('__TOTAL__', str(total))}</script>\n"
        + "</body></html>"
    )


# ────────────────────────────── 樣式 ──────────────────────────────

CSS = r"""
:root{
  --bg0:#0c0a08; --bg1:#15100d; --panel:#1c1511; --panel2:#16100d;
  --ink:#F6EFE7; --mut:#AC9F92; --dim:#6f6258; --line:#352a23;
  --accent:#D97757; --accent2:#E8A87C; --cyan:#86B6BC;
  --c-kw:#E0996F; --c-str:#A9BE86; --c-com:#6f6258; --c-fn:#EBC074;
  --c-cls:#86A9CB; --c-num:#CB9CC9; --c-dec:#E0996F; --c-const:#CB9CC9;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;font-family:-apple-system,"Segoe UI","Noto Sans CJK TC","Microsoft JhengHei",sans-serif}
.mono,pre,code,.glyph{font-family:"Cascadia Code","JetBrains Mono",Consolas,"SF Mono",ui-monospace,monospace}

/* 每張投影片 = 1280×720 */
.slide{
  position:absolute; width:1280px; height:720px; left:50%; top:50%;
  transform:translate(-50%,-50%) scale(var(--s,1)); transform-origin:center center;
  background:
    radial-gradient(1200px 600px at 88% -10%, rgba(217,119,87,.13), transparent 60%),
    radial-gradient(900px 500px at -5% 110%, rgba(134,182,188,.08), transparent 55%),
    linear-gradient(160deg, var(--bg1), var(--bg0));
  color:var(--ink); overflow:hidden;
  padding:72px 84px 64px; display:none; flex-direction:column;
}
.slide.active{display:flex}
.slide::after{ /* 細邊框光 */
  content:""; position:absolute; inset:0; pointer-events:none;
  box-shadow:inset 0 0 0 1px rgba(246,239,231,.05);
}

/* 共用零件 */
.kicker{ color:var(--accent2); font-size:17px; font-weight:700;
  letter-spacing:.22em; text-transform:uppercase; margin-bottom:14px }
.slide-title{ font-size:50px; line-height:1.1; font-weight:800; letter-spacing:-.01em;
  color:#fff; margin-bottom:6px }
.lead{ font-size:24px; color:var(--mut); margin:14px 0 26px; max-width:34em; line-height:1.5 }

.points{ list-style:none; display:flex; flex-direction:column; gap:20px; margin-top:8px }
.points li{ position:relative; padding-left:38px; }
.points li::before{ content:"▸"; position:absolute; left:0; top:-2px; color:var(--accent);
  font-size:26px; line-height:1 }
.pt-head{ display:block; font-size:25px; font-weight:700; color:var(--ink); margin-bottom:3px }
.pt-desc{ display:block; font-size:19px; color:var(--mut); line-height:1.5 }

.callout{ margin-top:26px; padding:16px 22px; font-size:20px; line-height:1.5;
  color:var(--accent2); background:rgba(217,119,87,.09);
  border-left:4px solid var(--accent); border-radius:0 10px 10px 0 }

/* 程式碼塊 */
.code{ background:#0a0807; border:1px solid var(--line); border-radius:14px;
  overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,.45); margin-top:6px }
.code-bar{ display:flex; align-items:center; gap:9px; padding:13px 18px;
  background:linear-gradient(#191310,#140f0c); border-bottom:1px solid var(--line) }
.dot{ width:13px; height:13px; border-radius:50% }
.dot.r{ background:#E06C60 } .dot.y{ background:#E6B95C } .dot.g{ background:#7FB87C }
.code-name{ margin-left:10px; font-size:15px; color:var(--dim); letter-spacing:.04em }
.code pre{ padding:22px 26px; overflow:hidden }
.code code{ font-size:20px; line-height:1.62; color:#E8E0D6; white-space:pre }
.c-kw{color:var(--c-kw);font-weight:600} .c-str{color:var(--c-str)} .c-com{color:var(--c-com);font-style:italic}
.c-fn{color:var(--c-fn)} .c-cls{color:var(--c-cls)} .c-num{color:var(--c-num)}
.c-dec{color:var(--c-dec)} .c-const{color:var(--c-const)}
.code-note{ margin-top:18px; font-size:19px; color:var(--mut); padding-left:18px;
  border-left:3px solid var(--cyan); line-height:1.5 }

/* 封面 */
.cover{ display:flex; width:100%; height:100%; align-items:center; gap:40px }
.cover-left{ flex:1 }
.cover-title{ font-size:78px; line-height:1.04; font-weight:850; color:#fff;
  letter-spacing:-.02em; margin:6px 0 18px }
.cover-sub{ font-size:25px; color:var(--mut); line-height:1.55; max-width:30em }
.stats{ display:flex; gap:54px; margin-top:48px }
.stat-n{ display:block; font-size:54px; font-weight:850; color:var(--accent);
  font-family:inherit; line-height:1 }
.stat-l{ display:block; font-size:18px; color:var(--mut); margin-top:8px; letter-spacing:.04em }
.cover-right{ width:330px; height:330px; position:relative; display:grid; place-items:center;
  border:1px solid var(--line); border-radius:28px;
  background:radial-gradient(circle at 50% 35%, rgba(217,119,87,.16), rgba(20,15,12,.2));
  flex:none }
.glyph{ font-size:150px; font-weight:700; color:var(--accent); line-height:1;
  text-shadow:0 8px 40px rgba(217,119,87,.4) }
.glyph-cap{ position:absolute; bottom:26px; font-size:16px; color:var(--mut); letter-spacing:.18em }
.end-links{ list-style:none; margin-top:34px; display:flex; flex-direction:column; gap:11px }
.end-links li{ font-size:19px; color:var(--cyan); padding-left:24px; position:relative }
.end-links li::before{ content:"→"; position:absolute; left:0; color:var(--accent) }

/* 階段分隔頁 */
.section{ position:relative; width:100%; height:100%; display:flex; align-items:center }
.sec-bignum{ position:absolute; right:-20px; top:50%; transform:translateY(-50%);
  font-size:420px; font-weight:850; line-height:1; color:transparent;
  -webkit-text-stroke:2px rgba(217,119,87,.22); font-family:inherit; user-select:none }
.sec-body{ position:relative; max-width:62% }
.sec-title{ font-size:64px; font-weight:850; color:#fff; letter-spacing:-.01em; margin:4px 0 14px }
.sec-lead{ font-size:23px; color:var(--mut); line-height:1.55; margin-bottom:30px; max-width:30em }
.sec-list{ list-style:none; display:flex; flex-direction:column; gap:13px }
.sec-list li{ display:flex; align-items:baseline; gap:16px; font-size:22px }
.sec-no{ color:var(--accent); font-weight:800; font-family:inherit; min-width:34px }
.sec-name{ color:var(--ink) }

/* 課程地圖 */
.ol-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:26px 34px; margin-top:26px }
.ol-col{ }
.ol-head{ font-size:18px; font-weight:800; color:var(--accent2); letter-spacing:.06em;
  padding-bottom:9px; margin-bottom:12px; border-bottom:1px solid var(--line) }
.ol-list{ list-style:none; display:flex; flex-direction:column; gap:10px }
.ol-list li{ display:flex; gap:12px; align-items:baseline; font-size:18px }
.ol-no{ color:var(--accent); font-weight:800; font-family:inherit; font-size:15px; min-width:24px }
.ol-t{ color:var(--ink) }

/* split */
.split{ display:flex; gap:46px; width:100%; height:100%; align-items:center }
.split-left{ flex:1; min-width:0 }
.split-right{ flex:1.05; min-width:0 }
.split .points{ gap:16px } .split .pt-head{ font-size:22px } .split .pt-desc{ font-size:17px }
.split .code pre{ padding:18px 20px }
.split .code code{ font-size:15px; line-height:1.55 }

/* 頁尾 / 進度 */
.foot{ position:absolute; left:84px; right:84px; bottom:30px;
  display:flex; justify-content:space-between; align-items:center;
  font-size:15px; color:var(--dim); letter-spacing:.04em }
.foot-chap{ text-transform:uppercase; letter-spacing:.14em }
.foot-pg{ font-family:inherit; font-weight:700; color:var(--mut) }
.foot-sep{ color:var(--dim) }
.prog{ position:absolute; left:0; bottom:0; height:4px; width:100%; background:rgba(255,255,255,.05) }
.prog i{ display:block; height:100%; background:linear-gradient(90deg,var(--accent),var(--accent2)) }

/* HUD（螢幕用，列印隱藏）*/
#hud{ position:fixed; right:18px; bottom:14px; z-index:9; display:flex; gap:10px; align-items:center;
  font:13px/1 -apple-system,sans-serif; color:#8b8178 }
#hud button{ background:#1c1511; color:#cabfb4; border:1px solid #352a23; border-radius:8px;
  padding:7px 11px; cursor:pointer; font-size:14px }
#hud button:hover{ background:#241b16; color:#fff }
#hint{ position:fixed; left:18px; bottom:16px; z-index:9; font:12px/1.4 -apple-system,sans-serif;
  color:#6f6258 }

/* 螢幕：黑底襯托 */
@media screen{ body{ background:#070605; overflow:hidden } }

/* 列印：每張一頁 */
@media print{
  @page{ size:1280px 720px; margin:0 }
  html,body{ background:#0c0a08 }
  #deck{ }
  .slide{ position:relative; left:auto; top:auto; transform:none !important;
    display:flex !important; page-break-after:always; break-after:page; margin:0 }
  .slide:last-child{ page-break-after:auto }
  #hud,#hint{ display:none !important }
}
"""

HTML_HEAD = """<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>__CSS__</style>
</head><body>
"""

HUD = """
<div id="hud">
  <button onclick="go(i-1)">‹</button>
  <span id="hud-n">1 / 1</span>
  <button onclick="go(i+1)">›</button>
</div>
<div id="hint">← → / 空白翻頁　·　F 全螢幕　·　列印(Ctrl/Cmd+P) 匯出 PDF</div>
"""

JS = r"""
const slides=[...document.querySelectorAll('.slide')];
const TOTAL=__TOTAL__; let i=0;
const hudN=document.getElementById('hud-n');
function fit(){const s=Math.min(innerWidth/1280,innerHeight/720);
  document.documentElement.style.setProperty('--s',s);}
function go(n){ i=Math.max(0,Math.min(slides.length-1,n));
  slides.forEach((s,k)=>s.classList.toggle('active',k===i));
  hudN.textContent=(i+1)+' / '+TOTAL; location.hash=i+1; }
addEventListener('resize',fit);
addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();go(i+1);}
  else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(i-1);}
  else if(e.key==='Home'){go(0);} else if(e.key==='End'){go(slides.length-1);}
  else if(e.key==='f'||e.key==='F'){ if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen(); }
});
addEventListener('click',e=>{ if(e.target.closest('#hud'))return; go(i+1); });
fit(); const h=parseInt(location.hash.slice(1)); go(h?h-1:0);
"""

if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    n = len(collect_slides())
    print(f"已輸出 {OUT}（{n} 張投影片，{OUT.stat().st_size/1024:.0f} KB）")
