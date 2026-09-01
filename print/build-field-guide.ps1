# Field Guide build: extract doctrine from the guide pages -> inject into the print shell
# -> copy gates -> render with headless Edge -> assets/Groundwork-Program-Guide.pdf.
# Run from anywhere: .\print\build-field-guide.ps1
# The guide pages are the living doctrine; this script makes the PDF incapable of drifting from them.

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

Write-Host "== Assemble: extract templates from the guide pages =="
$assemble = python -X utf8 -c @'
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def read(p): return io.open(p, encoding="utf-8").read()

def strip_links(html):
    return re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", html, flags=re.S)

DOC_RE = re.compile(
    r"<h3>Document (\d+): (.*?)</h3>\s*"
    r"<p class=\"quiet\"[^>]*><code>(.*?)</code></p>\s*"
    r"(?:<p>(.*?)</p>\s*)?"
    r"<pre><code>(.*?)</code></pre>\s*"
    r"<p><strong>(How to [^:<]*:)</strong>(.*?)</p>", re.S)
HEAD_RE = re.compile(r"<span class=\"kicker\">(.*?)</span>\s*<h1>(.*?)</h1>\s*<p class=\"lede\">(.*?)</p>", re.S)

out, total = [], 0
PAGES = ["identity", "knowledge", "limits", "operator", "remember", "improve"]
for name in PAGES:
    page = read("guide/%s.html" % name)
    kicker, h1, lede = HEAD_RE.search(page).groups()
    out.append("<div class=\"layerhead\"><span class=\"kicker\">%s</span><h2>%s</h2><p class=\"lede\">%s</p></div>"
               % (kicker, h1, strip_links(lede)))
    docs = DOC_RE.findall(page)
    if not docs:
        print("FAIL: no document sections found in guide/%s.html" % name); sys.exit(1)
    for num, title, path, desc, tpl, label, how in docs:
        total += 1
        descblock = "<p>%s</p>" % strip_links(desc) if desc else ""
        out.append(("<div class=\"doc\"><span class=\"kicker\">Document %s</span>"
                    "<h3>%s</h3><p class=\"path\">%s</p>%s"
                    "<pre><code>%s</code></pre>"
                    "<p class=\"how\"><strong>%s</strong>%s</p></div>")
                   % (num, title, path, descblock, tpl, label, strip_links(how)))
if total != 15:
    print("FAIL: expected 15 document templates, found %d" % total); sys.exit(1)

op = read("guide/operator.html")
pres = re.findall(r"<pre><code>(.*?)</code></pre>", op, re.S)
pkg = [p for p in pres if "01_Operator/" in p and "00_CONTEXT.md" in p]
prm = [p for p in pres if "You are now the Operator" in p]
if len(pkg) != 1 or len(prm) != 1:
    print("FAIL: could not identify the package and prompt blocks in operator.html (found %d pre blocks)" % len(pres)); sys.exit(1)

shell = read("print/field-guide.html")
for marker, frag in (("<!-- INJECT:DOCUMENTS -->", "\n".join(out)),
                     ("<!-- INJECT:PACKAGE -->", "<pre><code>%s</code></pre>" % pkg[0]),
                     ("<!-- INJECT:PROMPT -->", "<pre><code>%s</code></pre>" % prm[0])):
    if marker not in shell:
        print("FAIL: marker missing from print shell: %s" % marker); sys.exit(1)
    shell = shell.replace(marker, frag)

io.open("print/field-guide.build.html", "w", encoding="utf-8").write(shell)
print("assembled: 15 documents across 6 orders, package + prompt from operator.html")
'@
if ($LASTEXITCODE -ne 0) { Write-Host $assemble; throw "Assembly failed." }
Write-Host $assemble

Write-Host "== Gates: copy and identity gates on the assembled book =="
$gates = python -X utf8 -c @'
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
s = io.open("print/field-guide.build.html", encoding="utf-8").read()
bad = []
if "\u2014" in s: bad.append("em dash x%d" % s.count("\u2014"))
if "mdash" in s or "#8212" in s: bad.append("mdash entity")
banned = re.compile(r"\bleverage|\bseamless|\bempower|\bunlock\b|\brobust\b|actionable|data-driven|game-changer|synergy|circle back|best practices|dive into|\bdelve|\belevate\b|testament", re.I)
for m in banned.finditer(s): bad.append("banned word: " + m.group(0))
if re.search(r"orange ocean|disbar", s, re.I): bad.append("identity term")
if bad:
    print("GATE FAILURES:")
    for b in bad: print("  ", b)
    sys.exit(1)
print("gates clean")
'@
if ($LASTEXITCODE -ne 0) { Write-Host $gates; throw "Copy gates failed on the assembled book." }
Write-Host $gates

Write-Host "== Render: headless Edge -> assets/Groundwork-Program-Guide.pdf =="
$edge = @(
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw "No Edge or Chrome executable found for headless rendering." }

$src = (Resolve-Path "print/field-guide.build.html").Path -replace '\\', '/'
$out = Join-Path $root "assets\Groundwork-Program-Guide.pdf"
& $edge --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 --print-to-pdf="$out" "file:///$src" 2>$null | Out-Null
if (-not (Test-Path $out)) { throw "Render produced no PDF." }
$kb = [math]::Round((Get-Item $out).Length / 1KB)
if ($kb -lt 50) { throw "Rendered PDF is suspiciously small ($kb KB); check the build HTML." }
Write-Host "Rendered $out ($kb KB). Inspect it, then commit and deploy with .\deploy.ps1."
