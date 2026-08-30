# Banner source

Generates `dark.svg` / `light.svg` in the repo root — the animated terminal banner
at the top of the profile README.

The `.npy` files are the source of truth, not the SVG. Edit the scripts, re-run,
never hand-edit the generated SVG.

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python pillow numpy scipy
```

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1. Segment the photo from its background | `seg2.py`, `clean.py` | `crop_fg.npy` |
| 2. Dither the portrait to a 300x340 grid | `portrait.py` | `light.npy` |
| 3. Rasterise the morph targets | `logos.py`, `logos_fix.py`, `code_fix.py`, `logos2.py` | `logo_*.npy` |
| 4. Assemble the SVG | `build_svg.py` (+ `panel.py`) | `dark.svg`, `light.svg` |

Only step 4 needs re-running for text or colour changes:

```bash
.venv/bin/python build_svg.py
```

Steps 1-2 need the original photo, which is not committed.

## Editing

- **Panel rows** — `panel.py`, the `ROWS` list. Dotted leaders are computed from
  label/value length; never hand-edit them.
- **Colours** — `build_svg.py`, the `DARK` / `LIGHT` dicts.
- **Timing** — `build_svg.py`, `PORTRAIT_HOLD` / `LOGO_HOLD` / `TRANS`. keyTimes must
  stay uneven, otherwise every phase is forced to the same length.
- **Logos** — the `LOGOS` tuple picks which `logo_*.npy` the swarm morphs through,
  and in what order.

## Checks worth keeping

Verify by measurement, not by eye — cairosvg renders only the first SMIL frame.

- Intro groups must scatter across the whole portrait (evenness ~1.0), not by region.
- Drift bands must not quantise into a square grid (straight-boundary ~0.0).
- File size lands ~1.1MB. Warn before changes that grow it.
