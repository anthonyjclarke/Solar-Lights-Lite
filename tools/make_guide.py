#!/usr/bin/env python3
"""One-page visual build guide: docs/ASSEMBLY.html.

Renders the numbered Markdown guides (docs/01-*.md ... docs/12-*.md) into a
single page, places each A3 drawing inline beside the module it belongs to,
and appends the wire schedule and parts checklist from their CSV files. The
Markdown stays the source of truth: edit the docs, then regenerate.

Needs the `markdown` package:  python3 tools/make_guide.py
"""
from pathlib import Path
import csv, html, re
import markdown

DOC = Path(__file__).resolve().parents[1] / 'docs'
DRAW = DOC / 'drawings'
VERSION = '0.6.0'

# Drawings placed inline in the first document that relies on them.
FIGURES = {
    '01': [('07-system-overview.svg', 'Sheet 7 – System overview')],
    '03': [('01-power.svg', 'Sheet 1 – Module A: power, charging and battery')],
    '04': [('02-controller.svg', 'Sheet 2 – Modules B–D: controller, light sensor and low-power LEDs'),
           ('BTE13-010A-pin-map.svg', 'Reference board connection and programming map'),
           ('breadboard-layout.svg', 'Breadboard layout – the whole system on a bench')],
    '07': [('06-telemetry-advanced.svg', 'Sheet 6 – Tier 1 Advanced Telemetry'),
           ('03-telemetry-production.svg', 'Sheet 3 – Tier 2 Production Telemetry'),
           ('perfboard-layout.svg', 'Perfboard layout – the whole system on a carrier')],
    '08': [('usbasp-wiring.png', 'USBasp wiring sheet')],
    '10': [('05-staging.svg', 'Sheet 5 – Staged power-up and wired serial monitor'),
           ('04-assembly.svg', 'Sheet 4 – Enclosure and physical assembly')],
}
SEE_ALSO = {'05': 'Sheet 2 is shown under Module B.', '06': 'Sheet 2 is shown under Module B.'}
NAV = {'01': 'Overview', '02': 'Parts and safety', '03': 'A · Power', '04': 'B · Controller',
       '05': 'C · Lighting', '06': 'D · Sensor', '07': 'E · Telemetry', '08': 'Firmware',
       '09': 'Home Assistant', '10': 'Commissioning', '11': 'Operation', '12': 'Going further'}


def slug(value, separator='-'):
    """GitHub-style heading anchor, so links written for GitHub keep working."""
    value = re.sub(r'[^\w\- –]', '', value.strip().lower())
    return value.replace(' ', separator)


def figure(name, caption):
    path = DRAW / name
    if path.suffix == '.svg':
        svg = path.read_text()
        body = svg[svg.index('<svg'):]
        pdf = 'SolarLights_Lite_Drawings.pdf' if name[0].isdigit() else name.replace('.svg', '.pdf')
        links = f'<a href="drawings/{name}">Full-size SVG</a>'
        if (DRAW / pdf).exists():
            links += f' · <a href="drawings/{pdf}">Printable PDF</a>'
    else:
        body = f'<img src="drawings/{name}" alt="{html.escape(caption)}">'
        links = f'<a href="drawings/{name.replace(".png", ".pdf")}">Printable PDF</a>'
    return (f'<figure><div class="drawing">{body}</div>'
            f'<figcaption><b>{html.escape(caption)}</b> · {links}</figcaption></figure>')


def render(path, num):
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'],
                           extension_configs={'toc': {'slugify': slug}})
    text = md.convert(path.read_text())
    # headings one level down, ids prefixed per document so they stay unique
    text = re.sub(r'<(/?)h([1-5])', lambda m: f'<{m.group(1)}h{int(m.group(2)) + 1}', text)
    text = re.sub(r'id="([^"]+)"', lambda m: f'id="d{num}-{m.group(1)}"', text)
    text = re.sub(r'href="#([^"]+)"', lambda m: f'href="#d{num}-{m.group(1)}"', text)
    # links between the numbered docs become in-page anchors
    text = re.sub(r'href="(\d\d)-[\w-]+\.md(?:#([^"]+))?"',
                  lambda m: f'href="#d{m.group(1)}' + (f'-{m.group(2)}"' if m.group(2) else '"'), text)
    text = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
                  lambda m: f'<pre class="mermaid">{m.group(1)}</pre>', text, flags=re.S)
    text = text.replace('<table>', '<div class="scroll"><table>').replace('</table>', '</table></div>')
    text = text.replace('<li>[ ] ', '<li class="check">').replace('<li>[x] ', '<li class="check done">')
    # drawings go after the introduction, before the first section rule
    figs = ''.join(figure(n, c) for n, c in FIGURES.get(num, []))
    if num in SEE_ALSO:
        figs += f'<p class="small"><a href="#d04">{SEE_ALSO[num]}</a></p>'
    if figs:
        text = text.replace('<hr />', figs + '<hr />', 1) if '<hr />' in text else text + figs
    title = re.search(r'<h2[^>]*>(.*?)</h2>', text).group(1)
    return f'<section id="d{num}">{text}<p class="top"><a href="#top">Back to top</a></p></section>', title


def csv_table(path, keep=None):
    rows = list(csv.reader(path.open()))
    head, body = rows[0], rows[1:]
    idx = [head.index(k) for k in keep] if keep else range(len(head))
    th = ''.join(f'<th>{html.escape(head[i])}</th>' for i in idx)
    tr = ''.join('<tr>' + ''.join(f'<td>{html.escape(r[i])}</td>' for i in idx) + '</tr>' for r in body)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


docs = sorted(p for p in DOC.glob('[0-9][0-9]-*.md'))
sections, nav = [], []
for p in docs:
    num = p.name[:2]
    body, title = render(p, num)
    sections.append(body)
    nav.append(f'<a href="#d{num}" title="{html.escape(title)}">{NAV.get(num, title)}</a>')

CSS = '''
:root{--ink:#173047;--muted:#516578;--green:#008572;--amber:#a95e00;--red:#a83232;--line:#d9e3e8}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:#f1f5f7;color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
header,main,footer{max-width:1320px;margin:auto;padding:32px}header{padding-top:52px}
h1{font-size:clamp(34px,5vw,58px);line-height:1.1;letter-spacing:-1.5px;margin:14px 0}
h2{font-size:30px;line-height:1.2;margin-top:0}h3{font-size:22px;margin-top:34px}h4{font-size:18px}
p,li{color:#2c4458}p{max-width:960px}.eyebrow{font-size:13px;letter-spacing:2px;font-weight:800;color:var(--green)}
.badge{display:inline-block;background:#e3f4ef;color:var(--green);padding:5px 12px;border-radius:6px;font-size:13px;font-weight:750}
a{color:#096b8c;text-underline-offset:4px}
nav{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}
nav a{background:white;border:1px solid #cad9e0;border-radius:8px;padding:8px 13px;text-decoration:none;font-size:15px}
nav a.pdf{background:var(--green);color:white;border-color:var(--green)}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.card,section{background:white;border:1px solid var(--line);border-radius:14px;padding:26px}
section{margin-bottom:26px}.card strong{font-size:26px;display:block}.card p{font-size:15px;margin:6px 0 0}
.hold{padding:18px 24px;margin:0 0 24px;border-radius:8px;background:#fff8e9;border-left:5px solid #c38325}
.hold p{margin:6px 0;max-width:none}
hr{border:0;border-top:1px solid #e3eaee;margin:30px 0}
figure{margin:24px 0}figcaption{font-size:14px;color:var(--muted);margin-top:8px}
.drawing{overflow:auto;border:1px solid #e0e7eb;border-radius:8px;background:white}
.drawing svg,.drawing img{width:100%;height:auto;min-width:900px;display:block}
pre{overflow:auto;background:#10293d;color:#edf7fb;border-radius:8px;padding:16px 20px;font:14px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace}
pre code{background:none;color:inherit;padding:0}pre.mermaid{background:white;color:var(--ink);border:1px solid #e0e7eb;text-align:center}
code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:14px;background:#edf4f7;padding:1px 5px;border-radius:4px}
.scroll{overflow:auto;margin:14px 0}table{width:100%;border-collapse:collapse;font-size:15px}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid #dde5e9;padding:9px 11px}th{background:#edf4f7}
li.check{list-style:none;margin-left:-22px}li.check::before{content:"\\2610  ";color:var(--green);font-weight:700}
.small{font-size:14px}.top{font-size:13px;text-align:right;margin:10px 0 0;max-width:none}.top a{color:var(--muted)}
footer{font-size:14px;color:var(--muted)}
@media(max-width:900px){.cards{grid-template-columns:1fr 1fr}}
@media(max-width:600px){header,main,footer{padding:18px}.cards{grid-template-columns:1fr}section{padding:16px}h2{font-size:24px}}
@media print{body{background:white}nav,.top{display:none}header,main{padding:0}.drawing svg,.drawing img{min-width:0}
section{break-before:page;border:0;padding:0}a{color:inherit}pre{color:#000;background:#fff;border:1px solid #999}footer{display:none}}
'''

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solar Lights Lite – Build and operate guide</title>
<style>{CSS}</style>
</head>
<body id="top">
<header>
<div class="eyebrow">SOLAR LIGHTS LITE / BUILD AND OPERATE GUIDE</div>
<h1>Low-power solar lights,<br>built one module at a time.</h1>
<span class="badge">v{VERSION} · MODULES A–F · TELEMETRY TIERS 0–2 · GATES 0–8</span>
<p>A small panel charges a protected Li-ion battery; an ATmega328P sleeps most of the time, detects dusk with a light sensor, and runs a low-power LED string from dusk to dawn. An optional Wemos D1 Mini reports it all to Home Assistant. Every module is built and tested on its own, so the project doubles as a hands-on course in soldering, microelectronics, embedded code and home automation.</p>
<nav>{"".join(nav)}<a href="#wires">Wire schedule</a><a href="#parts">Parts checklist</a><a class="pdf" href="drawings/SolarLights_Lite_Drawings.pdf">A3 drawings (PDF)</a></nav>
</header>
<main>
<div class="cards">
<div class="card"><strong>Build</strong><p>Six modules – power, controller, lighting, sensor, telemetry, enclosure – each with its own drawing and test gate.</p></div>
<div class="card"><strong>Learn</strong><p>SMD rework, AVR fuses and ISP, sleep and PWM, serial level shifting, ESPHome and Home Assistant.</p></div>
<div class="card"><strong>Commission</strong><p>Gates 0–8 add one thing at a time. Advanced Telemetry shows every controller decision during the soak test.</p></div>
<div class="card"><strong>Operate</strong><p>Production Telemetry reports hourly on battery power. The lights never depend on Wi-Fi.</p></div>
</div>
<div class="hold"><p><b>Low-power lights only.</b> The controller drives the LED string directly by PWM from pin D9 through a 47 Ω resistor, with no driver transistor. The whole string must run at 20 mA or less from a 3–4.2 V supply. Mains lights, 12 V garden lights and conventional or legacy fittings cannot be used; brighter lighting needs a driver stage (see Going further).</p></div>
{"".join(sections)}
<section id="wires"><h2>Wire schedule</h2><p>Every terminal in a row belongs to the same external net. Read the actual module pad labels and transistor pin order before soldering. <a href="wire-schedule.csv">CSV checklist</a> · <a href="netlist.json">Wiring model (JSON)</a></p>{csv_table(DOC / "wire-schedule.csv")}<p class="top"><a href="#top">Back to top</a></p></section>
<section id="parts"><h2>Parts checklist</h2><p><a href="parts-list.csv">CSV checklist</a> with a "have it?" column for printing.</p>{csv_table(DOC / "parts-list.csv", ["Module", "Ref", "Part / value", "Qty", "Notes"])}<p class="top"><a href="#top">Back to top</a></p></section>
</main>
<footer>Generated by tools/make_guide.py from docs/01–12, the drawings and the CSV files. Edit the Markdown, then regenerate. Diagrams render with Mermaid when online.</footer>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
mermaid.initialize({{startOnLoad: true, theme: "neutral"}});
</script>
</body>
</html>
'''
(DOC / 'ASSEMBLY.html').write_text(page)
print(f'wrote {DOC / "ASSEMBLY.html"} ({len(page) // 1024} KB, {len(sections)} guides)')
