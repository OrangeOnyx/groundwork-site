# Groundwork one-command deploy: gates -> link check -> deploy -> live verify.
# Run from the groundwork-site clone: .\deploy.ps1
# Fails loudly at the first broken gate. Committing is not shipping; this is shipping.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

Write-Host "== Gate 1: copy and identity gates =="
$gates = python -X utf8 -c @"
import io, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
files = [f for f in glob.glob('*.html') + glob.glob('guide/*.html') + glob.glob('curriculum/*.html')]
banned = re.compile(r'\bleverage|\bseamless|\bempower|\bunlock\b|\brobust\b|actionable|data-driven|game-changer|synergy|circle back|best practices|dive into|\bdelve|\belevate\b|testament', re.I)
bad = []
for f in files:
    s = io.open(f, encoding='utf-8').read()
    if '—' in s: bad.append((f, 'em dash x%d' % s.count('—')))
    if 'mdash' in s or '#8212' in s: bad.append((f, 'mdash entity'))
    for m in banned.finditer(s): bad.append((f, 'banned word: ' + m.group(0)))
    if re.search(r'orange ocean|disbar', s, re.I): bad.append((f, 'identity term'))
if bad:
    print('GATE FAILURES:')
    for b in bad: print('  ', b)
    sys.exit(1)
print('gates clean across', len(files), 'files')
"@
if ($LASTEXITCODE -ne 0) { Write-Host $gates; throw "Copy gates failed. Fix before deploying." }
Write-Host $gates

Write-Host "== Gate 2: internal links resolve =="
$links = python -X utf8 -c @"
import io, glob, re, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
missing = []
for f in glob.glob('*.html') + glob.glob('guide/*.html') + glob.glob('curriculum/*.html'):
    base = os.path.dirname(f)
    s = io.open(f, encoding='utf-8').read()
    for href in re.findall(r'href=\"([^\"#]+?)(?:#[^\"]*)?\"', s):
        if href.startswith(('http', 'mailto', 'data:', 'tel:')): continue
        t = os.path.normpath(href.lstrip('/')) if href.startswith('/') else os.path.normpath(os.path.join(base, href))
        if t and not os.path.exists(t): missing.append((f, href))
if missing:
    print('BROKEN LINKS:')
    for m in missing: print('  ', m)
    sys.exit(1)
print('all internal links resolve')
"@
if ($LASTEXITCODE -ne 0) { Write-Host $links; throw "Link check failed. Fix before deploying." }
Write-Host $links

Write-Host "== Deploy =="
npx vercel deploy --prod --yes
if ($LASTEXITCODE -ne 0) { throw "Vercel deploy failed." }

Write-Host "== Live verification =="
$pages = @("", "guide/index.html", "guide/day-one.html", "guide/scorecard.html", "curriculum/index.html", "curriculum/level-1.html", "legal.html")
$fail = $false
foreach ($p in $pages) {
    $url = "https://groundwork.adamabdalla.com/$p"
    try {
        $r = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 20
        Write-Host ("{0}  {1}" -f $r.StatusCode, $url)
        if ($r.StatusCode -ne 200) { $fail = $true }
    } catch {
        Write-Host ("FAIL  {0}" -f $url); $fail = $true
    }
}
if ($fail) { throw "Live verification failed: a page is not serving 200." }
Write-Host "Shipped and verified."
