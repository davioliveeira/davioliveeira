"""Assemble the animated terminal banner SVG (dark and light variants)."""
import numpy as np
from scipy.optimize import linear_sum_assignment
from panel import rows_svg

DARK  = dict(bg="#0D1117", chrome="#00d2ff", portrait="#00d2ff", text="#8b98a5",
             label="#5c6b7a", accent="#00d2ff", stroke="#1c2530", empty="#161b22")
LIGHT = dict(bg="#ffffff", chrome="#0284c7", portrait="#0369a1", text="#475569",
             label="#94a3b8", accent="#0284c7", stroke="#e2e8f0", empty="#f1f5f9")

W, H = 1180, 610
PX0, PY0 = 72, 128          # top-left of the dot grid
S = 1.16                     # grid cell -> svg units
DW = 1.9                     # dot / stroke width
# five logos: portrait holds 3.0s, each logo 1.7s, 1.15s transitions -> 18.4s loop.
# keyTimes must be uneven, otherwise every phase is forced to the same length.
PORTRAIT_HOLD, LOGO_HOLD, TRANS = 3.0, 1.7, 1.15
N_LOGOS = 5
TOTAL = PORTRAIT_HOLD + N_LOGOS*(TRANS + LOGO_HOLD) + TRANS
DUR = f"{TOTAL:.1f}s"

_t, _stops = 0.0, [0.0]
_t += PORTRAIT_HOLD; _stops.append(_t)
for _ in range(N_LOGOS):
    _t += TRANS; _stops.append(_t)
    _t += LOGO_HOLD; _stops.append(_t)
_t += TRANS; _stops.append(_t)
KT = ";".join(f"{v/TOTAL:.4f}" for v in _stops)          # 13 stops

grid   = np.load("light.npy")
GH, GW = grid.shape
py, px = np.where(grid)
P = np.stack([px, py], 1).astype(float)
LOGOS = ("go", "react", "python", "n8n", "code")
logos = [np.load(f"logo_{n}.npy") for n in LOGOS]
rng = np.random.default_rng(11)

def runs_for(mask):
    """Merge consecutive lit cells in a row into one 'Mx y h<len>' command. 3.7x fewer nodes."""
    out = []
    for y in range(GH):
        row = mask[y]
        x = 0
        while x < GW:
            if row[x]:
                x0 = x
                while x < GW and row[x]:
                    x += 1
                sx = PX0 + x0*S; sy = PY0 + y*S
                out.append(f"M{sx:.0f} {sy:.0f}h{(x-x0)*S:.0f}")
            else:
                x += 1
    return "".join(out)

# ---- drift bands: per-dot noise BEFORE grouping, else quantising rebuilds a square grid ----
noise = rng.normal(0, 4.0, size=len(P))
proj  = P[:,0]*0.6 + P[:,1]*0.8 + noise
band_of = np.digitize(proj, np.quantile(proj, np.linspace(0, 1, 95)[1:-1]))
centroid = logos[0].mean(0)

# ---- travellers ----
n_trav = 900
sel = rng.choice(len(P), n_trav, replace=False)
T0 = P[sel]
def match(src, dst):
    d = ((src[:,None,:] - dst[None,:,:])**2).sum(-1)
    r, c = linear_sum_assignment(d)
    o = np.empty_like(src); o[r] = dst[c]; return o
chain = [T0]
for lg in logos:
    chain.append(match(chain[-1], lg[:n_trav]))

def build(pal, fname):
    a = [].append; o = []
    def add(s): o.append(s)
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace">')
    add(f'<rect width="{W}" height="{H}" rx="10" fill="{pal["bg"]}" stroke="{pal["stroke"]}"/>')
    add(f'<path d="M1 11a10 10 0 0 1 10-10h{W-22}a10 10 0 0 1 10 10v28H1z" fill="{pal["empty"]}"/>')
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        add(f'<circle cx="{24+i*20}" cy="20" r="6" fill="{c}"/>')
    add(f'<text x="{W/2}" y="25" fill="{pal["label"]}" font-size="13" text-anchor="middle">profile.sh --live</text>')
    add(f'<line x1="0" y1="39" x2="{W}" y2="39" stroke="{pal["stroke"]}"/>')
    add(f'<rect x="40" y="62" width="448" height="516" rx="6" fill="none" stroke="{pal["stroke"]}"/>')
    add(f'<text x="54" y="88" fill="{pal["label"]}" font-size="12" letter-spacing="1.5">VISUAL.MAP</text>')

    # portrait: drift bands, each a run-compressed path
    add(f'<g stroke="{pal["portrait"]}" stroke-width="{DW}" fill="none" shape-rendering="crispEdges" opacity="0">')
    add(f'<animate attributeName="opacity" values="0;1" dur="0.01s" begin="2.1s" fill="freeze"/>')
    for b in range(band_of.max()+1):
        m = band_of == b
        if not m.any(): continue
        sub = np.zeros_like(grid); sub[P[m][:,1].astype(int), P[m][:,0].astype(int)] = True
        cxm, cym = P[m].mean(0)
        dx = (centroid[0]-cxm)*0.42*S; dy = (centroid[1]-cym)*0.42*S
        add(f'<path d="{runs_for(sub)}">')
        drift = ["0 0", "0 0"] + [f"{dx:.0f} {dy:.0f}"]*(2*N_LOGOS) + ["0 0"]
        fade  = ["1", "1"] + [".06"]*(2*N_LOGOS) + ["1"]
        add(f'<animateTransform attributeName="transform" type="translate" values="{";".join(drift)}"'
            f' keyTimes="{KT}" dur="{DUR}" repeatCount="indefinite"/>')
        add(f'<animate attributeName="opacity" values="{";".join(fade)}" keyTimes="{KT}" dur="{DUR}" repeatCount="indefinite"/>')
        add('</path>')
    add('</g>')

    # intro: 60 interleaved random groups scattered across the WHOLE portrait, not by region
    add(f'<g stroke="{pal["portrait"]}" stroke-width="{DW}" fill="none" shape-rendering="crispEdges">')
    order = rng.permutation(len(P))
    for gi, chunk in enumerate(np.array_split(order, 60)):
        sub = np.zeros_like(grid); sub[P[chunk][:,1].astype(int), P[chunk][:,0].astype(int)] = True
        add(f'<path d="{runs_for(sub)}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{0.03+gi*0.0007:.4f};0.94;1"'
            f' dur="2.2s" begin="{gi*0.03:.2f}s" fill="freeze"/></path>')
    add('</g>')

    # travellers: sparse swarm, hidden during the portrait phase
    seq = [chain[0], chain[0]]
    for li in range(1, N_LOGOS+1):
        seq += [chain[li], chain[li]]
    seq.append(chain[0])
    # hidden while the portrait shows, visible only during the logo phases
    trav_op = ["0", "0"] + ["1"]*(2*N_LOGOS) + ["0"]
    add(f'<g fill="{pal["accent"]}" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.01s" begin="2.1s" fill="freeze"/>')
    for i in range(n_trav):
        xs = ";".join(f"{PX0+s[i,0]*S:.0f}" for s in seq)
        ys = ";".join(f"{PY0+s[i,1]*S:.0f}" for s in seq)
        add(f'<circle r="1.3" opacity="0">'
            f'<animate attributeName="cx" values="{xs}" keyTimes="{KT}" dur="{DUR}" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{ys}" keyTimes="{KT}" dur="{DUR}" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{";".join(trav_op)}" keyTimes="{KT}" dur="{DUR}" repeatCount="indefinite"/>'
            f'</circle>')
    add('</g>')
    add(rows_svg(pal))
    add('</svg>')
    s = "".join(o)
    open(fname, "w").write(s)
    print(fname, f"{len(s)/1024:.0f}KB")

build(DARK, "dark.svg"); build(LIGHT, "light.svg")
