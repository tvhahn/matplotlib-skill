# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "matplotlib",
#     "seaborn",
#     "numpy",
#     "pandas",
# ]
# ///
"""Run a chart script and report layout, honesty, and style problems in its figures.

Measures what is hard to see in a downsized PNG: text that collides with
other text, legends sitting on data, labels running off into a neighbouring
panel, crowded tick labels, unreadably small fonts, misleading encodings
(truncated bars, dual axes, inverted axes, rainbow colormaps), colour pairs
that collapse under colour-vision deficiency, low-contrast text and lines,
and drift from the house style (dimgrey text, footers, mathtext dollars).

Usage:
    uv run check_figure.py chart.py            # human-readable report
    uv run check_figure.py --json chart.py     # machine-readable
    uv run check_figure.py --strict chart.py   # WARN also fails (exit 1)

The chart script runs exactly as it would normally (same cwd, same outputs).
Each figure is inspected at the moment it is first saved (or shown).
Exit code is 1 if any ERROR was found (or any WARN with --strict), else 0.

Every issue has a severity (ERROR, WARN, STYLE, INFO), a stable short `code`
(e.g. "bar-not-at-zero", "cvd-collision"), and a message with a fix hint.

Colour distances are Euclidean distances in OKLab x 100 (a JND is roughly 2;
below 8 two thin marks are hard to tell apart). Colour-vision deficiency is
simulated with the Machado, Oliveira & Fernandes (2009) severity-1.0 matrices
for deuteranopia and protanopia, applied in linear sRGB.
"""

import argparse
import json
import re
import runpy
import sys
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as patheffects  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import (  # noqa: E402
    LineCollection,
    PathCollection,
    PolyCollection,
    QuadMesh,
)
from matplotlib.colors import (  # noqa: E402
    CenteredNorm,
    LogNorm,
    SymLogNorm,
    TwoSlopeNorm,
    to_hex,
    to_rgb,
    to_rgba,
    to_rgba_array,
)
from matplotlib.container import BarContainer  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402

# Overlap smaller than this fraction of the smaller box is treated as touching,
# not colliding (antialiasing and font descenders make 1-2 px contact common).
OVERLAP_FRAC = 0.08
# Below ~6.5 pt text is hard to read in print and on a laptop screen at 100%.
MIN_FONT_PT = 6.5
LIGHTGREY = to_rgb("lightgrey")
DIMGREY = to_rgb("dimgrey")  # #696969
ACCENT_RED = to_rgb("#bd0c0c")
WHITE = (1.0, 1.0, 1.0)

# Two series whose colours are closer than this (OKLab x 100) under simulated
# deuteranopia or protanopia, with no second encoding, are flagged.
CVD_DE_MIN = 8.0
# Greyscale (lightness-only) similarity below this (OKLab L x 100) -> INFO.
GREY_DL_MIN = 8.0
# WCAG 2.1 contrast floors: 3:1 for (large/graphical) text, 2:1 for thin lines.
TEXT_CONTRAST_MIN = 3.0
LINE_CONTRAST_MIN = 2.0
THIN_LW = 1.5
# More free-standing annotations than this in one panel dilutes the message.
MAX_ANNOTATIONS = 3
# Text this close to a mark (fraction of the panel diagonal) is "at" the mark.
NEAR_FRAC = 0.04

RAINBOW_CMAPS = {"jet", "rainbow", "hsv", "gist_rainbow", "nipy_spectral", "gist_ncar"}
DIVERGING_CMAPS = {
    "rdbu", "coolwarm", "bwr", "rdylbu", "puor", "brbg", "piyg", "prgn",
    "seismic", "spectral", "rdylgn", "rdgy", "vlag", "icefire",
}  # fmt: skip

_inspected = {}  # id(fig) -> report
_saves = {}  # id(fig) -> list of save kwargs


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


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


def _densify(d, n=12):
    if len(d) < 2:
        return d
    t = np.linspace(0, 1, n)[:, None, None]
    return (d[:-1] * (1 - t) + d[1:] * t).reshape(-1, 2)


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
        pts.append(_densify(d))  # so a legend over a line segment is caught
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
                    pts.append(_densify(d))
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


# --------------------------------------------------------------------------
# Colour science (no extra dependencies)
# --------------------------------------------------------------------------

# Machado, Oliveira & Fernandes (2009), severity 1.0, linear-sRGB matrices.
_MACHADO = {
    "deuteranopia": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ]
    ),
    "protanopia": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    ),
}
_OK_M1 = np.array(
    [
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ]
)
_OK_M2 = np.array(
    [
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ]
)


def _linear(rgb):
    c = np.clip(np.asarray(rgb, float), 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _oklab_from_linear(lin):
    return _OK_M2 @ np.cbrt(_OK_M1 @ lin)


def _oklab(rgb):
    return _oklab_from_linear(_linear(rgb))


def _cvd_distances(a, b):
    """OKLab x 100 distance between two sRGB colours: normal, deutan, protan."""
    la, lb = _linear(a), _linear(b)

    def de(x, y):
        diff = _oklab_from_linear(x) - _oklab_from_linear(y)
        return 100 * float(np.linalg.norm(diff))

    out = {"normal": de(la, lb)}
    for name, m in _MACHADO.items():
        out[name] = de(np.clip(m @ la, 0, 1), np.clip(m @ lb, 0, 1))
    return out


def _rel_luminance(rgb):
    return float(np.dot([0.2126, 0.7152, 0.0722], _linear(rgb)))


def _contrast(a, b):
    la, lb = sorted((_rel_luminance(a), _rel_luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _blend(rgba, bg=WHITE):
    r, g, b, a = to_rgba(rgba)
    return tuple(np.array([r, g, b]) * a + np.array(bg[:3]) * (1 - a))


def _chroma(rgb):
    lab = _oklab(rgb)
    return float(np.hypot(lab[1], lab[2]))


def _same_colour(a, b, tol=0.03):
    return float(np.abs(np.array(a[:3]) - np.array(b[:3])).max()) <= tol


def _hex(rgb):
    return to_hex(rgb[:3])


def _norm_marker(m):
    return None if m in (None, "None", "none", "", " ", ",") else str(m)


def _norm_ls(ls):
    return None if ls in (None, "None", "none", "", " ") else str(ls)


def _is_data_tr(tr, ax):
    """True when both x and y of an artist transform go through ax.transData."""
    try:
        bx, by = tr.contains_branch_seperately(ax.transData)
        return bool(bx and by)
    except Exception:  # noqa: BLE001
        return True


# --------------------------------------------------------------------------
# Series extraction (for colour-vision and contrast checks)
# --------------------------------------------------------------------------


def _path_key(path):
    v = np.round(np.asarray(path.vertices, float), 3)
    return "path:" + str(hash(v.tobytes()))


def _series(ax):
    """Distinct data series on ax as dicts (kind, rgb, marker, ls, pts, lw, ...).

    Excluded: reference lines (axhline/axvline), short segments without
    markers (error bars, connectors), supporting marks (achromatic with
    alpha <= 0.5), faint background layers (alpha < 0.35), white halos, and
    single-container bar charts (where position already identifies bars).
    """
    bg = to_rgb(ax.get_facecolor())
    raw = []
    for line in ax.lines:
        if not line.get_visible() or not _is_data_tr(line.get_transform(), ax):
            continue
        xy = np.column_stack(line.get_data(orig=False)).astype(float)
        xy = xy[np.isfinite(xy).all(axis=1)] if len(xy) else xy
        marker, ls = _norm_marker(line.get_marker()), _norm_ls(line.get_linestyle())
        if len(xy) == 0 or (marker is None and (ls is None or len(xy) <= 2)):
            continue
        rgba = to_rgba(line.get_color())
        alpha = line.get_alpha()
        alpha = rgba[3] if alpha is None else alpha
        d = line.get_transform().transform(xy)
        raw.append(
            dict(
                kind="line",
                rgba=(*rgba[:3], alpha),
                marker=marker,
                ls=ls,
                lw=line.get_linewidth() if ls else None,
                pts=_densify(d),
                ends=np.array([d[0], d[-1]]),
                label=line.get_label(),
                artist=line,
            )
        )
    for coll in ax.collections:
        if not isinstance(coll, PathCollection) or not coll.get_visible():
            continue
        offs = np.asarray(coll.get_offsets(), float)
        if not len(offs) or coll.get_array() is not None:
            continue  # colormapped scatter: colour encodes a value, not a series
        if not _is_data_tr(coll.get_offset_transform(), ax):
            continue
        fcs = np.asarray(coll.get_facecolor(), float)
        if not len(fcs) or (fcs[:, 3] == 0).all():
            continue  # hollow rings: highlight marks, not a series
        fcs = np.broadcast_to(fcs, (len(offs), 4)) if len(fcs) == 1 else fcs
        if len(fcs) != len(offs):
            continue
        paths = coll.get_paths()
        if len(paths) == len(offs) and len(paths) > 1:
            pkeys = [_path_key(p) for p in paths]
        else:
            pkeys = [_path_key(paths[0]) if paths else "path:none"] * len(offs)
        d = coll.get_offset_transform().transform(offs)
        groups = {}
        for k in range(len(offs)):
            key = (tuple(np.round(fcs[k], 3)), pkeys[k])
            groups.setdefault(key, []).append(k)
        if len(groups) > 12:
            continue  # continuous colouring without a colormap array
        for (rgba, pk), idx in groups.items():
            raw.append(
                dict(
                    kind="scatter",
                    rgba=rgba,
                    marker=pk,
                    ls=None,
                    lw=None,
                    pts=d[idx],
                    ends=d[idx],
                    label=coll.get_label(),
                    artist=coll,
                )
            )
    containers = [
        c for c in ax.containers if isinstance(c, BarContainer) and len(c.patches)
    ]
    if len(containers) > 1:
        for c in containers:
            fcs = {tuple(np.round(p.get_facecolor(), 3)) for p in c.patches}
            if len(fcs) != 1:
                continue
            ends = []
            for p in c.patches:
                x, y, w, h = p.get_x(), p.get_y(), p.get_width(), p.get_height()
                if getattr(c, "orientation", "vertical") == "horizontal":
                    ends.append((x + w, y + h / 2))
                else:
                    ends.append((x + w / 2, y + h))
            d = ax.transData.transform(np.array(ends, float))
            hatch = c.patches[0].get_hatch()
            raw.append(
                dict(
                    kind="bar",
                    rgba=next(iter(fcs)),
                    marker=f"bar:{hatch}",
                    ls=None,
                    lw=None,
                    pts=d,
                    ends=d,
                    label=c.get_label(),
                    artist=c,
                )
            )
    out = []
    for s in raw:
        alpha = s["rgba"][3]
        rgb = _blend(s["rgba"], bg)
        if alpha < 0.35:
            continue  # faint background layer (decision regions, density clouds)
        if _chroma(s["rgba"][:3]) < 0.02 and alpha <= 0.5:
            continue  # supporting grey marks
        if _rel_luminance(s["rgba"][:3]) > 0.95 and _chroma(s["rgba"][:3]) < 0.02:
            continue  # white halo / casing
        pts = s["pts"]
        pts = pts[np.isfinite(pts).all(axis=1)]
        if len(pts) > 4000:
            pts = pts[np.linspace(0, len(pts) - 1, 4000).astype(int)]
        s.update(rgb=rgb, pts=pts)
        out.append(s)
    # merge artists that share colour + marker + linestyle into one series
    merged = []
    for s in out:
        for m in merged:
            if (
                m["kind"] == s["kind"]
                and _same_colour(m["rgb"], s["rgb"], 0.004)
                and m["marker"] == s["marker"]
                and m["ls"] == s["ls"]
            ):
                m["pts"] = np.vstack([m["pts"], s["pts"]])
                m["ends"] = np.vstack([m["ends"], s["ends"]])
                break
        else:
            merged.append(dict(s))
    return merged


def _bbox_dist(bb, pts):
    """Minimum display distance from bbox to any of pts (0 if inside)."""
    if len(pts) == 0:
        return np.inf
    dx = np.maximum(np.maximum(bb.x0 - pts[:, 0], 0), pts[:, 0] - bb.x1)
    dy = np.maximum(np.maximum(bb.y0 - pts[:, 1], 0), pts[:, 1] - bb.y1)
    return float(np.hypot(dx, dy).min())


def _anchor(t):
    """Display position an Annotation points at (its xy), else None."""
    if hasattr(t, "xy") and hasattr(t, "_get_xy_display"):
        try:
            return np.array(t._get_xy_display(), float)
        except Exception:  # noqa: BLE001
            return None
    return None


def _text_mark_dist(t, bb, pts):
    d = _bbox_dist(bb, pts)
    a = _anchor(t)
    if a is not None and len(pts) and np.isfinite(a).all():
        d = min(d, float(np.hypot(*(pts - a).T).min()))
    return d


# --------------------------------------------------------------------------
# Text inventory for the new checks (includes legend and heatmap-axes text)
# --------------------------------------------------------------------------


def _all_texts(fig, r):
    """Every visible text as (kind, Text, axes_index, bbox).

    Kinds: suptitle, figure text, sup label, title, x label, y label, x tick,
    y tick, annotation, cell label (text on a heatmap cell), legend text,
    legend title.
    """
    items = []
    sup_labels = {id(getattr(fig, n, None)) for n in ("_supxlabel", "_supylabel")}
    if fig._suptitle is not None:
        items.append(("suptitle", fig._suptitle, None))
    for t in fig.texts:
        items.append(("sup label" if id(t) in sup_labels else "figure text", t, None))
    for i, ax in enumerate(fig.get_axes()):
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
        heat = _is_heatmap(ax)
        abox = ax.get_window_extent(r)
        for t in ax.texts:
            kind = "annotation"
            if heat:
                bb = Text.get_window_extent(t, r)
                cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
                if abox.x0 <= cx <= abox.x1 and abox.y0 <= cy <= abox.y1:
                    kind = "cell label"
            items.append((kind, t, i))
    for leg, i in _legends(fig):
        for t in leg.get_texts():
            items.append(("legend text", t, i))
        items.append(("legend title", leg.get_title(), i))
    seen, out = set(), []
    for k, t, i in items:
        if id(t) in seen or not t.get_visible() or not t.get_text().strip():
            continue
        seen.add(id(t))
        out.append((k, t, i, Text.get_window_extent(t, r)))
    return out


def _data_colours(fig):
    """Colours used by data marks anywhere in the figure (for direct labels)."""
    cols = []

    def add(c):
        try:
            rgba = to_rgba(c)
        except (ValueError, TypeError):
            return
        if rgba[3] > 0 and not any(_same_colour(rgba, x, 0.004) for x in cols):
            cols.append(rgba[:3])

    for ax in fig.get_axes():
        for line in ax.lines:
            add(line.get_color())
            add(line.get_markerfacecolor())
        for coll in ax.collections:
            for arr in (coll.get_facecolor(), coll.get_edgecolor()):
                arr = np.atleast_2d(np.asarray(arr, float))
                for c in arr[:50] if arr.size else []:
                    add(tuple(c))
        for p in ax.patches:
            if p is not ax.patch:
                add(p.get_facecolor())
                add(p.get_edgecolor())
    for leg in [lg for lg, _ in _legends(fig)]:
        for h in getattr(leg, "legend_handles", []) or []:
            for getter in ("get_color", "get_facecolor", "get_markerfacecolor"):
                fn = getattr(h, getter, None)
                if fn is None:
                    continue
                try:
                    v = fn()
                except Exception:  # noqa: BLE001
                    continue
                arr = np.atleast_2d(np.asarray(_to_rgba_array(v), float))
                for c in arr[:10]:
                    add(tuple(c))
    return cols


def _hue_chroma(rgb):
    _, a, b = _oklab(rgb)
    return float(np.degrees(np.arctan2(b, a))), float(np.hypot(a, b))


def _matches_series(rgb, data_cols, hue_tol=15.0):
    """True if rgb is a data colour, or a darker/lighter shade of one.

    Shades keep the OKLCh hue (within `hue_tol` degrees); both colours must be
    chromatic, so grey text never matches a coloured series by hue alone.
    """
    if any(_same_colour(rgb, c, 0.02) for c in data_cols):
        return True
    h, ch = _hue_chroma(rgb)
    if ch < 0.03:
        return False
    for c in data_cols:
        hc, cc = _hue_chroma(c)
        if cc >= 0.03 and abs((h - hc + 180) % 360 - 180) <= hue_tol:
            return True
    return False


def _to_rgba_array(v):
    try:
        return to_rgba_array(v)
    except (ValueError, TypeError):
        return np.empty((0, 4))


_NUMERIC_RE = re.compile(r"^[+\-−–]?\(?[\d.,]+\)?(?:[kKMB]|bn|x|×)?$")


def _is_numeric_label(s):
    s = s.replace("\\$", "").replace("$", "").replace("€", "").replace("£", "")
    s = s.replace("%", "").replace(" ", "").replace("\u2009", "")
    return bool(s) and any(ch.isdigit() for ch in s) and bool(_NUMERIC_RE.match(s))


# --------------------------------------------------------------------------
# Mathtext dollar heuristics
# --------------------------------------------------------------------------

_UNESCAPED_DOLLAR = re.compile(r"(?<!\\)\$")
_TEX_CMD = re.compile(r"\\[A-Za-z]+(\{[^}]*\})?")
_SUBSUP = re.compile(r"[_^](\{[^}]*\}|\w)")
_PROSE_WORD = re.compile(r"(?<![\\\w])[A-Za-z]{2,}(?!\w)")


def _currency_math(s):
    """Return the offending math segment if `s` looks like prose with two '$'."""
    if len(_UNESCAPED_DOLLAR.findall(s)) < 2 or len(_UNESCAPED_DOLLAR.findall(s)) % 2:
        return None  # matplotlib only switches to mathtext on an even count
    parts = _UNESCAPED_DOLLAR.split(s)
    for seg in parts[1::2]:
        stripped = _SUBSUP.sub(" ", _TEX_CMD.sub(" ", seg))
        words = _PROSE_WORD.findall(stripped)
        starts_num = bool(re.match(r"\s*[\d.,]", seg))
        if starts_num and (seg[-1:].isspace() or words):
            return seg
        if len(words) >= 2:
            return seg
    return None


# --------------------------------------------------------------------------
# Axis helpers
# --------------------------------------------------------------------------


def _is_categorical(axis):
    from matplotlib.ticker import FixedFormatter

    if axis.get_units().__class__.__name__ == "UnitData":
        return True
    conv = getattr(axis, "get_converter", lambda: getattr(axis, "converter", None))()
    if conv is not None and "Category" in conv.__class__.__name__:
        return True
    if isinstance(axis.get_major_formatter(), FixedFormatter):
        return True
    labels = [t.get_text() for t in _visible_ticklabels(axis)]
    for s in labels:
        s2 = s.replace("−", "-").replace(",", "").replace("%", "").replace("$", "")
        try:
            float(s2)
        except ValueError:
            return True
    return False


def _is_date_axis(axis):
    fmt = axis.get_major_formatter().__class__.__name__
    return "Date" in fmt


def _axis_values(ax, which):
    """Plotted data values along x (which=0) or y (which=1), in data units."""
    vals = []
    for line in ax.lines:
        if not line.get_visible():
            continue
        try:
            br = line.get_transform().contains_branch_seperately(ax.transData)
        except Exception:  # noqa: BLE001
            br = (True, True)
        if not br[which]:
            continue
        v = np.asarray(line.get_data(orig=False)[which], float)
        vals.append(v)
    for coll in ax.collections:
        if isinstance(coll, PathCollection) and coll.get_visible():
            try:
                tr = coll.get_offset_transform()
                br = tr.contains_branch_seperately(ax.transData)
            except Exception:  # noqa: BLE001
                br = (True, True)
            offs = np.asarray(coll.get_offsets(), float)
            if br[which] and len(offs):
                vals.append(offs[:, which])
        elif isinstance(coll, PolyCollection) and coll.get_visible():
            for p in coll.get_paths():
                vals.append(np.asarray(p.vertices, float)[:, which])
    for c in ax.containers:
        if not isinstance(c, BarContainer):
            continue
        horiz = getattr(c, "orientation", "vertical") == "horizontal"
        for p in c.patches:
            x, y, w, h = p.get_x(), p.get_y(), p.get_width(), p.get_height()
            if (which == 0) != horiz:  # position axis: bar centre
                vals.append(np.array([x + w / 2] if which == 0 else [y + h / 2]))
            else:  # value axis: base and end
                vals.append(np.array([x, x + w] if which == 0 else [y, y + h]))
    if not vals:
        return np.empty(0)
    v = np.concatenate([np.ravel(a) for a in vals]).astype(float)
    return v[np.isfinite(v)]


def _in_view(v, lo, hi, tol):
    return lo - tol <= v <= hi + tol


# --------------------------------------------------------------------------
# The checks
# --------------------------------------------------------------------------


def inspect(fig):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    issues = []

    def add(sev, code, msg):
        issues.append({"severity": sev, "code": code, "message": msg})

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
                "text-overlap",
                f"{ka} '{_short(ta.get_text())}' ({where(ia)}) overlaps "
                f"{kb} '{_short(tb.get_text())}' ({where(ib)})",
            )
    for (kind, i), pairs in tick_pairs.items():
        n_labels = len({x for p in pairs for x in p})
        eg = ", ".join(f"'{_short(x, 15)}'/'{_short(y, 15)}'" for x, y in pairs[:2])
        add(
            "ERROR",
            "tick-collision",
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
                    "legend-overlaps-text",
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
                    "legend-on-data",
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
        if n and _has_halo(t):
            add(
                "INFO",
                "annotation-on-data",
                f"annotation '{_short(t.get_text())}' sits on {n} data points "
                f"in {where(i)} but is haloed — readable over data",
            )
        elif n:
            add(
                "WARN",
                "annotation-on-data",
                f"annotation '{_short(t.get_text())}' sits on {n} data points "
                f"in {where(i)} — offset it, use ax.annotate() with an arrow, "
                "or add a white halo (style-reference Craft)",
            )
        for j, other in enumerate(axes):
            if j != i and other.get_visible() and not _is_colorbar(other):
                if _overlap_frac(tb, other.get_window_extent(r)) > 0.3:
                    add(
                        "ERROR",
                        "annotation-spill",
                        f"annotation '{_short(t.get_text())}' from {where(i)} "
                        f"spills into {where(j)}",
                    )

    # --- panels overlapping each other (twinned axes are reported as dual-axis) ---
    vis = [
        (j, a) for j, a in enumerate(axes) if a.get_visible() and not _is_colorbar(a)
    ]
    twins = set()
    for x in range(len(vis)):
        for y in range(x + 1, len(vis)):
            (ja, a), (jb, b) = vis[x], vis[y]
            if _is_twin(a, b):
                twins.add((ja, jb))
                continue
            if _overlap_frac(a.get_window_extent(r), b.get_window_extent(r)) > 0.05:
                add(
                    "WARN",
                    "panel-overlap",
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
        add(
            "WARN",
            "tiny-text",
            f"text at {small} pt is below {MIN_FONT_PT} pt — hard to read",
        )
    for j, ax in vis:
        has_content = ax.lines or ax.collections or _bars(ax) or ax.images or ax.texts
        if not has_content:
            add(
                "WARN",
                "empty-panel",
                f"panel {j} is visible but empty — hide it with ax.set_visible(False)",
            )

    # --- style invariants (style-reference.md) ---
    for j, ax in vis:
        spines = [n for n, s in ax.spines.items() if s.get_visible()]
        if spines:
            add(
                "STYLE",
                "spines",
                f"panel {j}: visible spines {spines} — "
                "call sns.despine(left=True, bottom=True)",
            )
        ticks = ax.xaxis.get_major_ticks()[:1] + ax.yaxis.get_major_ticks()[:1]
        if any(
            tk.tick1line.get_visible() and tk.tick1line.get_markersize() > 0
            for tk in ticks
        ):
            add(
                "STYLE",
                "tick-marks",
                f"panel {j}: tick marks visible — tick_params(length=0)",
            )
    fonts = {t.get_fontname() for _, t, _, _ in boxes}
    if fonts - {"DejaVu Sans", "STIXGeneral", "DejaVu Sans Mono", "cmr10"}:
        add("STYLE", "font", f"fonts {sorted(fonts)} — expected DejaVu Sans")
    for leg, i in _legends(fig):
        frame = leg.get_frame()
        if not leg.get_frame_on():
            add(
                "STYLE",
                "legend-no-frame",
                f"legend ({where(i)}) has no frame — frameon=True",
            )
        elif np.abs(np.array(frame.get_edgecolor()[:3]) - LIGHTGREY).max() > 0.05:
            add(
                "STYLE",
                "legend-edgecolor",
                f"legend ({where(i)}) edgecolor is not lightgrey",
            )

    # --- new checks: each guarded so one odd artist cannot crash the checker ---
    all_texts = _all_texts(fig, r)
    ctx = dict(fig=fig, r=r, vis=vis, twins=twins, texts=all_texts, add=add)
    for check in (
        _check_bars_at_zero,
        _check_areas_at_zero,
        _check_dual_axes,
        _check_inverted,
        _check_fractional_ticks,
        _check_colormaps,
        _check_series_colours,
        _check_text_contrast,
        _check_text_colour,
        _check_footer,
        _check_mathtext_dollar,
        _check_annotation_count,
    ):
        try:
            check(ctx)
        except Exception as e:  # noqa: BLE001
            add("INFO", "checker-error", f"{check.__name__} skipped: {e!r}")

    w, h = fig.get_size_inches()
    return {"size_in": [round(w, 2), round(h, 2)], "n_axes": len(vis), "issues": issues}


def _has_halo(t):
    """True if the text has a white(ish) withStroke halo of linewidth >= 2."""
    for eff in t.get_path_effects() or []:
        if not isinstance(eff, patheffects.Stroke):
            continue
        gc = getattr(eff, "_gc", {}) or {}
        lw = gc.get("linewidth", gc.get("lw", 0)) or 0
        fg = gc.get("foreground", gc.get("color"))
        try:
            light = fg is not None and _rel_luminance(to_rgb(fg)) > 0.85
        except (ValueError, TypeError):
            light = False
        if lw >= 2 and light:
            return True
    return False


def _is_twin(a, b):
    tw = getattr(a, "_twinned_axes", None)
    try:
        if tw is not None and tw.joined(a, b):
            return True
    except Exception:  # noqa: BLE001
        pass
    return False


def _has_data(ax):
    return bool(
        [ln for ln in ax.lines if _is_data_tr(ln.get_transform(), ax)]
        or ax.collections
        or _bars(ax)
        or ax.images
    )


# 1. Bars and areas must start at zero (proportional ink).


def _check_bars_at_zero(ctx):
    for j, ax in ctx["vis"]:
        flagged = set()
        for c in ax.containers:
            if not isinstance(c, BarContainer) or not len(c.patches):
                continue
            horiz = getattr(c, "orientation", "vertical") == "horizontal"
            axis = ax.xaxis if horiz else ax.yaxis
            if axis.get_scale() != "linear" or horiz in flagged:
                continue
            lo, hi = sorted(axis.get_view_interval())
            tol = 1e-3 * ((hi - lo) or 1.0)
            n_cut = 0
            for p in c.patches:
                if not p.get_visible() or p.get_width() == 0 or p.get_height() == 0:
                    continue
                if horiz:
                    base, end = p.get_x(), p.get_x() + p.get_width()
                else:
                    base, end = p.get_y(), p.get_y() + p.get_height()
                if not np.isfinite([base, end]).all():
                    continue
                visible = not (max(base, end) < lo - tol or min(base, end) > hi + tol)
                if visible and not _in_view(base, lo, hi, tol):
                    n_cut += 1
            if n_cut:
                flagged.add(horiz)
                name = "x" if horiz else "y"
                ctx["add"](
                    "ERROR",
                    "bar-not-at-zero",
                    f"panel {j}: {n_cut} bar(s) start outside the {name} axis "
                    f"({lo:g} to {hi:g}) — bar length must be proportional to "
                    f"value; let the {name} axis include 0 (remove set_{name}lim) "
                    "or use dots/lines, which may start anywhere",
                )


def _flat_edge(vals):
    """Value shared by a large share of polygon vertices (an area's baseline)."""
    v = np.round(vals[np.isfinite(vals)], 10)
    if len(v) < 6:
        return None
    u, n = np.unique(v, return_counts=True)
    k = n.argmax()
    if n[k] >= max(3, 0.3 * len(v)):
        return float(u[k])
    return None


def _offset_rows(ax):
    """Ridgeline / joyplot: several fills, each on its own flat baseline."""
    bases = set()
    for coll in ax.collections:
        if isinstance(coll, PolyCollection) and not isinstance(coll, QuadMesh):
            for path in coll.get_paths():
                b = _flat_edge(np.asarray(path.vertices, float)[:, 1])
                if b is not None:
                    bases.add(round(b, 6))
    return len(bases) >= 3


def _check_areas_at_zero(ctx):
    for j, ax in ctx["vis"]:
        if _is_heatmap(ax) or _offset_rows(ax):
            continue  # ridgeline rows sit on offset baselines by design
        for coll in ax.collections:
            if not isinstance(coll, PolyCollection) or not coll.get_visible():
                continue
            if isinstance(coll, QuadMesh):
                continue
            tdir = getattr(coll, "t_direction", None)
            dims = [1] if tdir == "x" else [0] if tdir == "y" else [1, 0]
            done = False
            for dim in dims:
                axis = ax.yaxis if dim == 1 else ax.xaxis
                if axis.get_scale() != "linear" or _is_categorical(axis):
                    continue
                lo, hi = sorted(axis.get_view_interval())
                span = (hi - lo) or 1.0
                tol = 1e-3 * span
                for path in coll.get_paths():
                    b = _flat_edge(np.asarray(path.vertices, float)[:, dim])
                    if b is None:
                        continue
                    zero_in = _in_view(0.0, lo, hi, tol)
                    at_edge = min(abs(b - lo), abs(b - hi)) <= 0.06 * span
                    if not _in_view(b, lo, hi, tol) or (
                        at_edge and abs(b) > tol and not zero_in
                    ):
                        name = "y" if dim == 1 else "x"
                        ctx["add"](
                            "ERROR",
                            "area-not-at-zero",
                            f"panel {j}: filled area has its baseline at {b:g} while "
                            f"the {name} axis shows {lo:g} to {hi:g} — area must "
                            f"grow from 0; include 0 on the {name} axis, or show "
                            "the series as a line",
                        )
                        done = True
                        break
                if done:
                    break
            if done:
                break


# 2. Dual axes.


def _check_dual_axes(ctx):
    axes = ctx["fig"].get_axes()
    for ja, jb in sorted(ctx["twins"]):
        if _has_data(axes[ja]) and _has_data(axes[jb]):
            ctx["add"](
                "WARN",
                "dual-axis",
                f"panels {ja} and {jb} are twinned axes with independent scales — "
                "dual axes invite false comparisons; use two aligned panels (P8) "
                "or index both series to a common base",
            )


# 3. Inverted numeric value axis.


def _check_inverted(ctx):
    for j, ax in ctx["vis"]:
        if _is_heatmap(ax):
            continue
        has_hbar = any(
            isinstance(c, BarContainer)
            and getattr(c, "orientation", "") == "horizontal"
            for c in ax.containers
        )
        for name, axis, inv in (
            ("x", ax.xaxis, ax.xaxis_inverted()),
            ("y", ax.yaxis, ax.yaxis_inverted()),
        ):
            if not inv or _is_categorical(axis):
                continue
            if name == "y" and has_hbar:
                continue  # ranked horizontal bars: category axis
            ctx["add"](
                "WARN",
                "inverted-axis",
                f"panel {j}: numeric {name} axis is inverted — readers assume "
                "values grow up/right; remove invert_{name}axis() unless the "
                "convention demands it (depth, rank)",
            )


# 4. Fractional tick labels on integer data.


def _check_fractional_ticks(ctx):
    for j, ax in ctx["vis"]:
        if _is_heatmap(ax):
            continue
        for which, name, axis in ((0, "x", ax.xaxis), (1, "y", ax.yaxis)):
            if axis.get_scale() != "linear" or _is_date_axis(axis):
                continue
            if _is_categorical(axis):
                continue
            v = _axis_values(ax, which)
            if len(v) < 2 or len(np.unique(v)) < 2:
                continue
            if np.abs(v - np.round(v)).max() > 1e-9:
                continue
            bad = [
                lab.get_text()
                for lab in _visible_ticklabels(axis)
                if _tick_is_fractional(axis, lab)
            ]
            if bad:
                ctx["add"](
                    "WARN",
                    "fractional-ticks",
                    f"panel {j}: {name} data are whole numbers but tick labels "
                    f"show fractions ({', '.join(bad[:3])}) — use "
                    f"ax.{name}axis.set_major_locator(MaxNLocator(integer=True))",
                )


def _tick_is_fractional(axis, lab):
    x, y = lab.get_position()
    loc = x if axis.axis_name == "x" else y
    return abs(loc - round(loc)) > 1e-6


# 5. Rainbow colormaps; diverging colormaps not centred on zero.


def _cmap_base(cm):
    name = (getattr(cm, "name", "") or "").lower()
    return name[:-2] if name.endswith("_r") else name


def _check_colormaps(ctx):
    seen = set()
    for j, ax in enumerate(ctx["fig"].get_axes()):
        if not ax.get_visible() or _is_colorbar(ax):
            continue
        for art in list(ax.collections) + list(ax.images):
            if not hasattr(art, "get_cmap") or art.get_array() is None:
                continue
            cm, base = art.get_cmap(), _cmap_base(art.get_cmap())
            if base in RAINBOW_CMAPS and (j, base) not in seen:
                seen.add((j, base))
                ctx["add"](
                    "STYLE",
                    "rainbow-cmap",
                    f"panel {j}: colormap '{cm.name}' is not perceptually uniform "
                    "and fails for colour-blind readers — use 'rocket', 'inferno', "
                    "'Blues_d' (sequential) or 'RdBu_r' (diverging)",
                )
            if base not in DIVERGING_CMAPS:
                continue
            data = np.ma.masked_invalid(np.ma.asarray(art.get_array(), float))
            if data.count() == 0 or not (data.min() < 0 < data.max()):
                continue
            norm = art.norm
            if isinstance(norm, (LogNorm,)):
                continue
            if isinstance(norm, (TwoSlopeNorm, CenteredNorm)):
                centre = norm.vcenter
            elif isinstance(norm, SymLogNorm):
                centre = 0.0 if norm.vmin == -norm.vmax else None
            else:
                vmin, vmax = norm.vmin, norm.vmax
                if vmin is None or vmax is None:
                    continue
                span = (vmax - vmin) or 1.0
                centre = 0.0 if abs(vmin + vmax) <= 0.02 * span else (vmin + vmax) / 2
            if centre is None or abs(centre) > 1e-9:
                ctx["add"](
                    "WARN",
                    "diverging-uncentred",
                    f"panel {j}: diverging colormap '{cm.name}' on data spanning "
                    f"both signs is centred at {centre if centre is not None else '?'}"
                    ", not 0 — the neutral colour lands on a non-zero value; set "
                    "vmin=-m, vmax=m (or norm=TwoSlopeNorm(0), or center=0 in "
                    "sns.heatmap)",
                )


# 6. Colour-vision-deficiency collisions between series; 7. thin-line contrast.


def _direct_label(ax_texts, a, b, thr):
    """True if some text sits next to series a (nearer to a than to b)."""
    for t, bb in ax_texts:
        da = min(_text_mark_dist(t, bb, a["pts"]), _text_mark_dist(t, bb, a["ends"]))
        db = min(_text_mark_dist(t, bb, b["pts"]), _text_mark_dist(t, bb, b["ends"]))
        if da <= thr and da < db:
            return True
    return False


def _series_name(s):
    lab = s.get("label") or ""
    lab = "" if lab.startswith("_") else f" '{_short(lab, 20)}'"
    return f"{s['kind']}{lab} {_hex(s['rgb'])}"


def _check_series_colours(ctx):
    texts_by_ax = {}
    for k, t, i, bb in ctx["texts"]:
        if k == "annotation" and i is not None:
            texts_by_ax.setdefault(i, []).append((t, bb))
    for j, ax in ctx["vis"]:
        if _is_heatmap(ax):
            continue
        series = _series(ax)
        bg = to_rgb(ax.get_facecolor())
        # 7b. thin data lines that vanish against the background
        for s in series:
            if _chroma(s["rgb"]) < 0.02:
                continue  # grey context lines are deliberately recessive
            if s["kind"] == "line" and s["lw"] is not None and s["lw"] < THIN_LW:
                c = _contrast(s["rgb"], bg)
                if c < LINE_CONTRAST_MIN:
                    ctx["add"](
                        "WARN",
                        "low-contrast-line",
                        f"panel {j}: {_series_name(s)} is a thin line "
                        f"(lw={s['lw']:g}) with contrast {c:.1f}:1 against the "
                        f"background (< {LINE_CONTRAST_MIN:g}:1) — darken it or "
                        f"thicken it to >= {THIN_LW:g}",
                    )
        abox = ax.get_window_extent(ctx["r"])
        thr = max(NEAR_FRAC * float(np.hypot(abox.width, abox.height)), 12.0)
        ax_texts = texts_by_ax.get(j, [])
        grey_noted = False
        for a, b in combinations(series, 2):
            if _same_colour(a["rgb"], b["rgb"], 0.004):
                continue  # same colour: intentionally one group
            if a["marker"] != b["marker"] or a["ls"] != b["ls"]:
                continue  # second encoding present
            if _direct_label(ax_texts, a, b, thr) or _direct_label(ax_texts, b, a, thr):
                continue
            d = _cvd_distances(a["rgb"], b["rgb"])
            worst = min(d, key=d.get)
            if d[worst] < CVD_DE_MIN:
                how = (
                    "even with normal colour vision"
                    if worst == "normal"
                    else f"under {worst}"
                )
                ctx["add"](
                    "WARN",
                    "cvd-collision",
                    f"panel {j}: {_series_name(a)} and {_series_name(b)} are "
                    f"nearly indistinguishable {how} (ΔE_OK {d[worst]:.1f} < "
                    f"{CVD_DE_MIN:g}) and share marker and line style — add a "
                    "second encoding (marker, linestyle, direct label) or pick "
                    "colours from CATEGORICAL",
                )
                continue
            dl = 100 * abs(_oklab(a["rgb"])[0] - _oklab(b["rgb"])[0])
            if dl < GREY_DL_MIN and not grey_noted:
                grey_noted = True
                ctx["add"](
                    "INFO",
                    "greyscale-collision",
                    f"panel {j}: {_series_name(a)} and {_series_name(b)} have "
                    f"similar lightness (ΔL {dl:.1f}) — they merge in greyscale "
                    "print; fine on screen, add markers or direct labels if the "
                    "chart may be printed in black and white",
                )


# 7a. Low-contrast text.


def _check_text_contrast(ctx):
    seen = set()
    for k, t, i, bb in ctx["texts"]:
        if k == "cell label":
            continue
        rgba = to_rgba(t.get_color(), t.get_alpha())
        rgb = _blend(rgba)
        if _rel_luminance(rgba[:3]) > 0.9 and _chroma(rgba[:3]) < 0.03:
            continue  # white text: assumed to sit on a dark mark
        patch = t.get_bbox_patch()
        bg = WHITE
        if patch is not None and patch.get_facecolor()[3] > 0.5:
            bg = _blend(patch.get_facecolor())
        c = _contrast(rgb, bg)
        key = (k, i, _hex(rgb))
        if c < TEXT_CONTRAST_MIN and key not in seen:
            seen.add(key)
            where = f"panel {i}" if i is not None else "figure"
            ctx["add"](
                "WARN",
                "low-contrast-text",
                f"{k} '{_short(t.get_text())}' ({where}) "
                f"is {_hex(rgb)} with contrast {c:.1f}:1 (< {TEXT_CONTRAST_MIN:g}:1) "
                "— use dimgrey, or a darker shade of the series colour",
            )


# 8. Text colour must be dimgrey (or white, accent red, or a series colour).


def _check_text_colour(ctx):
    data_cols = _data_colours(ctx["fig"])
    groups = {}
    for k, t, i, bb in ctx["texts"]:
        if k == "cell label":
            continue
        rgb = to_rgb(t.get_color())
        if _same_colour(rgb, DIMGREY, 0.03) or _same_colour(rgb, WHITE, 0.03):
            continue
        if _same_colour(rgb, ACCENT_RED, 0.03):
            continue
        if _matches_series(rgb, data_cols):
            continue  # direct label in (a shade of) its series colour
        groups.setdefault((k, i, _hex(rgb)), []).append(t.get_text())
    for (k, i, hx), txts in groups.items():
        where = f"panel {i}" if i is not None else "figure"
        eg = _short(txts[0], 25)
        more = f" (+{len(txts) - 1} more)" if len(txts) > 1 else ""
        ctx["add"](
            "STYLE",
            "text-colour",
            f"{k} '{eg}'{more} ({where}) is {hx}, not dimgrey — pass "
            "color='dimgrey' (labelcolor='dimgrey' for ticks and legends)",
        )


# 9. Detached footer text.


def _check_footer(ctx):
    fig, r = ctx["fig"], ctx["r"]
    axes = fig.get_axes()
    fh = fig.bbox.height or 1.0
    for k, t, i, bb in ctx["texts"]:
        if k == "annotation" and i is not None:
            abox = axes[i].get_window_extent(r)
            if bb.y1 <= abox.y0 + 1:
                ctx["add"](
                    "WARN",
                    "footer",
                    f"text '{_short(t.get_text())}' (panel {i}) sits below the "
                    "axes like a footer — put the takeaway in the subtitle or "
                    "annotate it at the data",
                )
        elif k == "figure text":
            cy = (bb.y0 + bb.y1) / 2 - fig.bbox.y0
            if cy / fh < 0.06:
                ctx["add"](
                    "WARN",
                    "footer",
                    f"figure text '{_short(t.get_text())}' sits in the bottom "
                    "of the figure like a footer — put the takeaway in the "
                    "subtitle or annotate it at the data",
                )


# 10. Two unescaped dollars turn prose into mathtext.


def _check_mathtext_dollar(ctx):
    for k, t, i, bb in ctx["texts"]:
        s = t.get_text()
        if getattr(t, "get_usetex", lambda: False)():
            continue
        if not getattr(t, "get_parse_math", lambda: True)():
            continue
        seg = _currency_math(s)
        if seg is not None:
            ctx["add"](
                "ERROR",
                "mathtext-dollar",
                f"{k} '{_short(s)}' has unescaped '$' signs, so '{_short(seg, 20)}' "
                "renders as italic mathtext — escape currency as '\\$' "
                '(f"\\${v:,.0f}")',
            )


# 11. Too many free-standing annotations in a panel.


def _check_annotation_count(ctx):
    fig, r = ctx["fig"], ctx["r"]
    axes = fig.get_axes()
    data_cols = _data_colours(fig)
    by_ax = {}
    for k, t, i, bb in ctx["texts"]:
        if k == "annotation" and i is not None:
            by_ax.setdefault(i, []).append((t, bb))
    for j, items in by_ax.items():
        ax = axes[j]
        if not ax.get_visible() or _is_colorbar(ax):
            continue
        abox = ax.get_window_extent(r)
        thr = max(NEAR_FRAC * float(np.hypot(abox.width, abox.height)), 12.0)
        marks = [_data_points(ax)]
        for p in _bars(ax):
            e = p.get_window_extent(r)
            marks.append(
                np.array(
                    [
                        [(e.x0 + e.x1) / 2, e.y1],
                        [(e.x0 + e.x1) / 2, e.y0],
                        [e.x1, (e.y0 + e.y1) / 2],
                        [e.x0, (e.y0 + e.y1) / 2],
                        [(e.x0 + e.x1) / 2, (e.y0 + e.y1) / 2],
                    ]
                )
            )
        marks = [m for m in marks if len(m)]
        marks = np.vstack(marks) if marks else np.empty((0, 2))
        ends = [s["ends"] for s in _series(ax) if s["kind"] == "line"]
        ends = np.vstack(ends) if ends else np.empty((0, 2))
        count = []
        for t, bb in items:
            if bb.y0 >= abox.y1 - 2 or bb.y1 <= abox.y0 + 1:
                continue  # subtitle zone above the axes / footer (own check)
            rgb = to_rgb(t.get_color())
            if not _same_colour(rgb, DIMGREY, 0.03) and _matches_series(rgb, data_cols):
                continue  # direct series label in the series colour
            txt = t.get_text().strip()
            if _is_numeric_label(txt) and _text_mark_dist(t, bb, marks) <= thr:
                continue  # value label on a mark (bar_label, dot value)
            if len(txt) <= 30 and len(ends) and _text_mark_dist(t, bb, ends) <= thr:
                continue  # direct label at a line end
            count.append(txt)
        # One label per category row/column or per band (ridgeline medians, band
        # names, n= per bar) is a labelling scheme, not free-standing notes.
        n_cat = max(
            sum(not _is_numeric_label(lab.get_text()) for lab in _visible_ticklabels(a))
            for a in (ax.xaxis, ax.yaxis)
        )
        n_fill = sum(
            isinstance(c, PolyCollection) and not isinstance(c, QuadMesh)
            for c in ax.collections
        )
        per_mark = max(n_cat, n_fill) if max(n_cat, n_fill) >= 3 else 0
        free = len(count) - per_mark if per_mark and len(count) >= per_mark - 1 else len(count)
        if free > MAX_ANNOTATIONS:
            ctx["add"](
                "WARN",
                "too-many-annotations",
                f"panel {j} has {free} free-standing annotations "
                f"(e.g. '{_short(count[0], 25)}') — one to three annotations "
                "per panel; keep the ones that state the takeaway",
            )


# --------------------------------------------------------------------------
# Saving and running a script
# --------------------------------------------------------------------------


def _check_saves(fig_id):
    out = []
    saves = _saves.get(fig_id, [])
    exts = sorted({Path(str(s["fname"])).suffix.lstrip(".").lower() for s in saves})
    dpis = sorted({s.get("dpi") for s in saves}, key=str)
    if saves and any(s.get("bbox_inches") != "tight" for s in saves):
        out.append(
            {
                "severity": "STYLE",
                "code": "savefig-bbox",
                "message": "savefig without bbox_inches='tight'",
            }
        )
    if saves and not set(dpis) <= {150, 300}:
        out.append(
            {
                "severity": "STYLE",
                "code": "savefig-dpi",
                "message": f"savefig dpi {dpis} — use 150 (300 for publication)",
            }
        )
    if "png" in exts and "pdf" not in exts:
        out.append(
            {
                "severity": "INFO",
                "code": "png-only",
                "message": "saved PNG only — fine for quick/exploratory charts; "
                "otherwise save a PDF too",
            }
        )
    dirs = {Path(str(s["fname"])).parent.name for s in saves}
    if saves and dirs != {"figures"}:
        out.append(
            {
                "severity": "INFO",
                "code": "not-in-figures-dir",
                "message": f"saved outside ./figures/ ({sorted(dirs)}) — the "
                "convention is ./figures/<name>.{pdf,png}",
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


def check_script(path, strict=False):
    """Run a chart script, inspect every figure it makes, and return the result.

    rcParams changes made by the script are reverted afterwards, and every
    figure is closed, so this can be called repeatedly in one process.
    """
    _inspected.clear()
    _saves.clear()
    script = Path(path).resolve()
    old_argv, old_path = sys.argv, list(sys.path)
    Figure.savefig, plt.show = _savefig, _show
    sys.argv = [str(script)]
    sys.path.insert(0, str(script.parent))
    run_error = None
    reports = []
    try:
        with matplotlib.rc_context():
            try:
                runpy.run_path(str(script), run_name="__main__")
            except SystemExit:
                pass
            except Exception as e:  # report instead of crashing the checker
                run_error = f"{type(e).__name__}: {e}"
            _show()  # inspect any figure that was never saved
            for fid, rep in list(_inspected.items()):
                fig = rep.pop("fig")
                exts, dpis, save_issues = _check_saves(fid)
                rep["issues"].extend(save_issues)
                fnames = [Path(str(s["fname"])) for s in _saves.get(fid, [])]
                rep.update(
                    {
                        "saved_as": sorted({p.name for p in fnames}),
                        "formats": exts,
                        "dpi": dpis,
                        "saved_pdf": "pdf" in exts,
                        "saved_png": "png" in exts,
                        "in_figures_dir": bool(fnames)
                        and all(p.parent.name == "figures" for p in fnames),
                    }
                )
                reports.append(rep)
                plt.close(fig)
    finally:
        Figure.savefig, plt.show = _orig_savefig, _orig_show
        sys.argv, sys.path[:] = old_argv, old_path
        plt.close("all")
        _inspected.clear()
        _saves.clear()

    issues = [i for r in reports for i in r["issues"]]
    n_err = sum(i["severity"] == "ERROR" for i in issues)
    n_warn = sum(i["severity"] == "WARN" for i in issues)
    failed = bool(n_err or run_error or (strict and n_warn))
    return {
        "script": script.name,
        "run_error": run_error,
        "figures": reports,
        "issues": issues,
        "errors": n_err,
        "warnings": n_warn,
        "strict": strict,
        "exit_code": 1 if failed else 0,
    }


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("script")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--strict", action="store_true", help="WARN-level issues also fail (exit 1)"
    )
    args = ap.parse_args()

    result = check_script(args.script, strict=args.strict)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["run_error"]:
            print(f"Script failed: {result['run_error']}")
        if not result["figures"]:
            print("No figures were created.")
        for rep in result["figures"]:
            name = ", ".join(rep["saved_as"]) or "(unsaved figure)"
            print(
                f"{name}  {rep['size_in'][0]}x{rep['size_in'][1]} in, "
                f"{rep['n_axes']} panel(s), dpi={rep['dpi']}"
            )
            if not rep["issues"]:
                print("  OK — no overlaps, collisions, or style drift found")
            for i in rep["issues"]:
                print(f"  {i['severity']:<5} [{i['code']}] {i['message']}")
    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
