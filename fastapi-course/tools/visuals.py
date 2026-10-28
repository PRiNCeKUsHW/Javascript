"""Animated illustrations that sit beside a concept (`visual: <name>`).

Each builder returns (svg_markup, js_lines). The SVG is drawn in a 620 x 640 box and
every animation is a finite GSAP tween on the scene timeline `tl`, sized to the
scene's duration so the illustration keeps moving while the narration plays.
"""

FONT = 'font-family="Inter, sans-serif" font-weight="700"'
MONO = 'font-family="JetBrains Mono, monospace" font-weight="700"'
INK, TEAL, AMBER, RED, GREEN, NAVY = "#0f1b2d", "#05998b", "#f5a524", "#e5484d", "#2f9e44", "#1d2b45"


def reps(dur, cycle, start=0.6):
    return max(0, int((dur - start) / cycle) - 1)


def client_server(p, dur):
    svg = f"""
  <rect x="60" y="70" width="120" height="200" rx="22" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <rect x="78" y="96" width="84" height="140" rx="8" fill="#d7f2ee"/>
  <rect x="40" y="370" width="200" height="130" rx="14" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <rect x="58" y="388" width="164" height="94" rx="6" fill="#d7f2ee"/>
  <rect x="20" y="500" width="240" height="18" rx="9" fill="{INK}"/>
  <text x="140" y="580" text-anchor="middle" {FONT} font-size="34" fill="{INK}">Clients</text>
  <rect x="410" y="150" width="170" height="340" rx="22" fill="{NAVY}"/>
  <rect x="430" y="180" width="130" height="70" rx="10" fill="#2b3d63"/><rect x="430" y="270" width="130" height="70" rx="10" fill="#2b3d63"/><rect x="430" y="360" width="130" height="70" rx="10" fill="#2b3d63"/>
  <circle id="{p}-led1" cx="540" cy="215" r="10" fill="#19c2b0"/><circle id="{p}-led2" cx="540" cy="305" r="10" fill="#19c2b0"/><circle id="{p}-led3" cx="540" cy="395" r="10" fill="#19c2b0"/>
  <text x="495" y="560" text-anchor="middle" {FONT} font-size="34" fill="{INK}">Server</text>
  <path d="M195 175 C290 175 320 230 400 250" fill="none" stroke="#b8c4d2" stroke-width="6" stroke-dasharray="14 12"/>
  <path d="M250 430 C320 430 340 380 400 370" fill="none" stroke="#b8c4d2" stroke-width="6" stroke-dasharray="14 12"/>
  <g id="{p}-req"><rect x="170" y="150" width="110" height="48" rx="24" fill="{TEAL}"/><text x="225" y="183" text-anchor="middle" {MONO} font-size="28" fill="#fff">GET</text></g>
  <g id="{p}-res"><rect x="300" y="395" width="120" height="48" rx="24" fill="{AMBER}"/><text x="360" y="428" text-anchor="middle" {MONO} font-size="28" fill="{INK}">JSON</text></g>"""
    n = reps(dur, 2.4)
    js = [f'tl.fromTo("#{p}-req", {{ x: 0, y: 0, opacity: 1 }}, {{ x: 190, y: 75, opacity: 0, duration: 1.1, ease: "power1.in", repeat: {n}, repeatDelay: 1.3 }}, 0.6);',
          f'tl.fromTo("#{p}-res", {{ x: 0, y: 0, opacity: 0 }}, {{ x: -230, y: 20, opacity: 1, duration: 1.1, ease: "power1.out", repeat: {n}, repeatDelay: 1.3 }}, 1.8);',
          f'tl.fromTo("#{p}-led1, #{p}-led2, #{p}-led3", {{ opacity: 1 }}, {{ opacity: 0.25, duration: 0.3, stagger: 0.12, ease: "steps(1)", yoyo: true, repeat: {reps(dur, 0.6) | 1} }}, 0.6);']
    return svg, js


def json_doc(p, dur):
    lines = ['{', '  "id": 42,', '  "title": "Learn FastAPI",', '  "done": false', '}']
    rows = "".join(f'<text x="70" y="{170 + i * 70}" {MONO} font-size="34" fill="{"#e5e9f0" if i in (0, 4) else "#b5e08c"}">{l.replace("&", "&amp;").replace("<", "&lt;")}</text>' for i, l in enumerate(lines))
    svg = f"""
  <rect x="30" y="60" width="560" height="460" rx="28" fill="#0e1726"/>
  <rect id="{p}-band" x="30" y="195" width="560" height="62" fill="rgba(5,153,139,0.3)"/>
  {rows}
  <text x="310" y="590" text-anchor="middle" {FONT} font-size="34" fill="{INK}">JSON response</text>"""
    n = reps(dur, 1.0)
    js = [f'tl.fromTo("#{p}-band", {{ y: 0 }}, {{ keyframes: {{ y: [0, 70, 140, 0] }}, duration: 3, ease: "none", repeat: {max(0, int(dur / 3) - 1)} }}, 0.6);']
    return svg, js


def shield(p, dur):
    svg = f"""
  <path d="M310 90 L470 150 L470 300 C470 410 390 480 310 520 C230 480 150 410 150 300 L150 150 Z" fill="{TEAL}" stroke="{INK}" stroke-width="8"/>
  <path d="M245 300 L295 350 L385 250" fill="none" stroke="#ffffff" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>
  <g id="{p}-ok"><rect x="10" y="190" width="150" height="56" rx="28" fill="{GREEN}"/><text x="85" y="228" text-anchor="middle" {MONO} font-size="28" fill="#fff">age=21</text></g>
  <g id="{p}-bad"><rect x="10" y="350" width="170" height="56" rx="28" fill="{RED}"/><text x="95" y="388" text-anchor="middle" {MONO} font-size="28" fill="#fff">age="abc"</text></g>
  <g id="{p}-x" opacity="0"><circle cx="110" cy="470" r="40" fill="{RED}"/><text x="110" y="484" text-anchor="middle" {FONT} font-size="34" fill="#fff">422</text></g>
  <text x="310" y="600" text-anchor="middle" {FONT} font-size="34" fill="{INK}">Validation</text>"""
    n = reps(dur, 3.0)
    js = [f'tl.fromTo("#{p}-ok", {{ x: 0, opacity: 1 }}, {{ keyframes: {{ x: [0, 200, 460], opacity: [1, 1, 0] }}, duration: 1.4, ease: "none", repeat: {n}, repeatDelay: 1.6 }}, 0.6);',
          f'tl.fromTo("#{p}-bad", {{ x: 0 }}, {{ keyframes: {{ x: [0, 120, 0] }}, duration: 1.2, ease: "power2.inOut", repeat: {n}, repeatDelay: 1.8 }}, 1.6);',
          f'tl.fromTo("#{p}-x", {{ opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)", yoyo: true, repeat: {2 * n + 1}, repeatDelay: 1.2 }}, 2.2);']
    return svg, js


def database(p, dur):
    rows = "".join(f'<g id="{p}-r{i}"><rect x="250" y="{150 + i * 86}" width="330" height="70" rx="12" fill="#ffffff" stroke="#cfd9e3" stroke-width="4"/>'
                   f'<text x="275" y="{196 + i * 86}" {MONO} font-size="28" fill="{INK}">{i + 1}  task {i + 1}</text>'
                   f'<circle cx="545" cy="{185 + i * 86}" r="14" fill="{GREEN if i % 2 == 0 else "#cfd9e3"}"/></g>' for i in range(4))
    svg = f"""
  <ellipse cx="130" cy="150" rx="100" ry="36" fill="#19c2b0" stroke="{INK}" stroke-width="7"/>
  <path d="M30 150 V420 C30 470 230 470 230 420 V150" fill="{TEAL}" stroke="{INK}" stroke-width="7"/>
  <ellipse cx="130" cy="150" rx="100" ry="36" fill="#19c2b0" stroke="{INK}" stroke-width="7"/>
  <path d="M30 240 C30 280 230 280 230 240 M30 330 C30 370 230 370 230 330" fill="none" stroke="{INK}" stroke-width="6"/>
  {rows}
  <text x="310" y="590" text-anchor="middle" {FONT} font-size="34" fill="{INK}">Rows become objects</text>"""
    js = [f'tl.fromTo("#{p}-r{i}", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {0.6 + i * 0.35:.2f});' for i in range(4)]
    js.append(f'tl.fromTo("#{p}-r0, #{p}-r1, #{p}-r2, #{p}-r3", {{ scale: 1 }}, {{ scale: 1.04, transformOrigin: "50% 50%", duration: 0.3, stagger: 0.3, yoyo: true, repeat: {reps(dur, 2.4, 2.5) | 1} }}, 2.4);')
    return svg, js


def layers(p, dur):
    names = ["Router", "Service", "Repository", "Database"]
    cols = [TEAL, "#2f6fdb", "#7a4fd6", NAVY]
    rows = "".join(f'<g id="{p}-l{i}"><rect x="80" y="{60 + i * 125}" width="460" height="100" rx="20" fill="{cols[i]}"/>'
                   f'<text x="310" y="{122 + i * 125}" text-anchor="middle" {FONT} font-size="36" fill="#fff">{n}</text></g>' for i, n in enumerate(names))
    svg = f"""{rows}
  <circle id="{p}-dot" cx="560" cy="110" r="20" fill="{AMBER}" stroke="{INK}" stroke-width="5"/>
  <text x="310" y="600" text-anchor="middle" {FONT} font-size="34" fill="{INK}">One job per layer</text>"""
    n = max(0, int((dur - 0.6) / 3.2) - 1)
    js = [f'tl.fromTo("#{p}-dot", {{ y: 0 }}, {{ keyframes: {{ y: [0, 125, 250, 375, 250, 125, 0] }}, duration: 3.2, ease: "none", repeat: {n} }}, 0.6);',
          f'tl.fromTo("#{p}-l0, #{p}-l1, #{p}-l2, #{p}-l3", {{ x: 0 }}, {{ x: -16, duration: 0.25, stagger: 0.5, yoyo: true, repeat: 1, repeatDelay: 0, ease: "power2.out" }}, 0.6);']
    return svg, js


def lock(p, dur):
    svg = f"""
  <path id="{p}-shackle" d="M200 260 V180 C200 100 420 100 420 180 V260" fill="none" stroke="{INK}" stroke-width="30" stroke-linecap="round"/>
  <rect x="160" y="250" width="300" height="230" rx="34" fill="{AMBER}" stroke="{INK}" stroke-width="8"/>
  <circle cx="310" cy="340" r="26" fill="{INK}"/><rect x="298" y="350" width="24" height="70" rx="10" fill="{INK}"/>
  <g id="{p}-tok"><rect x="40" y="520" width="180" height="60" rx="14" fill="{RED}"/><rect x="220" y="520" width="180" height="60" fill="#7a4fd6"/><rect x="400" y="520" width="180" height="60" rx="14" fill="{TEAL}"/>
  <text x="130" y="561" text-anchor="middle" {MONO} font-size="28" fill="#fff">header</text><text x="310" y="561" text-anchor="middle" {MONO} font-size="28" fill="#fff">payload</text><text x="490" y="561" text-anchor="middle" {MONO} font-size="28" fill="#fff">sign</text></g>"""
    n = reps(dur, 3.0)
    js = [f'tl.fromTo("#{p}-shackle", {{ y: 0 }}, {{ y: -40, duration: 0.5, ease: "power2.out", yoyo: true, repeat: {2 * n + 1}, repeatDelay: 1.0 }}, 1.0);',
          f'tl.fromTo("#{p}-tok", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.6);']
    return svg, js


def gear_path(cx, cy, r, teeth):
    import math
    pts = []
    for i in range(teeth * 2):
        a = math.pi * i / teeth
        rr = r if i % 2 == 0 else r * 0.8
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def gears(p, dur):
    svg = f"""
  <path id="{p}-g1" d="{gear_path(220, 260, 150, 10)}" fill="{TEAL}" stroke="{INK}" stroke-width="7"/>
  <circle cx="220" cy="260" r="46" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <path id="{p}-g2" d="{gear_path(450, 420, 110, 8)}" fill="{AMBER}" stroke="{INK}" stroke-width="7"/>
  <circle cx="450" cy="420" r="34" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <text x="310" y="600" text-anchor="middle" {FONT} font-size="34" fill="{INK}">Work in the background</text>"""
    js = [f'tl.fromTo("#{p}-g1", {{ rotation: 0 }}, {{ rotation: {int(dur * 40)}, transformOrigin: "50% 50%", duration: {max(1, dur - 0.6):.2f}, ease: "none" }}, 0.6);',
          f'tl.fromTo("#{p}-g2", {{ rotation: 0 }}, {{ rotation: {-int(dur * 55)}, transformOrigin: "50% 50%", duration: {max(1, dur - 0.6):.2f}, ease: "none" }}, 0.6);']
    return svg, js


def tests(p, dur):
    rows = "".join(f'<g><rect x="70" y="{90 + i * 100}" width="64" height="64" rx="14" fill="#ffffff" stroke="{INK}" stroke-width="6"/>'
                   f'<path id="{p}-c{i}" d="M84 {124 + i * 100} L100 {140 + i * 100} L124 {104 + i * 100}" fill="none" stroke="{GREEN}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
                   f'<rect x="160" y="{106 + i * 100}" width="{300 - i * 30}" height="30" rx="15" fill="#cfd9e3"/></g>' for i in range(4))
    svg = f"""{rows}
  <rect x="70" y="510" width="480" height="30" rx="15" fill="#dbe4ec"/>
  <rect id="{p}-bar" x="70" y="510" width="480" height="30" rx="15" fill="{GREEN}"/>
  <text id="{p}-ok" x="310" y="600" text-anchor="middle" {FONT} font-size="34" fill="{GREEN}">4 passed</text>"""
    js = [f'tl.fromTo("#{p}-c{i}", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.3, ease: "power2.out" }}, {0.8 + i * 0.5:.2f});' for i in range(4)]
    js += [f'tl.fromTo("#{p}-bar", {{ scaleX: 0, transformOrigin: "0 50%" }}, {{ scaleX: 1, duration: 2.0, ease: "none" }}, 0.8);',
           f'tl.fromTo("#{p}-ok", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 2.9);']
    return svg, js


def plug(p, dur):
    svg = f"""
  <rect x="400" y="190" width="170" height="240" rx="30" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <rect x="440" y="255" width="22" height="50" rx="8" fill="{INK}"/><rect x="510" y="255" width="22" height="50" rx="8" fill="{INK}"/>
  <g id="{p}-plug"><path d="M40 310 C90 310 110 310 160 310" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>
  <rect x="160" y="230" width="160" height="160" rx="28" fill="{TEAL}" stroke="{INK}" stroke-width="7"/>
  <rect x="320" y="262" width="60" height="18" rx="6" fill="{INK}"/><rect x="320" y="330" width="60" height="18" rx="6" fill="{INK}"/></g>
  <g id="{p}-spark" opacity="0"><path d="M390 170 L410 130 M430 180 L470 150 M370 200 L340 160" stroke="{AMBER}" stroke-width="10" stroke-linecap="round"/></g>
  <text x="310" y="560" text-anchor="middle" {MONO} font-size="36" fill="{INK}">Depends(...)</text>"""
    n = reps(dur, 2.6)
    js = [f'tl.fromTo("#{p}-plug", {{ x: -60 }}, {{ x: 30, duration: 0.6, ease: "power2.in", yoyo: true, repeat: {2 * n + 1}, repeatDelay: 0.7 }}, 0.6);',
          f'tl.fromTo("#{p}-spark", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, yoyo: true, repeat: {2 * n + 1}, repeatDelay: 1.2 }}, 1.2);']
    return svg, js


def speed(p, dur):
    svg = f"""
  <path d="M90 420 A220 220 0 0 1 530 420" fill="none" stroke="#dbe4ec" stroke-width="44" stroke-linecap="round"/>
  <path d="M90 420 A220 220 0 0 1 530 420" fill="none" stroke="{TEAL}" stroke-width="44" stroke-linecap="round" pathLength="1" stroke-dasharray="1" id="{p}-arc" stroke-dashoffset="1"/>
  <line id="{p}-needle" x1="310" y1="420" x2="310" y2="240" stroke="{INK}" stroke-width="14" stroke-linecap="round"/>
  <circle cx="310" cy="420" r="28" fill="{INK}"/>
  <text x="310" y="540" text-anchor="middle" {FONT} font-size="40" fill="{INK}">High performance</text>"""
    js = [f'tl.fromTo("#{p}-needle", {{ rotation: -90, svgOrigin: "310 420" }}, {{ rotation: 70, svgOrigin: "310 420", duration: 1.4, ease: "power3.out" }}, 0.6);',
          f'tl.fromTo("#{p}-arc", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0.12, duration: 1.4, ease: "power3.out" }}, 0.6);',
          f'tl.to("#{p}-needle", {{ rotation: 62, svgOrigin: "310 420", duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: {reps(dur, 0.8, 2.2) | 1} }}, 2.1);']
    return svg, js


def docs(p, dur):
    rows = [("GET", "/items", "#2f6fdb"), ("POST", "/items", GREEN), ("PATCH", "/items/{id}", AMBER), ("DELETE", "/items/{id}", RED)]
    r = "".join(f'<g id="{p}-row{i}"><rect x="50" y="{170 + i * 92}" width="520" height="74" rx="14" fill="#ffffff" stroke="#dfe6ee" stroke-width="4"/>'
                f'<rect x="64" y="{184 + i * 92}" width="130" height="46" rx="10" fill="{c}"/>'
                f'<text x="129" y="{217 + i * 92}" text-anchor="middle" {FONT} font-size="28" fill="#fff">{m}</text>'
                f'<text x="214" y="{218 + i * 92}" {MONO} font-size="28" fill="{INK}">{u}</text></g>' for i, (m, u, c) in enumerate(rows))
    svg = f"""
  <rect x="20" y="40" width="580" height="560" rx="26" fill="#f4f6f8" stroke="{INK}" stroke-width="6"/>
  <rect x="20" y="40" width="580" height="70" rx="26" fill="#e3e9ef"/>
  <circle cx="60" cy="75" r="10" fill="#ff5f57"/><circle cx="90" cy="75" r="10" fill="#febc2e"/><circle cx="120" cy="75" r="10" fill="#28c840"/>
  <rect x="150" y="56" width="420" height="40" rx="20" fill="#ffffff"/><text x="170" y="86" {MONO} font-size="28" fill="{INK}">/docs</text>
  {r}
  <path id="{p}-cursor" d="M460 520 L460 580 L476 566 L490 596 L502 590 L488 560 L510 558 Z" fill="{INK}" stroke="#fff" stroke-width="3"/>"""
    js = [f'tl.fromTo("#{p}-row{i}", {{ opacity: 0, x: 30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {0.6 + i * 0.2:.2f});' for i in range(4)]
    n = reps(dur, 2.4, 1.8)
    js.append(f'tl.fromTo("#{p}-cursor", {{ x: 0, y: 0 }}, {{ keyframes: {{ x: [0, -120, -60, 0], y: [0, -330, -150, 0] }}, duration: 2.4, ease: "sine.inOut", repeat: {n} }}, 1.8);')
    js.append(f'tl.fromTo("#{p}-row0, #{p}-row1, #{p}-row2, #{p}-row3", {{ scale: 1 }}, {{ scale: 1.04, transformOrigin: "50% 50%", duration: 0.2, stagger: 0.6, yoyo: true, repeat: 1 }}, 2.2);')
    return svg, js


def containers(p, dur):
    cols = [TEAL, AMBER, "#2f6fdb", RED]
    boxes = "".join(f'<g id="{p}-b{i}"><rect x="{70 + (i % 2) * 250}" y="{300 - (i // 2) * 120}" width="230" height="110" rx="12" fill="{c}" stroke="{INK}" stroke-width="6"/>'
                    + "".join(f'<rect x="{90 + (i % 2) * 250 + k * 40}" y="{315 - (i // 2) * 120}" width="18" height="80" rx="6" fill="rgba(255,255,255,0.35)"/>' for k in range(5)) + "</g>"
                    for i, c in enumerate(cols))
    svg = f"""
  <path d="M30 430 H590 L540 520 H80 Z" fill="{NAVY}" stroke="{INK}" stroke-width="6"/>
  {boxes}
  <text x="310" y="600" text-anchor="middle" {FONT} font-size="34" fill="{INK}">Ship the same image everywhere</text>"""
    js = [f'tl.fromTo("#{p}-b{i}", {{ y: -500, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.55, ease: "bounce.out" }}, {0.6 + i * 0.45:.2f});' for i in range(4)]
    js.append(f'tl.to("#{p}-b0, #{p}-b1, #{p}-b2, #{p}-b3", {{ y: -6, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: {reps(dur, 1.2, 2.8) | 1} }}, 2.8);')
    return svg, js


def chat(p, dur):
    svg = f"""
  <rect x="30" y="60" width="200" height="340" rx="26" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <rect x="390" y="60" width="200" height="340" rx="26" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <path d="M240 230 H380" stroke="{TEAL}" stroke-width="10" stroke-dasharray="16 10"/>
  <g id="{p}-m1"><rect x="50" y="110" width="160" height="56" rx="20" fill="{TEAL}"/><text x="130" y="148" text-anchor="middle" {FONT} font-size="28" fill="#fff">Hi!</text></g>
  <g id="{p}-m2"><rect x="410" y="200" width="160" height="56" rx="20" fill="{AMBER}"/><text x="490" y="238" text-anchor="middle" {FONT} font-size="28" fill="{INK}">Hello</text></g>
  <g id="{p}-m3"><rect x="50" y="290" width="160" height="56" rx="20" fill="{TEAL}"/><text x="130" y="328" text-anchor="middle" {FONT} font-size="28" fill="#fff">Live!</text></g>
  <text x="310" y="500" text-anchor="middle" {FONT} font-size="34" fill="{INK}">One open connection,</text>
  <text x="310" y="550" text-anchor="middle" {FONT} font-size="34" fill="{INK}">messages both ways</text>"""
    js = [f'tl.fromTo("#{p}-m{i + 1}", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }}, {0.8 + i * 0.9:.2f});' for i in range(3)]
    return svg, js


def cache(p, dur):
    svg = f"""
  <rect x="40" y="90" width="200" height="140" rx="22" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
  <text x="140" y="175" text-anchor="middle" {FONT} font-size="34" fill="{INK}">API</text>
  <rect x="380" y="60" width="200" height="140" rx="22" fill="{RED}" stroke="{INK}" stroke-width="7"/>
  <text x="480" y="145" text-anchor="middle" {FONT} font-size="34" fill="#fff">Cache</text>
  <ellipse cx="480" cy="330" rx="100" ry="32" fill="#19c2b0" stroke="{INK}" stroke-width="7"/>
  <path d="M380 330 V470 C380 510 580 510 580 470 V330" fill="{TEAL}" stroke="{INK}" stroke-width="7"/>
  <text x="480" y="440" text-anchor="middle" {FONT} font-size="30" fill="#fff">DB</text>
  <path d="M240 130 H370" stroke="{GREEN}" stroke-width="10" stroke-linecap="round"/>
  <path d="M240 200 C300 260 320 330 370 380" fill="none" stroke="#b8c4d2" stroke-width="8" stroke-dasharray="12 10"/>
  <circle id="{p}-fast" cx="250" cy="130" r="16" fill="{GREEN}"/>
  <text x="300" y="590" text-anchor="middle" {FONT} font-size="34" fill="{INK}">2 ms vs 80 ms</text>"""
    js = [f'tl.fromTo("#{p}-fast", {{ x: 0 }}, {{ x: 110, duration: 0.35, ease: "power2.in", repeat: {reps(dur, 0.9)}, repeatDelay: 0.55 }}, 0.6);']
    return svg, js


VISUALS = {
    "client-server": client_server, "json": json_doc, "shield": shield, "database": database,
    "layers": layers, "lock": lock, "gears": gears, "tests": tests, "plug": plug, "speed": speed,
    "docs": docs, "containers": containers, "chat": chat, "cache": cache,
}


def render(name, prefix, dur):
    svg, js = VISUALS[name](prefix, dur)
    markup = f'<svg viewBox="0 0 620 640" width="620" height="640" aria-hidden="true">{svg}\n</svg>'
    return markup, ["    " + j for j in js]
