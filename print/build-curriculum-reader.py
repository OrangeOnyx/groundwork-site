# The Groundwork Curriculum -> site reader pages.
# Compiles the groundwork-curriculum repo working tree VERBATIM into
# curriculum/read/*.html: one page per module folder, plus orientation,
# shared, per-level overview / start-here / shared / repos / eli10 pages
# and a contents page. Same reading order and the same illustration plates
# (gw_plates.py) as the book, so book and site cannot drift apart.
# CONTENT IS THE REPO'S OWN VOICE: the site copy gates deliberately do not
# run on curriculum/read/ (see deploy.ps1); the shell strings here are gated.
# Also rewrites the block between the curriculum-reader markers in sitemap.xml.
# Usage: python print/build-curriculum-reader.py [repo-path] [lastmod YYYY-MM-DD]

import io
import re
import shutil
import sys
from pathlib import Path

import markdown
from PIL import Image

from gw_plates import group_device, GROUPS, climb_line

SITE = Path(__file__).resolve().parent.parent
REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else SITE.parent / "groundwork-curriculum"
LASTMOD = sys.argv[2] if len(sys.argv) > 2 else "2026-08-28"
OUT = SITE / "curriculum" / "read"
ASSETS = OUT / "assets"
BASE_URL = "https://groundwork.adamabdalla.com/curriculum/read/"
GH = "https://github.com/OrangeOnyx/groundwork-curriculum"
BOOK = GH + "/releases/latest/download/Groundwork-Curriculum.pdf"

LEVELS = [
    ("level-1-essentials", 1, "Essentials"),
    ("level-2-intermediate", 2, "Intermediate"),
    ("level-3-advanced", 3, "Advanced"),
    ("level-4-professional", 4, "Professional"),
    ("level-5-frontier", 5, "Frontier"),
]
GROUP_ORDER = ["00-start-here", "individual", "company", "shared", "repos", "eli10"]
GROUP_KEY = {"00-start-here": "start-here", "individual": "individual",
             "company": "company", "shared": "shared", "repos": "repos", "eli10": "eli10"}

MD = markdown.Markdown(extensions=["tables", "fenced_code"])


def rel_md_files(subdir):
    d = REPO / subdir
    if not d.is_dir():
        return []
    files = sorted(d.rglob("*.md"), key=lambda p: (
        tuple(s.lower() for s in p.relative_to(REPO).parts[:-1]),
        0 if p.name == "README.md" else 1, p.name.lower()))
    return [str(p.relative_to(REPO)).replace("\\", "/") for p in files]


def humanize(slug):
    s = re.sub(r"^\d+-", "", slug)
    return s.replace("-", " ").title().replace("Eli10", "ELI10").replace("Ai ", "AI ").replace("Mcp", "MCP").replace("Rag", "RAG")


def first_h1(relpath):
    try:
        for line in (REPO / relpath).read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                return re.sub(r"[#*`]", "", line[2:]).strip()
    except OSError:
        pass
    return None


# ---------- build the ordered page list ----------
pages = []  # dicts: slug,title,kicker,gkey,files,ghdir,level

def add(slug, title, kicker, gkey, files, ghdir, level=None):
    if files:
        pages.append(dict(slug=slug, title=title, kicker=kicker, gkey=gkey,
                          files=files, ghdir=ghdir, level=level))

add("orientation", "Read this first", "ORIENTATION", "overview",
    [f for f in ["README.md", "GROUNDWORK-AND-FLUENCY.md", "LEVEL-MAP.md"] if (REPO / f).exists()],
    GH)
add("shared-cover-letter", "The cover letters", "SHARED MATERIALS", "shared",
    rel_md_files("shared/cover-letter"), f"{GH}/tree/master/shared/cover-letter")
add("shared-starter-packs", "The starter packs", "SHARED MATERIALS", "shared",
    rel_md_files("shared/starter-packs"), f"{GH}/tree/master/shared/starter-packs")

for ldir, n, lname in LEVELS:
    kick = f"LEVEL {n} · {lname.upper()}"
    add(f"l{n}-overview", f"Level {n} at a glance", kick, "overview",
        [f"{ldir}/README.md"], f"{GH}/tree/master/{ldir}", n)
    add(f"l{n}-start-here", "Start here", kick, "start-here",
        rel_md_files(f"{ldir}/00-start-here"), f"{GH}/tree/master/{ldir}/00-start-here", n)
    for track in ("individual", "company"):
        tdir = REPO / ldir / track
        if not tdir.is_dir():
            continue
        for mod in sorted(p for p in tdir.iterdir() if p.is_dir()):
            mrel = f"{ldir}/{track}/{mod.name}"
            title = first_h1(f"{mrel}/README.md") or humanize(mod.name)
            add(f"l{n}-{track}-{mod.name}", title,
                f"{kick} · {track.upper()} TRACK", track,
                rel_md_files(mrel), f"{GH}/tree/master/{mrel}", n)
    add(f"l{n}-shared", f"Level {n} shared materials", kick, "shared",
        rel_md_files(f"{ldir}/shared"), f"{GH}/tree/master/{ldir}/shared", n)
    add(f"l{n}-repos", "Working repositories", kick, "repos",
        rel_md_files(f"{ldir}/repos"), f"{GH}/tree/master/{ldir}/repos", n)
    add(f"l{n}-eli10", f"Level {n} ELI10 companions", kick, "eli10",
        rel_md_files(f"{ldir}/eli10"), f"{GH}/tree/master/{ldir}/eli10", n)

add("appendix", "Contributing, and the license", "APPENDIX", "shared",
    [f for f in ["CONTRIBUTING.md"] if (REPO / f).exists()], GH)

FILE_PAGE = {}
for pg in pages:
    for f in pg["files"]:
        FILE_PAGE.setdefault(f, pg["slug"])

# ---------- markdown rendering with link/image rewriting ----------
if ASSETS.exists():
    shutil.rmtree(ASSETS)
ASSETS.mkdir(parents=True, exist_ok=True)


def copy_asset(repo_rel):
    src = REPO / repo_rel
    if not src.exists():
        return None
    flat = repo_rel.replace("/", "--")
    if src.suffix.lower() in (".svg",):
        dst = ASSETS / flat
        shutil.copyfile(src, dst)
    else:
        flat = re.sub(r"\.(png|jpg|jpeg|webp)$", ".jpg", flat, flags=re.I)
        dst = ASSETS / flat
        im = Image.open(src).convert("RGB")
        if im.width > 1400:
            im = im.resize((1400, int(im.height * 1400 / im.width)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=80)
    return "assets/" + flat


def resolve(base, href):
    href = re.sub(r"^(\./)+", "", href)
    parts = base.split("/") if base else []
    while href.startswith("../"):
        href = href[3:]
        parts = parts[:-1]
    return "/".join(parts + [href]) if parts else href


def render_file(relpath, gkey):
    text = (REPO / relpath).read_text(encoding="utf-8", errors="replace")
    base = relpath.rsplit("/", 1)[0] if "/" in relpath else ""

    def fix_img(m):
        alt, src = m.group(1), m.group(2)
        if src.startswith("http"):
            return m.group(0)
        rel = resolve(base, src)
        local = copy_asset(rel)
        return f"![{alt}]({local})" if local else f"*[image: {alt}]*"

    def fix_link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith(("http", "mailto:", "#")):
            return m.group(0)
        target, _, anchor = href.partition("#")
        rel = resolve(base, target)
        if rel in FILE_PAGE:
            return f"[{label}]({FILE_PAGE[rel]}.html)"
        if rel.endswith(".md") and (REPO / rel).exists():
            return f"[{label}]({GH}/blob/master/{rel})"
        return f"[{label}]({GH}/tree/master/{rel.rstrip('/')})"

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", fix_img, text)
    text = re.sub(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)", fix_link, text)
    MD.reset()
    html = MD.convert(text)
    dev = group_device(gkey, 16)
    return (f'<article class="doc"><p class="fcrumb">{dev}<span>{relpath}</span></p>\n'
            f"{html}\n</article>")


# ---------- page shell ----------
def nav_html(level):
    links = ['<a href="../index.html">Curriculum</a>']
    for i in range(1, 6):
        cur = ' aria-current="page"' if i == level else ""
        links.append(f'<a href="../level-{i}.html"{cur}>L{i}</a>')
    links.append('<a href="index.html">Reader</a>')
    links.append('<a class="keep" href="../../index.html">Main site</a>')
    return "\n    ".join(links)


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Groundwork Curriculum Reader</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#F4EFE2">
<link rel="canonical" href="{base_url}{slug}.html">
<meta property="og:image" content="https://groundwork.adamabdalla.com/assets/og-card.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='5' fill='%23F4EFE2'/%3E%3Crect x='8' y='22' width='16' height='4' rx='1' fill='%23C7681D'/%3E%3Crect x='8' y='16' width='16' height='4' rx='1' fill='%23C7681D'/%3E%3Crect x='8' y='10' width='16' height='4' rx='1' fill='%23C7681D'/%3E%3Ccircle cx='16' cy='5.5' r='2.6' fill='%23D9A419'/%3E%3Cpath d='M5 29 H27' stroke='%231E1B16' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;900&family=Besley:ital,wght@0,400;0,700;0,900;1,400;1,600&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/guide.css">
</head>
<body class="reader">
<a class="skip" href="#main">Skip to content</a>
<nav class="top" aria-label="Curriculum reader">
  <a class="brand" href="../../index.html" aria-label="Groundwork home">
    <svg viewBox="0 0 32 32" aria-hidden="true"><rect x="8" y="22" width="16" height="4" rx="1" fill="#C7681D"/><rect x="8" y="16" width="16" height="4" rx="1" fill="#C7681D"/><rect x="8" y="10" width="16" height="4" rx="1" fill="#C7681D"/><circle cx="16" cy="5.5" r="2.6" fill="#D9A419"/><path d="M5 29 H27" stroke="#1E1B16" stroke-width="2" stroke-linecap="round"/></svg>
    <b>GROUNDWORK</b>
  </a>
  <button class="navtoggle" aria-expanded="false" aria-label="Levels" onclick="var l=this.nextElementSibling,o=l.classList.toggle('open');this.setAttribute('aria-expanded',o)">MENU</button>
  <div class="links">
    {nav}
  </div>
</nav>
<main id="main" tabindex="-1">
  <span class="crumb"><a href="../index.html">The Curriculum</a> / <a href="index.html">Reader</a> / {crumbleaf}</span>
"""

FOOT = """
  <div class="pnav">
    <a href="{prev_href}">← {prev_label}</a>
    <a href="{next_href}">{next_label} →</a>
  </div>
</main>
<footer class="site"><div class="passiton">Pass it on: <button class="btn btn-ghost pbtn" onclick="navigator.clipboard.writeText(location.href);this.textContent='Copied'">Copy link</button> <a href="mailto:?subject=Groundwork&amp;body=A free, ungated AI readiness system for owners and operators: https://groundwork.adamabdalla.com">Send to a fellow owner</a> · <a href="https://github.com/OrangeOnyx/groundwork-curriculum">Curriculum on GitHub</a></div>
Groundwork. The free, ungated AI readiness system by Adam Abdalla. Lafayette, Louisiana. <a href="mailto:adam@adamabdalla.com">adam@adamabdalla.com</a> · <a href="../../legal.html">Disclaimer &amp; Privacy</a></footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""

OUT.mkdir(parents=True, exist_ok=True)

# ---------- write section pages ----------
for i, pg in enumerate(pages):
    prev = pages[i - 1] if i > 0 else None
    nxt = pages[i + 1] if i + 1 < len(pages) else None
    body = [HEAD.format(title=pg["title"], slug=pg["slug"], base_url=BASE_URL,
                        desc=f"{pg['kicker'].title()}: {pg['title']}. Compiled verbatim from the Groundwork Curriculum repository.",
                        nav=nav_html(pg["level"]), crumbleaf=pg["title"])]
    body.append(f'<div class="gopen">{group_device(pg["gkey"], 44)}'
                f'<div><span class="kicker" style="margin-bottom:.15rem">{pg["kicker"]}</span>'
                f'<h1 style="margin:.1rem 0 0">{pg["title"]}</h1></div></div>')
    nfiles = len(pg["files"])
    body.append(f'<p class="rnote">This page compiles {nfiles} file{"s" if nfiles != 1 else ""} '
                f'from the repository, verbatim, in reading order. The living version: '
                f'<a href="{pg["ghdir"]}">this folder on GitHub</a>.</p>')
    for f in pg["files"]:
        body.append(render_file(f, pg["gkey"]))
    body.append(FOOT.format(
        prev_href=(prev["slug"] + ".html") if prev else "index.html",
        prev_label=prev["title"] if prev else "Reader contents",
        next_href=(nxt["slug"] + ".html") if nxt else "index.html",
        next_label=nxt["title"] if nxt else "Reader contents"))
    (OUT / (pg["slug"] + ".html")).write_text("\n".join(body), encoding="utf-8", newline="\n")

# ---------- contents page ----------
toc = [HEAD.format(title="The Reader", slug="index", base_url=BASE_URL,
                   desc="The whole Groundwork Curriculum, readable on this site: every level, track, and module, compiled verbatim from the repository.",
                   nav=nav_html(None), crumbleaf="Contents")]
toc.append('<header class="page"><span class="kicker">THE READER</span>'
           '<h1>The whole curriculum, on this site.</h1>'
           '<p class="lede">Every level, both tracks, every module and companion, compiled '
           'verbatim from the repository in reading order. Nothing summarized, nothing gated. '
           'Prefer it bound? <a href="' + BOOK + '">The book</a> is the same content. '
           'Prefer the living files? <a href="' + GH + '">The repo</a> is the source of truth.</p></header>')
toc.append(f'<nav class="vw journeystrip" aria-label="Curriculum levels">{climb_line(None)}</nav>')
cur_kick = None
for pg in pages:
    if pg["kicker"] != cur_kick:
        if cur_kick is not None:
            toc.append("</div>")
        cur_kick = pg["kicker"]
        toc.append(f'<h2 style="margin-top:2.4rem">{cur_kick.title().replace("Eli10", "ELI10")}</h2><div>')
    n = len(pg["files"])
    toc.append(f'<div class="trow"><span class="tdev">{group_device(pg["gkey"], 20)}</span>'
               f'<a href="{pg["slug"]}.html">{pg["title"]}</a>'
               f'<span class="tcount">{n} file{"s" if n != 1 else ""}</span></div>')
toc.append("</div>")
toc.append(FOOT.format(prev_href="../index.html", prev_label="The Curriculum",
                       next_href="orientation.html", next_label="Read this first"))
(OUT / "index.html").write_text("\n".join(toc), encoding="utf-8", newline="\n")

# ---------- sitemap ----------
sm = SITE / "sitemap.xml"
s = sm.read_text(encoding="utf-8")
start, end = "<!-- curriculum-reader:start -->", "<!-- curriculum-reader:end -->"
if start not in s:
    s = s.replace("</urlset>", f"  {start}\n  {end}\n</urlset>")
urls = [f"  <url>\n    <loc>{BASE_URL}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>"]
for pg in pages:
    urls.append(f"  <url>\n    <loc>{BASE_URL}{pg['slug']}.html</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>")
block = start + "\n" + "\n".join(urls) + "\n  " + end
s = re.sub(re.escape(start) + r".*?" + re.escape(end), block, s, flags=re.S)
sm.write_text(s, encoding="utf-8", newline="\n")

total_files = sum(len(p["files"]) for p in pages)
print(f"reader: {len(pages) + 1} pages ({total_files} repo files compiled), "
      f"assets: {len(list(ASSETS.iterdir()))}, sitemap block: {len(pages) + 1} URLs")
