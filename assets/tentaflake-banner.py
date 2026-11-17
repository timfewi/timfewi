#!/usr/bin/env python3
"""Render the README's Tentaflake banner as animated SVGs, wide and narrow.

Tentaflake runs isolated AI agents on one NixOS host, declared in tentaflake.toml.
The banner shows that idea: one dark host base, four separate sandboxed platforms on
it with one agent each, and the original Tentaflake logo floating above the host's
core. Tentacle cables run from the core to every platform, never from one agent to
another. A small panel labelled tentaflake.toml feeds the core: the declaration.

The logo is `tentaflake-logo.webp`: the logo from Tentaflake's
public/tentaflake-wallpaper-16x9-dark.png, cropped, with the wallpaper's dark
background keyed to transparency. Its shape and colours are unchanged; this script
only embeds and places it.

Plain SVG with CSS animation, so GitHub shows it without scripts. The base styles are
the finished frame; animations only move and brighten, so viewers without animation
support or with reduced motion requested see a complete static picture. One dark
palette serves both GitHub themes.

    python3 assets/tentaflake-banner.py
"""

import base64
import math
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
SANS = (
    "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
)
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

HW, HH, ZU = 42, 21, 30  # isometric half tile width, half tile height, unit height
N, SLAB = 10, 0.9  # host base size in tiles, slab thickness in units
OX, OY = 1250, 130  # screen position of the host base's back corner
LOOP = 12  # seconds for one round of the declaration being applied

LOGO, LOGO_CENTRE = 344, (1250, 152)  # drawn size and screen centre of the logo
SHAFT, SHAFT_R = (4.0, 4.0), 0.8  # the host's core, in tiles
PAD, PAD_Z, BOX = 0.9, 0.35, 3.0  # platform half size, platform height, sandbox height
AGENT_SCALE = 0.86
PANEL = (1534, 168, 236, 142)  # tentaflake.toml panel: screen corner, width, height


def tile(d, s):
    """Tile coordinates for a position given as x - y (across) and x + y (depth)."""
    return (s + d) / 2, (s - d) / 2


# Back row first, then the front row, staggered so no platform hides another.
PLATFORMS = (tile(-4.4, 10), tile(4.4, 10), tile(-2.2, 13.4), tile(2.2, 13.4))

INK, MUTED = "#eef2f8", "#a9b4c6"
BLUE_DEEP, BLUE_MID, BLUE_LIGHT, BLUE_SPEC = "#0f3a94", "#2364de", "#62a5ff", "#d2e7ff"
CYAN = "#5fd8e6"


def P(x, y, z=0.0):
    return OX + (x - y) * HW, OY + (x + y) * HH - z * ZU


def num(v):
    text = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def pts(points):
    return " ".join(f"{num(x)} {num(y)}" for x, y in points)


def poly(points, fill, extra=""):
    return f'<path d="M{pts(points)}Z" fill="{fill}"{extra}/>'


def seg(a, b):
    return f"M{num(a[0])} {num(a[1])}L{num(b[0])} {num(b[1])}"


def text(x, y, body, size, fill, font=MONO, weight=None, anchor=None, spacing=None):
    attrs = [
        f'x="{num(x)}" y="{num(y)}" font-size="{size}" fill="{fill}" font-family="{font}"'
    ]
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    return f"<text {' '.join(attrs)}>{body}</text>"


def bezier(p0, p1, p2, p3, steps):
    out = []
    for i in range(steps + 1):
        t = i / steps
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t**3
        out.append(
            tuple(a * p0[k] + b * p1[k] + c * p2[k] + d * p3[k] for k in range(len(p0)))
        )
    return out


def noise(seed):
    """Deterministic stream of numbers in [0, 1)."""
    state = seed
    while True:
        state = (state * 1103515245 + 12345) % 2**31
        yield state / 2**31


# --- tentacles -------------------------------------------------------------------


def tentacle(points, w0, w1, suckers=True):
    """A tapered, shaded ribbon along screen points, lit from the upper left."""
    n = len(points)
    normals, widths = [], []
    for i in range(n):
        ax, ay = points[max(i - 1, 0)]
        bx, by = points[min(i + 1, n - 1)]
        length = math.hypot(bx - ax, by - ay) or 1
        normals.append((-(by - ay) / length, (bx - ax) / length))
        widths.append(w0 + (w1 - w0) * (i / (n - 1)) ** 0.8)
    mid = normals[n // 2]
    side = 1 if mid[0] + mid[1] < 0 else -1  # which normal direction faces the light

    def strip(a, b):
        left = [
            (p[0] + m[0] * w / 2 * a * side, p[1] + m[1] * w / 2 * a * side)
            for p, m, w in zip(points, normals, widths)
        ]
        right = [
            (p[0] + m[0] * w / 2 * b * side, p[1] + m[1] * w / 2 * b * side)
            for p, m, w in zip(points, normals, widths)
        ]
        return left + right[::-1]

    body = strip(1, -1)
    out = [
        poly(body, BLUE_MID, ' opacity=".4" filter="url(#glow)"'),
        poly(body, BLUE_DEEP),
        poly(strip(1, -0.3), BLUE_MID),
        poly(strip(0.82, 0.3), BLUE_LIGHT, ' opacity=".85"'),
        poly(strip(0.68, 0.54), BLUE_SPEC, ' opacity=".7"'),
    ]
    rings = "".join(
        seg(
            *[
                (
                    points[i][0] + normals[i][0] * widths[i] / 2 * s,
                    points[i][1] + normals[i][1] * widths[i] / 2 * s,
                )
                for s in (1, -1)
            ]
        )
        for i in range(3, n - 1, 3)
    )
    out.append(f'<path d="{rings}" stroke="#061a44" stroke-width="1.2" opacity=".45"/>')
    if suckers:
        for i in range(3, n - 2, 2):
            x = points[i][0] - normals[i][0] * widths[i] * 0.31 * side
            y = points[i][1] - normals[i][1] * widths[i] * 0.31 * side
            out.append(
                f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(widths[i] * 0.075)}" fill="{BLUE_LIGHT}" opacity=".55"/>'
            )
    tx, ty = points[-1]
    out.append(
        f'<circle cx="{num(tx)}" cy="{num(ty)}" r="{num(w1 / 2)}" fill="{BLUE_MID}"/>'
    )
    return "".join(out)


def moving(svg, a, b, key, sheet, period, swing=0.0, skew=0.0, curl=0.0):
    """Wrap a tentacle from a to b in the motion that suits it.

    `skew` and `curl` shear and stretch it around the line a-b, so it flexes while both
    ends stay where they are: for cables docked at both ends. `swing` rotates the whole
    tentacle around its root a: for tentacles whose tip is free.
    """
    phi = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    frame = f"translate({num(a[0])}px,{num(a[1])}px) rotate({phi:.2f}deg)"
    back = f"rotate({-phi:.2f}deg) translate({num(-a[0])}px,{num(-a[1])}px)"
    pivot = f"translate({num(a[0])}px,{num(a[1])}px)"
    unpivot = f"translate({num(-a[0])}px,{num(-a[1])}px)"
    layers = []
    if curl:
        layers.append(
            (
                f"c{key}",
                period * 0.71,
                f"{frame} scale(1,{1 - curl:.3f}) {back}",
                f"{frame} scale(1,{1 + curl:.3f}) {back}",
            )
        )
    if skew:
        layers.append(
            (
                f"k{key}",
                period,
                f"{frame} skewX({-skew:.2f}deg) {back}",
                f"{frame} skewX({skew:.2f}deg) {back}",
            )
        )
    if swing:
        layers.append(
            (
                f"w{key}",
                period * 1.37,
                f"{pivot} rotate({-swing:.2f}deg) {unpivot}",
                f"{pivot} rotate({swing:.2f}deg) {unpivot}",
            )
        )
    delay = (sum(map(ord, key)) * 1.7) % period
    for name, duration, start, end in layers:
        sheet.append(
            f"@keyframes {name}{{from{{transform:{start}}}to{{transform:{end}}}}}"
        )
        svg = (
            f'<g class="arm" style="animation-name:{name};animation-duration:{duration:.1f}s;'
            f'animation-delay:-{delay:.1f}s">{svg}</g>'
        )
    return svg


def pulse_track(name, points):
    """Keyframes for a light running along a cable from its first point to its last."""
    x0, y0 = points[0]
    picks = points[2::3]
    frames = ["0%{opacity:0;transform:translate(0,0)}"]
    for k, (x, y) in enumerate(picks):
        pct = 8 + 84 * k / (len(picks) - 1)
        frames.append(
            f"{pct:.0f}%{{opacity:1;transform:translate({num(x - x0)}px,{num(y - y0)}px)}}"
        )
    lx, ly = picks[-1]
    frames.append(
        f"100%{{opacity:0;transform:translate({num(lx - x0)}px,{num(ly - y0)}px)}}"
    )
    return f"@keyframes {name}{{{''.join(frames)}}}"


def port(pos):
    """Where a platform's cables dock: the middle of its edge that faces the core."""
    px, py = pos
    dx, dy = SHAFT[0] - px, SHAFT[1] - py
    if abs(dx) > abs(dy):
        return px + math.copysign(PAD, dx), py + dy / abs(dx) * PAD * 0.5
    return px + dx / abs(dy) * PAD * 0.5, py + math.copysign(PAD, dy)


def cables(i, pos, sheet):
    """Two tentacle cables from the core to one platform: a main one and a thin one."""
    ex, ey = port(pos)
    dx, dy = ex - SHAFT[0], ey - SHAFT[1]
    reach = math.hypot(dx, dy)
    ux, uy = dx / reach, dy / reach
    nx, ny = -uy, ux
    out, css = [], []
    for k, (offset, lift, w0, w1) in enumerate(
        ((-0.16, 2.7, 26, 10), (0.34, 1.5, 12, 5))
    ):
        sx = SHAFT[0] + ux * SHAFT_R * 0.7 + nx * offset
        sy = SHAFT[1] + uy * SHAFT_R * 0.7 + ny * offset
        tx, ty = ex + nx * offset * 0.5, ey + ny * offset * 0.5
        curve = bezier(
            (sx, sy, -0.3),
            (sx + ux * 0.5, sy + uy * 0.5, lift * 0.3),
            (tx - ux * 0.8, ty - uy * 0.8, lift),
            (tx, ty, PAD_Z + 0.05),
            28,
        )
        path = [P(*p) for p in curve]
        body = tentacle(path, w0, w1, suckers=k == 0)
        if k == 0:
            x0, y0 = path[0]
            body += (
                f'<circle cx="{num(x0)}" cy="{num(y0)}" r="5" fill="{BLUE_SPEC}" filter="url(#glow)" class="pulse p{i}"/>'
                f'<circle cx="{num(x0)}" cy="{num(y0)}" r="3" fill="#fff" class="pulse p{i}"/>'
            )
            css.append(
                f".p{i}{{animation-name:p{i};animation-delay:{-LOOP / 4 * i + 0.3:.1f}s}}"
            )
            css.append(pulse_track(f"p{i}", path))
        out.append(
            moving(
                body,
                path[0],
                path[-1],
                f"a{i}{k}",
                sheet,
                5.5 + i * 0.7 + k * 1.3,
                skew=4.0 if k == 0 else 6.0,
                curl=0.12,
            )
        )
    return "".join(out), "".join(css)


# --- host ------------------------------------------------------------------------


def surrounds(sheet):
    """Tentacles rising from the dark below the host, around its sides, curling at the tips."""
    a = []
    for sign in (-1, 1):
        for key, (root, c1, c2, tip, curl, w0) in enumerate(
            (
                ((60, 650), (420, 670), (575, 420), (505, 300), 44, 54),
                ((150, 650), (330, 650), (480, 540), (460, 438), 30, 34),
            )
        ):
            reach = bezier(
                (OX + sign * root[0], root[1]),
                (OX + sign * c1[0], c1[1]),
                (OX + sign * c2[0], c2[1]),
                (OX + sign * tip[0], tip[1]),
                30,
            )
            hook = bezier(
                (OX + sign * tip[0], tip[1]),
                (OX + sign * (tip[0] - curl * 0.1), tip[1] - curl * 1.3),
                (OX + sign * (tip[0] - curl * 1.4), tip[1] - curl * 1.1),
                (OX + sign * (tip[0] - curl * 1.05), tip[1] - curl * 0.35),
                10,
            )
            curve = reach + hook[1:]
            a.append(
                moving(
                    tentacle(curve, w0, 6),
                    curve[0],
                    curve[30],
                    "lr"[sign > 0] + f"u{key}",
                    sheet,
                    9 + key * 2.5,
                    swing=1.4 + key * 0.6,
                    curl=0.06,
                )
            )
    # Their roots sink into the dark they rise from.
    a.append('<rect x="0" y="500" width="2400" height="600" fill="url(#deep)" transform="translate(-300 0)"/>')
    return "".join(a)


def host():
    """The shared NixOS host: one dark slab under every platform."""
    top = [P(0, 0), P(N, 0), P(N, N), P(0, N)]
    a = [
        poly([P(0, N), P(N, N), P(N, N, -SLAB), P(0, N, -SLAB)], "url(#slabL)"),
        poly([P(N, 0), P(N, N), P(N, N, -SLAB), P(N, 0, -SLAB)], "url(#slabR)"),
        poly(top, "#141a25"),
        poly(top, "url(#floorGlow)"),
    ]
    grid = "".join(seg(P(i, 0), P(i, N)) + seg(P(0, i), P(N, i)) for i in range(1, N))
    a.append(f'<path d="{grid}" stroke="#8fb0ff" stroke-width="1" opacity=".06"/>')
    seams = "".join(
        seg(P(i, N, -0.2), P(i, N, -SLAB)) + seg(P(N, i, -0.2), P(N, i, -SLAB))
        for i in range(2, N, 2)
    )
    a.append(f'<path d="{seams}" stroke="#05070b" stroke-width="1.5" opacity=".7"/>')
    for i in range(1, N, 2):
        for point in (P(i, N, -0.45), P(N, i, -0.45)):
            a.append(
                f'<circle cx="{num(point[0])}" cy="{num(point[1])}" r="1.8" fill="{BLUE_LIGHT}" opacity=".8"/>'
            )
    a.append(
        f'<path d="{seg(P(0, N), P(N, N))}{seg(P(N, N), P(N, 0))}" stroke="#4a5873" stroke-width="2"/>'
    )
    a.append(f'<path d="M{pts(top)}Z" stroke="#2c3546" stroke-width="1" fill="none"/>')
    band = [P(0, N, -0.14), P(N, N, -0.14), P(N, 0, -0.14)]
    a.append(
        f'<path d="M{pts(band)}" stroke="{BLUE_MID}" stroke-width="2" fill="none" opacity=".55"/>'
    )
    # A ring of ticks in the floor around the core.
    cx, cy = P(*SHAFT)
    r = 1.55 * math.sqrt(2) * HW
    ticks = "".join(
        seg(
            (math.cos(t) * r * 0.9, math.sin(t) * r * 0.9),
            (math.cos(t) * r, math.sin(t) * r),
        )
        for k in range(40)
        for t in (math.tau * k / 40,)
    )
    a.append(
        f'<g transform="translate({num(cx)} {num(cy)}) scale(1 .5)" class="ring" fill="none" stroke="{BLUE_LIGHT}">'
        f'<circle r="{num(r)}" stroke-width="1.6" opacity=".6"/><path d="{ticks}" stroke-width="1.6" opacity=".7"/>'
        f'<circle r="{num(r * 1.12)}" stroke-width="1" opacity=".35" stroke-dasharray="3 9"/></g>'
    )
    # Traces in the floor from the ring to every platform.
    for pos in PLATFORMS:
        ex, ey = port(pos)
        dx, dy = ex - SHAFT[0], ey - SHAFT[1]
        reach = math.hypot(dx, dy)
        start = (SHAFT[0] + dx / reach * 1.65, SHAFT[1] + dy / reach * 1.65)
        a.append(
            f'<path d="{seg(P(*start), P(ex, ey))}" stroke="{CYAN}" stroke-width="1.6" stroke-dasharray="6 5" opacity=".5"/>'
        )
    return "".join(a)


def shaft():
    cx, cy = P(*SHAFT)
    rx, ry = SHAFT_R * math.sqrt(2) * HW, SHAFT_R * math.sqrt(2) * HH
    return "".join(
        (
            f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx + 8)}" ry="{num(ry + 4)}" fill="#0b0e15" stroke="#4a5873" stroke-width="2"/>',
            f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx)}" ry="{num(ry)}" fill="#04060b"/>',
            f'<ellipse cx="{num(cx)}" cy="{num(cy + 5)}" rx="{num(rx * 0.78)}" ry="{num(ry * 0.7)}" fill="url(#core)" class="breathe"/>',
            f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx)}" ry="{num(ry)}" fill="none" stroke="{BLUE_MID}" stroke-width="1.5" opacity=".8"/>',
        )
    )


def logo(mark):
    """The original Tentaflake logo, unchanged, floating over the core in its own light."""
    cx, cy = LOGO_CENTRE
    sx, sy = P(*SHAFT)
    r = 192
    ticks = "".join(
        seg(
            (
                math.cos(t) * (r - (9 if k % 4 else 15)),
                math.sin(t) * (r - (9 if k % 4 else 15)),
            ),
            (math.cos(t) * r, math.sin(t) * r),
        )
        for k in range(64)
        for t in (math.tau * k / 64,)
    )
    return "".join(
        (
            f'<ellipse cx="{cx}" cy="{cy + 10}" rx="230" ry="190" fill="{BLUE_MID}" opacity=".26" filter="url(#haze)" class="breathe"/>',
            f'<g transform="translate({cx} {cy})" class="halo" fill="none" stroke="{BLUE_LIGHT}" opacity=".3">'
            f'<circle r="{r + 8}" stroke-width="1.2"/><path d="{ticks}" stroke-width="1"/></g>',
            poly(
                [(sx - 40, sy), (sx + 40, sy), (cx + 90, cy + 70), (cx - 90, cy + 70)],
                "url(#column)",
            ),
            f'<g class="float"><image href="data:image/webp;base64,{mark}" x="{num(cx - LOGO / 2)}" '
            f'y="{num(cy - LOGO / 2)}" width="{LOGO}" height="{LOGO}"/></g>',
        )
    )


# --- platforms -------------------------------------------------------------------


def platform(i, pos):
    """One agent's own sandbox: a raised platform inside a faint box, with its agent."""
    px, py = pos
    x0, y0, x1, y1 = px - PAD, py - PAD, px + PAD, py + PAD
    z0, z1 = PAD_Z, PAD_Z + BOX

    def c(x, y, z):
        return P(x, y, z)

    top = [c(x0, y0, z0), c(x1, y0, z0), c(x1, y1, z0), c(x0, y1, z0)]
    a = [
        f'<ellipse cx="{num(P(px, py)[0])}" cy="{num(P(px, py)[1] + 6)}" rx="86" ry="30" fill="#000" opacity=".35" filter="url(#glow)"/>',
        poly([c(x0, y1, z0), c(x1, y1, z0), c(x1, y1, 0), c(x0, y1, 0)], "url(#slabL)"),
        poly([c(x1, y0, z0), c(x1, y1, z0), c(x1, y1, 0), c(x1, y0, 0)], "url(#slabR)"),
        poly(top, "#1b2232"),
        poly(top, "url(#padGlow)"),
        f'<path d="M{pts(top[1:])}" fill="none" stroke="#51607c" stroke-width="2"/>',
        f'<path d="M{pts([c(px - PAD * 0.8, py - PAD * 0.8, z0), c(px + PAD * 0.8, py - PAD * 0.8, z0), c(px + PAD * 0.8, py + PAD * 0.8, z0), c(px - PAD * 0.8, py + PAD * 0.8, z0)])}Z" '
        f'fill="none" stroke="#8fb0ff" stroke-width="1.2" stroke-dasharray="6 5" opacity=".5"/>',
        # The sandbox's two back walls, faintly lit.
        poly(
            [c(x0, y0, z0), c(x1, y0, z0), c(x1, y0, z1), c(x0, y0, z1)], "url(#wall)"
        ),
        poly(
            [c(x0, y0, z0), c(x0, y1, z0), c(x0, y1, z1), c(x0, y0, z1)], "url(#wall)"
        ),
        f'<path d="{seg(c(x0, y0, z0), c(x0, y0, z1))}{seg(c(x0, y0, z1), c(x1, y0, z1))}{seg(c(x0, y0, z1), c(x0, y1, z1))}" '
        f'stroke="{BLUE_LIGHT}" stroke-width="1.2" opacity=".4"/>',
    ]
    dock = P(*port(pos), z0)
    a.append(
        f'<ellipse cx="{num(dock[0])}" cy="{num(dock[1])}" rx="10" ry="5" fill="#0b0e15" stroke="{CYAN}" stroke-width="1.8"/>'
        f'<ellipse cx="{num(dock[0])}" cy="{num(dock[1])}" rx="14" ry="7" fill="none" stroke="{CYAN}" stroke-width="1.4" '
        f'class="loop dock d{i}"/>'
    )
    a.append(agent(i, P(px, py, z0)))
    front = (
        seg(c(x1, y0, z0), c(x1, y0, z1))
        + seg(c(x0, y1, z0), c(x0, y1, z1))
        + seg(c(x1, y1, z0), c(x1, y1, z1))
        + seg(c(x1, y0, z1), c(x1, y1, z1))
        + seg(c(x0, y1, z1), c(x1, y1, z1))
    )
    a.append(
        f'<path d="{front}" stroke="{BLUE_LIGHT}" stroke-width="1.2" opacity=".45"/>'
    )
    for corner in (c(x0, y0, z1), c(x1, y0, z1), c(x1, y1, z1), c(x0, y1, z1)):
        a.append(
            f'<circle cx="{num(corner[0])}" cy="{num(corner[1])}" r="2.2" fill="{BLUE_SPEC}" opacity=".8"/>'
        )
    return "".join(a)


def agent(i, feet):
    """A dark, angular operator with a lit visor."""
    fx, fy = feet

    def at(points):
        return [(fx + x * AGENT_SCALE, fy + y * AGENT_SCALE) for x, y in points]

    lit, mid, dark, rim = "#4a556a", "#333c4b", "#1f242e", "#8a99b3"
    visor = at([(-10, -87), (10, -87), (9, -82), (-9, -82)])
    return "".join(
        (
            f'<ellipse cx="{num(fx)}" cy="{num(fy)}" rx="22" ry="8" fill="#000" opacity=".5"/>',
            f'<g class="stand" style="animation-delay:{-0.9 * i:.1f}s">',
            poly(at([(-12, 0), (-3, 0), (-2, -36), (-14, -36)]), mid),
            poly(at([(3, 0), (12, 0), (14, -36), (2, -36)]), dark),
            poly(at([(-26, -52), (-19, -54), (-17, -34), (-23, -33)]), mid),
            poly(at([(26, -52), (19, -54), (17, -34), (23, -33)]), dark),
            poly(at([(-15, -34), (2, -34), (2, -72), (-12, -72), (-20, -63)]), lit),
            poly(at([(2, -34), (15, -34), (20, -63), (12, -72), (2, -72)]), mid),
            poly(at([(-20, -63), (-28, -58), (-27, -50), (-18, -53)]), lit),
            poly(at([(20, -63), (28, -58), (27, -50), (18, -53)]), mid),
            poly(at([(-5, -76), (5, -76), (5, -71), (-5, -71)]), dark),
            poly(at([(-11, -76), (1, -76), (1, -94), (-9, -94), (-14, -86)]), lit),
            poly(at([(1, -76), (11, -76), (14, -86), (9, -94), (1, -94)]), mid),
            f'<path d="M{pts(at([(-20, -63), (-12, -72), (2, -72)]))}M{pts(at([(-14, -86), (-9, -94), (1, -94)]))}" '
            f'stroke="{rim}" stroke-width="1" fill="none"/>',
            poly(
                at([(-6, -58), (0, -54), (6, -58), (6, -55), (0, -51), (-6, -55)]),
                BLUE_LIGHT,
                ' opacity=".9"',
            ),
            poly(
                visor,
                BLUE_LIGHT,
                f' filter="url(#glow)" class="visor" style="animation-delay:{-0.8 * i:.1f}s"',
            ),
            poly(visor, BLUE_SPEC),
            "</g>",
        )
    )


# --- declaration -----------------------------------------------------------------


def panel_cable(sheet):
    """The cable from the tentaflake.toml panel down into the core, behind the logo."""
    x, y, w, h = PANEL
    sx, sy = P(*SHAFT)
    start = (x + 18, y + h - 4)
    curve = bezier(start, (x - 60, y + 30), (sx + 150, sy - 120), (sx + 26, sy - 6), 30)
    return moving(
        tentacle(curve, 14, 8, suckers=False),
        curve[0],
        curve[-1],
        "tc",
        sheet,
        7,
        skew=3.0,
        curl=0.1,
    )


def panel():
    """A small editor panel, standing in the isometric plane, labelled tentaflake.toml."""
    x, y, w, h = PANEL
    ux, uy = HW / math.hypot(HW, HH), -HH / math.hypot(HW, HH)
    rows = (
        ((0, 74, CYAN), (82, 70, MUTED)),
        ((22, 54, BLUE_LIGHT), (84, 92, MUTED)),
        ((22, 66, BLUE_LIGHT), (96, 58, CYAN)),
        ((0, 92, CYAN),),
    )
    bars = []
    for k, row in enumerate(rows):
        line = "".join(
            f'<rect x="{left + 18}" y="{52 + k * 21}" width="{width}" height="9" rx="4.5" fill="{colour}"/>'
            for left, width, colour in row
        )
        bars.append(f'<g class="loop line n{k}">{line}</g>')
    return (
        f'<g transform="matrix({ux:.4f} {uy:.4f} 0 1 {x} {y})">'
        f'<rect x="-6" y="-6" width="{w + 12}" height="{h + 12}" rx="14" fill="{BLUE_MID}" opacity=".25" filter="url(#glow)"/>'
        f'<rect width="{w}" height="{h}" rx="10" fill="#0b111d" stroke="{BLUE_LIGHT}" stroke-width="1.4" opacity=".95"/>'
        f'<path d="M0 32H{w}" stroke="#2c3a55" stroke-width="1.2"/>'
        + "".join(
            f'<circle cx="{16 + k * 14}" cy="16" r="4" fill="{"#3d4a63" if k else BLUE_LIGHT}"/>'
            for k in range(3)
        )
        + text(60, 23, "tentaflake.toml", 20, INK)
        + "".join(bars)
        + f'<rect x="{18 + 100}" y="{52 + 3 * 21 - 1}" width="7" height="12" fill="{INK}" class="cursor"/>'
        "</g>"
    )


# --- composition -----------------------------------------------------------------


def defs():
    return (
        "<defs>"
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1526"/>'
        '<stop offset=".55" stop-color="#0b0f18"/><stop offset="1" stop-color="#14171d"/></linearGradient>'
        '<radialGradient id="vignette" cx="62%" cy="45%" r="75%"><stop offset="0" stop-color="#0b0f18" stop-opacity="0"/>'
        '<stop offset=".6" stop-color="#0b0f18" stop-opacity=".3"/><stop offset="1" stop-color="#07090e" stop-opacity=".95"/></radialGradient>'
        f'<radialGradient id="floorGlow" gradientUnits="userSpaceOnUse" cx="{num(P(*SHAFT)[0])}" cy="{num(P(*SHAFT)[1])}" r="380">'
        f'<stop offset="0" stop-color="{BLUE_MID}" stop-opacity=".42"/><stop offset=".5" stop-color="{BLUE_MID}" stop-opacity=".1"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="padGlow"><stop offset="0" stop-color="{BLUE_MID}" stop-opacity=".3"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="core"><stop offset="0" stop-color="{BLUE_SPEC}"/><stop offset=".45" stop-color="{BLUE_MID}"/>'
        '<stop offset="1" stop-color="#04060b" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="column" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{BLUE_LIGHT}" stop-opacity=".32"/>'
        f'<stop offset="1" stop-color="{BLUE_LIGHT}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="wall" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity=".14"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity=".02"/></linearGradient>'
        '<linearGradient id="slabL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#262e3d"/><stop offset="1" stop-color="#11151d"/></linearGradient>'
        '<linearGradient id="slabR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a202c"/><stop offset="1" stop-color="#0a0d13"/></linearGradient>'
        '<linearGradient id="deep" gradientUnits="userSpaceOnUse" x1="0" y1="500" x2="0" y2="640">'
        '<stop offset="0" stop-color="#07090e" stop-opacity="0"/><stop offset="1" stop-color="#07090e"/></linearGradient>'
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>'
        '<filter id="haze" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="22"/></filter>'
        "</defs>"
    )


def backdrop(x, y, w, h):
    """Rounded dark card with a faint isometric grid that fades towards the edges."""
    lines = "".join(
        f"M{num(x + k * 84)} {num(y)}l{num(2 * h)} {num(h)}M{num(x + k * 84)} {num(y)}l{num(-2 * h)} {num(h)}"
        for k in range(-30, 50)
    )
    return (
        f'<clipPath id="card"><rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="20"/></clipPath>'
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="20" fill="url(#bg)"/>'
        f'<g clip-path="url(#card)"><path d="{lines}" stroke="#8fb0ff" stroke-width="1" opacity=".05"/>'
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" fill="url(#vignette)"/>'
    )


def atmosphere():
    """Motes of light drifting up around the host."""
    rand = noise(7)
    out = []
    for _ in range(26):
        x, y = 720 + next(rand) * 1060, 20 + next(rand) * 560
        out.append(
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(0.9 + next(rand) * 1.4)}" fill="{BLUE_SPEC}" class="mote" '
            f'style="animation-duration:{7 + next(rand) * 7:.1f}s;animation-delay:-{next(rand) * 12:.1f}s"/>'
        )
    return "".join(out)


def scene(mark):
    sheet, css = [], []
    parts = [surrounds(sheet), host(), shaft(), panel_cable(sheet)]
    back = [i for i, pos in enumerate(PLATFORMS) if sum(pos) < 12]
    front = [i for i, pos in enumerate(PLATFORMS) if sum(pos) >= 12]
    wires = {}
    for i, pos in enumerate(PLATFORMS):
        wires[i], rule = cables(i, pos, sheet)
        css.append(rule)
    parts.extend(wires[i] for i in back)
    parts.extend(wires[i] for i in front)
    parts.append(logo(mark))
    parts.extend(platform(i, PLATFORMS[i]) for i in back)
    parts.extend(platform(i, PLATFORMS[i]) for i in front)
    parts.append(panel())
    parts.append(atmosphere())
    return "".join(parts), "".join(css), sheet


def style(css, sheet):
    rules = [
        f".loop{{animation-duration:{LOOP}s;animation-iteration-count:infinite;animation-timing-function:ease-in-out}}",
        ".arm{transform-origin:0 0;animation-iteration-count:infinite;animation-direction:alternate;animation-timing-function:ease-in-out}",
        ".breathe{animation:breathe 5s ease-in-out infinite alternate}",
        "@keyframes breathe{from{opacity:.62}to{opacity:1}}",
        ".float{animation:float 6s ease-in-out infinite alternate}",
        "@keyframes float{from{transform:translateY(0)}to{transform:translateY(-6px)}}",
        ".stand{animation:stand 3.4s ease-in-out infinite alternate}",
        "@keyframes stand{from{transform:translateY(0)}to{transform:translateY(-1.5px)}}",
        ".visor{animation:visor 3.6s ease-in-out infinite alternate}",
        "@keyframes visor{from{opacity:.55}to{opacity:1}}",
        ".halo{transform-origin:0 0;animation:halo 140s linear infinite}",
        f"@keyframes halo{{from{{transform:translate({LOGO_CENTRE[0]}px,{LOGO_CENTRE[1]}px) rotate(0deg)}}"
        f"to{{transform:translate({LOGO_CENTRE[0]}px,{LOGO_CENTRE[1]}px) rotate(360deg)}}}}",
        ".ring{transform-origin:0 0;animation:ring 100s linear infinite}",
        f"@keyframes ring{{from{{transform:translate({num(P(*SHAFT)[0])}px,{num(P(*SHAFT)[1])}px) scale(1,.5) rotate(0deg)}}"
        f"to{{transform:translate({num(P(*SHAFT)[0])}px,{num(P(*SHAFT)[1])}px) scale(1,.5) rotate(-360deg)}}}}",
        ".mote{opacity:.4;animation-name:mote;animation-iteration-count:infinite;animation-timing-function:linear}",
        "@keyframes mote{0%{opacity:0;transform:translateY(0)}25%{opacity:.8}100%{opacity:0;transform:translateY(-70px)}}",
        f".pulse{{opacity:0;animation-duration:{LOOP / 4}s;animation-iteration-count:infinite;animation-timing-function:linear}}",
        ".cursor{animation:cursor 1.1s steps(1) infinite}",
        "@keyframes cursor{50%{opacity:0}}",
        ".dock{opacity:.2}",
        css,
    ]
    rules += sheet
    for i in range(len(PLATFORMS)):
        rules.append(
            f".d{i}{{animation:dock {LOOP / 4}s ease-out infinite;animation-delay:{-LOOP / 4 * i + 0.3 - LOOP / 4 * 0.9:.2f}s}}"
        )
    rules.append("@keyframes dock{0%{opacity:1}60%,100%{opacity:.2}}")
    for k in range(4):
        a = 25 * k
        rules.append(
            f".n{k}{{animation-name:n{k}}}@keyframes n{k}{{0%,{a}%{{opacity:.55}}{a + 4}%,{a + 20}%{{opacity:1}}{a + 25}%,100%{{opacity:.55}}}}"
        )
    rules.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return "".join(rules)


TITLE = "Tentaflake"
SUBTITLE = ("Isolated AI agents.", "Declarative infrastructure.")
STACK = "NixOS · gVisor · Rust"
DESC = (
    "Tentaflake: isolated AI agents, declarative infrastructure. NixOS, gVisor, Rust. Illustration: the "
    "original Tentaflake logo, a blue octopus within crystal arms, floats over the glowing core of one dark "
    "host base. Tentacle cables run from the core to four separate platforms on that base, each inside a "
    "faint box with one agent; no cable joins two agents. Larger tentacles reach around the base from below. "
    "A small panel labelled tentaflake.toml sends a cable into the core."
)


def render(layout, mark):
    body, css, sheet = scene(mark)
    if layout == "wide":
        vx, vy, w, h = 0, 0, 1800, 600
        words = [
            f'<rect x="84" y="172" width="64" height="5" rx="2.5" fill="{BLUE_LIGHT}"/>',
            text(78, 274, TITLE, 108, INK, SANS, weight=700, spacing=-1),
            text(84, 336, SUBTITLE[0], 36, MUTED, SANS),
            text(84, 382, SUBTITLE[1], 36, MUTED, SANS),
            text(84, 444, STACK, 23, BLUE_LIGHT, spacing=2),
        ]
    else:
        vx, vy, w, h = 610, -330, 1300, 940
        words = [
            f'<rect x="{vx + 58}" y="{vy + 58}" width="76" height="6" rx="3" fill="{BLUE_LIGHT}"/>',
            text(vx + 52, vy + 178, TITLE, 132, INK, SANS, weight=700, spacing=-1),
            text(vx + 58, vy + 246, " ".join(SUBTITLE), 44, MUTED, SANS),
            text(vx + 58, vy + 304, STACK, 30, BLUE_LIGHT, spacing=2),
        ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d">'
        f'<title id="t">{TITLE}</title><desc id="d">{DESC}</desc>'
        f"<style>{style(css, sheet)}</style>{defs()}{backdrop(vx, vy, w, h)}"
        f"{body}</g>{''.join(words)}</svg>\n"
    )


def main():
    mark = base64.b64encode((ASSETS / "tentaflake-logo.webp").read_bytes()).decode()
    for layout, name in (
        ("wide", "tentaflake-banner.svg"),
        ("narrow", "tentaflake-banner-narrow.svg"),
    ):
        (ASSETS / name).write_text(render(layout, mark), encoding="utf-8")


if __name__ == "__main__":
    main()
