"""Info panel rows with computed dotted leaders, right-aligned values locked by textLength."""
ROWS = [
    ("Subject",        "Davi Oliveira"),
    ("Role",           "AI Agent Architect & Fullstack Dev"),
    ("Origin",         "Brazil"),
    ("Education",      "ADS - Systems Analysis & Development"),
    ("Status",         "Building & Shipping AI Agents"),
    ("ToolChain",      "Golang, React, Node, TS, Python"),
    (None, None),
    ("Core.Lang",      "Go / TypeScript / Python"),
    ("Core.Frontend",  "React / Vanilla JS / Design Systems"),
    ("Core.Backend",   "Node.js / Go / REST"),
    ("Core.Database",  "SQL / Procedures / Postgres"),
    ("Core.Infra",     "n8n / LangChain / LangGraph"),
    (None, None),
    ("Grid.Mail",      "davioliveeira.dev@gmail.com"),
    ("Grid.LinkedIn",  "in/davioliveeira"),
    ("Grid.GitHub",    "@davioliveeira"),
]

PX, PY = 530, 96          # panel origin
PW     = 600              # panel width
FS     = 14               # row font size
STEP   = 23               # row spacing
CHW    = FS * 0.60        # monospace advance width

from xml.sax.saxutils import escape

def rows_svg(pal):
    out = [f'<text x="{PX}" y="{PY-30}" fill="{pal["label"]}" font-size="13" letter-spacing="1.5">SYSTEM.INFO</text>']
    # LIVE badge
    out.append(f'<circle cx="{PX+PW-58}" cy="{PY-34}" r="4" fill="#ef4444">'
               f'<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    out.append(f'<text x="{PX+PW-46}" y="{PY-30}" fill="#ef4444" font-size="12" letter-spacing="1.2">LIVE</text>')

    y = PY
    for label, value in ROWS:
        if label is None:
            y += int(STEP*0.55); continue
        lw = len(label)  * CHW
        vw = len(value) * CHW
        gap = PW - lw - vw - 16
        n_dots = max(2, int(gap / (CHW*0.62)))
        leader = "·" * n_dots
        out.append(f'<text x="{PX}" y="{y}" fill="{pal["label"]}" font-size="{FS}">{escape(label)}</text>')
        out.append(f'<text x="{PX+lw+8}" y="{y}" fill="{pal["stroke"]}" font-size="{FS}">{leader}</text>')
        out.append(f'<text x="{PX+PW}" y="{y}" fill="{pal["text"]}" font-size="{FS}" text-anchor="end"'
                   f' textLength="{vw:.0f}" lengthAdjust="spacingAndGlyphs">{escape(value)}</text>')
        y += STEP
    # handle pill
    out.append(f'<rect x="{PX}" y="{y+14}" width="196" height="30" rx="15" fill="none" stroke="{pal["accent"]}"/>')
    out.append(f'<text x="{PX+98}" y="{y+34}" fill="{pal["accent"]}" font-size="14" text-anchor="middle">@davioliveeira</text>')
    return "\n".join(out)
