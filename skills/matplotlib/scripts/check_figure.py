# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "matplotlib",
#     "seaborn",
#     "numpy",
#     "pandas",
# ]
# ///
"""Run a chart script and report layout and style problems in its figures.

Measures what is hard to see in a downsized PNG: text that collides with
other text, legends sitting on data, labels running off into a neighbouring
panel, crowded tick labels, unreadably small fonts, and style-invariant drift.

Usage:
    uv run check_figure.py chart.py          # human-readable report
    uv run check_figure.py --json chart.py   # machine-readable

The chart script runs exactly as it would normally (same cwd, same outputs).
Each figure is inspected at the moment it is first saved (or shown).
Exit code is 1 if any ERROR was found, else 0.
"""

import argparse
import json
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import (  # noqa: E402
    LineCollection,
    PathCollection,
    QuadMesh,
)
from matplotlib.colors import to_rgb  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402

# Overlap smaller than this fraction of the smaller box is treated as touching,
# not colliding (antialiasing and font descenders make 1-2 px contact common).
OVERLAP_FRAC = 0.08
# Below ~6.5 pt text is hard to read in print and on a laptop screen at 100%.
MIN_FONT_PT = 6.5
LIGHTGREY = to_rgb("lightgrey")

_inspected = {}  # id(fig) -> report
_saves = {}  # id(fig) -> list of save kwargs


def _short(s, n=40):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _is_colorbar(ax):
    return getattr(ax, "_colorbar", None) is not None or ax.get_label() == "<colorbar>"


def _is_heatmap(ax):
    return any(isinstance(c, QuadMesh) for c in ax.collections) or bool(ax.images)


def _visible_ticklabels(axis):
    lo, hi = sorted(axis.get_view_interval())
    span = (hi - lo) or 1.0
    out = []
    for tick in axis.get_major_ticks():
        loc = tick.get_loc()
        if loc is None or not (lo - 1e-9 * span <= loc <= hi + 1e-9 * span):
            continue
        for lab in (tick.label1, tick.label2):
            if lab.get_visible() and lab.get_text().strip():
                out.append(lab)
    return out


def _collect_texts(fig):
    """Every visible, non-empty text item as (kind, label, Text, axes_index)."""
    items = []
    axes = fig.get_axes()
    if fig._suptitle is not None:
        items.append(("suptitle", fig._suptitle, None))
    for t in fig.texts:
        items.append(("figure text", t, None))
    for i, ax in enumerate(axes):
        if not ax.get_visible():
            continue
        for t in (ax.title, ax._left_title, ax._right_title):
            items.append(("title", t, i))
        items.append(("x label", ax.xaxis.label, i))
        items.append(("y label", ax.yaxis.label, i))
        for t in _visible_ticklabels(ax.xaxis):
            items.append(("x tick", t, i))
        for t in _visible_ticklabels(ax.yaxis):
            items.append(("y tick", t, i))
        if not _is_heatmap(ax):  # heatmap cell labels are meant to sit on cells
            for t in ax.texts:
                items.append(("annotation", t, i))
    seen, out = set(), []
    for k, t, i in items:  # suptitle also lives in fig.texts
        if id(t) not in seen and t.get_visible() and t.get_text().strip():
            seen.add(id(t))
            out.append((k, t, i))
    return out


def _legends(fig):
    out = []
    for i, ax in enumerate(fig.get_axes()):
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            out.append((leg, i))
        for art in ax.artists:  # legends re-added with ax.add_artist()
            if art.__class__.__name__ == "Legend" and art.get_visible():
                out.append((art, i))
    for leg in fig.legends:
        if leg.get_visible():
            out.append((leg, None))
    return out


def _overlap_frac(a, b):
    w = min(a.x1, b.x1) - max(a.x0, b.x0)
    h = min(a.y1, b.y1) - max(a.y0, b.y0)
    if w <= 0 or h <= 0:
        return 0.0
    smaller = min(a.width * a.height, b.width * b.height) or 1.0
    return (w * h) / smaller


def _text_poly(t, box, r):
    """Corners of the text's (possibly rotated) rectangle in display space."""
    rot = t.get_rotation()
    if rot % 90 == 0:
        return np.array(
            [[box.x0, box.y0], [box.x1, box.y0], [box.x1, box.y1], [box.x0, box.y1]]
        )
    t.set_rotation(0)
    flat = Text.get_window_extent(t, r)
    t.set_rotation(rot)
    th = np.radians(rot)
    u = np.array([np.cos(th), np.sin(th)]) * flat.width / 2
    n = np.array([-np.sin(th), np.cos(th)]) * flat.height / 2
    c = np.array([(box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2])
    return np.array([c - u - n, c + u - n, c + u + n, c - u + n])


def _collide(pa, pb, margin):
    """Separating-axis test on two convex quads, each shrunk by `margin` px."""

    def shrink(p):
        c = p.mean(axis=0)
        span = np.linalg.norm(p - c, axis=1, keepdims=True)
        return c + (p - c) * np.clip(1 - margin / np.maximum(span, 1e-9), 0, 1)

    pa, pb = shrink(pa), shrink(pb)
    for poly in (pa, pb):
        for k in range(4):
            edge = poly[(k + 1) % 4] - poly[k]
            axis = np.array([-edge[1], edge[0]])
            a, b = pa @ axis, pb @ axis
            if a.max() <= b.min() or b.max() <= a.min():
                return False
    return True


def _data_points(ax):
    """Display-space points of the data marks on ax (lines, scatter, segments)."""
    pts = []
    for line in ax.lines:
        if not line.get_visible():
            continue
        xy = np.column_stack(line.get_data(orig=False)).astype(float)
        if len(xy) == 0:
            continue
        d = line.get_transform().transform(xy)
        d = d[np.isfinite(d).all(axis=1)]
        if len(d) > 1:  # densify so a legend over a line segment is caught
            t = np.linspace(0, 1, 12)[:, None, None]
            d = (d[:-1] * (1 - t) + d[1:] * t).reshape(-1, 2)
        pts.append(d)
    for coll in ax.collections:
        if not coll.get_visible():
            continue
        if isinstance(coll, PathCollection):
            offs = coll.get_offsets()
            if len(offs):
                pts.append(
                    coll.get_offset_transform().transform(np.asarray(offs, float))
                )
        elif isinstance(coll, LineCollection):
            for seg in coll.get_segments():
                if len(seg) > 1:
                    d = coll.get_transform().transform(np.asarray(seg, float))
                    t = np.linspace(0, 1, 12)[:, None, None]
                    pts.append((d[:-1] * (1 - t) + d[1:] * t).reshape(-1, 2))
    if not pts:
        return np.empty((0, 2))
    allp = np.vstack(pts)
    return allp[np.isfinite(allp).all(axis=1)]


def _bars(ax):
    return [
        p
        for p in ax.patches
        if isinstance(p, Rectangle)
        and p.get_visible()
        and p is not ax.patch
        and p.get_width() != 0
        and p.get_height() != 0
    ]


def _points_in(bbox, pts, shrink=2.0):
    if len(pts) == 0:
        return 0
    x0, x1 = bbox.x0 + shrink, bbox.x1 - shrink
    y0, y1 = bbox.y0 + shrink, bbox.y1 - shrink
    inside = (pts[:, 0] > x0) & (pts[:, 0] < x1) & (pts[:, 1] > y0) & (pts[:, 1] < y1)
    return int(inside.sum())


def inspect(fig):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    issues = []

    def add(sev, msg):
        issues.append({"severity": sev, "message": msg})

    def where(i):
        return f"panel {i}" if i is not None else "figure"

    # --- text vs text ---
    texts = _collect_texts(fig)
    # Text.get_window_extent on an Annotation measures only the label, not the arrow.
    boxes = [(k, t, i, Text.get_window_extent(t, r)) for k, t, i in texts]
    polys = [_text_poly(t, b, r) for _, t, _, b in boxes]
    margin = 1.5 * fig.dpi / 100  # ignore hairline contact from antialiasing
    tick_pairs = {}
    for a in range(len(boxes)):
        ka, ta, ia, ba = boxes[a]
        for b in range(a + 1, len(boxes)):
            kb, tb, ib, bb = boxes[b]
            if ia == ib and {ka, kb} == {"x tick", "y tick"}:
                continue  # the two "0" labels meeting at the origin corner
            if not _collide(polys[a], polys[b], margin):
                continue
            if ka == kb and ka in ("x tick", "y tick") and ia == ib:
                tick_pairs.setdefault((ka, ia), []).append(
                    (ta.get_text(), tb.get_text())
                )
                continue
            add(
                "ERROR",
                f"{ka} '{_short(ta.get_text())}' ({where(ia)}) overlaps "
                f"{kb} '{_short(tb.get_text())}' ({where(ib)})",
            )
    for (kind, i), pairs in tick_pairs.items():
        n_labels = len({x for p in pairs for x in p})
        eg = ", ".join(f"'{_short(x, 15)}'/'{_short(y, 15)}'" for x, y in pairs[:2])
        add(
            "ERROR",
            f"{n_labels} {kind} labels collide in {where(i)} (e.g. {eg}) — "
            "rotate, abbreviate, thin the ticks, or widen the figure",
        )

    # --- legends vs text and data ---
    for leg, i in _legends(fig):
        lb = leg.get_window_extent(r)
        for k, t, ti, tb in boxes:
            if _overlap_frac(lb, tb) > OVERLAP_FRAC:
                add(
                    "ERROR",
                    f"legend ({where(i)}) overlaps {k} '{_short(t.get_text())}'",
                )
        for j, ax in enumerate(fig.get_axes()):
            if not ax.get_visible() or _is_colorbar(ax):
                continue
            n = _points_in(lb, _data_points(ax))
            nbars = sum(
                _overlap_frac(lb, p.get_window_extent(r)) > 0.15 for p in _bars(ax)
            )
            if n or nbars:
                what = f"{n} data points" if n else f"{nbars} bars"
                add(
                    "WARN",
                    f"legend ({where(i)}) covers {what} in {where(j)} — move it "
                    "to an empty region or outside the axes",
                )

    # --- annotations vs data, and annotations spilling into another panel ---
    axes = fig.get_axes()
    for k, t, i, tb in boxes:
        if k != "annotation":
            continue
        ax = axes[i]
        n = _points_in(tb, _data_points(ax))
        if n:
            add(
                "WARN",
                f"annotation '{_short(t.get_text())}' sits on {n} data points "
                f"in {where(i)} — offset it or use ax.annotate() with an arrow",
            )
        for j, other in enumerate(axes):
            if j != i and other.get_visible() and not _is_colorbar(other):
                if _overlap_frac(tb, other.get_window_extent(r)) > 0.3:
                    add(
                        "ERROR",
                        f"annotation '{_short(t.get_text())}' from {where(i)} "
                        f"spills into {where(j)}",
                    )

    # --- panels overlapping each other ---
    vis = [
        (j, a) for j, a in enumerate(axes) if a.get_visible() and not _is_colorbar(a)
    ]
    for x in range(len(vis)):
        for y in range(x + 1, len(vis)):
            (ja, a), (jb, b) = vis[x], vis[y]
            if _overlap_frac(a.get_window_extent(r), b.get_window_extent(r)) > 0.05:
                add(
                    "WARN",
                    f"panel {ja} and panel {jb} overlap (inset axes are fine; "
                    "otherwise fix the layout)",
                )

    # --- readability ---
    small = sorted(
        {
            round(t.get_fontsize(), 1)
            for _, t, _, _ in boxes
            if t.get_fontsize() < MIN_FONT_PT
        }
    )
    if small:
        add("WARN", f"text at {small} pt is below {MIN_FONT_PT} pt — hard to read")
    for j, ax in vis:
        has_content = ax.lines or ax.collections or _bars(ax) or ax.images or ax.texts
        if not has_content:
            add(
                "WARN",
                f"panel {j} is visible but empty — hide it with ax.set_visible(False)",
            )

    # --- style invariants (style-reference.md) ---
    for j, ax in vis:
        spines = [n for n, s in ax.spines.items() if s.get_visible()]
        if spines:
            add(
                "STYLE",
                f"panel {j}: visible spines {spines} — "
                "call sns.despine(left=True, bottom=True)",
            )
        ticks = ax.xaxis.get_major_ticks()[:1] + ax.yaxis.get_major_ticks()[:1]
        if any(
            tk.tick1line.get_visible() and tk.tick1line.get_markersize() > 0
            for tk in ticks
        ):
            add("STYLE", f"panel {j}: tick marks visible — tick_params(length=0)")
    fonts = {t.get_fontname() for _, t, _, _ in boxes}
    if fonts - {"DejaVu Sans", "STIXGeneral", "DejaVu Sans Mono", "cmr10"}:
        add("STYLE", f"fonts {sorted(fonts)} — expected DejaVu Sans")
    for leg, i in _legends(fig):
        frame = leg.get_frame()
        if not leg.get_frame_on():
            add("STYLE", f"legend ({where(i)}) has no frame — frameon=True")
        elif np.abs(np.array(frame.get_edgecolor()[:3]) - LIGHTGREY).max() > 0.05:
            add("STYLE", f"legend ({where(i)}) edgecolor is not lightgrey")

    w, h = fig.get_size_inches()
    return {"size_in": [round(w, 2), round(h, 2)], "n_axes": len(vis), "issues": issues}


def _check_saves(fig_id):
    out = []
    saves = _saves.get(fig_id, [])
    exts = sorted({Path(str(s["fname"])).suffix.lstrip(".").lower() for s in saves})
    dpis = sorted({s.get("dpi") for s in saves}, key=str)
    if saves and any(s.get("bbox_inches") != "tight" for s in saves):
        out.append(
            {"severity": "STYLE", "message": "savefig without bbox_inches='tight'"}
        )
    if saves and not set(dpis) <= {150, 300}:
        out.append(
            {
                "severity": "STYLE",
                "message": f"savefig dpi {dpis} — use 150 (300 for publication)",
            }
        )
    return exts, dpis, out


_orig_savefig = Figure.savefig
_orig_show = plt.show


def _savefig(self, fname, *args, **kwargs):
    if id(self) not in _inspected:
        _inspected[id(self)] = inspect(self)
        _inspected[id(self)]["fig"] = self
    _saves.setdefault(id(self), []).append({"fname": fname, **kwargs})
    return _orig_savefig(self, fname, *args, **kwargs)


def _show(*args, **kwargs):
    for num in plt.get_fignums():
        fig = plt.figure(num)
        if id(fig) not in _inspected:
            _inspected[id(fig)] = inspect(fig)
            _inspected[id(fig)]["fig"] = fig


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("script")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    Figure.savefig = _savefig
    plt.show = _show
    script = Path(args.script).resolve()
    sys.argv = [str(script)]
    sys.path.insert(0, str(script.parent))
    run_error = None
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit:
        pass
    except Exception as e:  # report instead of crashing the checker
        run_error = f"{type(e).__name__}: {e}"
    _show()  # inspect any figure that was never saved

    reports = []
    for fid, rep in _inspected.items():
        fig = rep.pop("fig")
        exts, dpis, save_issues = _check_saves(fid)
        rep["issues"].extend(save_issues)
        names = sorted({Path(str(s["fname"])).name for s in _saves.get(fid, [])})
        rep.update({"saved_as": names, "formats": exts, "dpi": dpis})
        reports.append(rep)
        plt.close(fig)

    n_err = sum(i["severity"] == "ERROR" for r in reports for i in r["issues"])
    result = {
        "script": script.name,
        "run_error": run_error,
        "figures": reports,
        "issues": [i for r in reports for i in r["issues"]],
        "errors": n_err,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if run_error:
            print(f"Script failed: {run_error}")
        if not reports:
            print("No figures were created.")
        for rep in reports:
            name = ", ".join(rep["saved_as"]) or "(unsaved figure)"
            print(
                f"{name}  {rep['size_in'][0]}x{rep['size_in'][1]} in, "
                f"{rep['n_axes']} panel(s), dpi={rep['dpi']}"
            )
            if not rep["issues"]:
                print("  OK — no overlaps, collisions, or style drift found")
            for i in rep["issues"]:
                print(f"  {i['severity']:<5} {i['message']}")
    sys.exit(1 if (n_err or run_error) else 0)


if __name__ == "__main__":
    main()
