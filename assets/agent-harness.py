#!/usr/bin/env python3
"""Render the README's benchmark scene as animated SVGs, wide and narrow.

A dark isometric platform for one agent-harness benchmark task, "repair routing and
firewall". Tentaflake rises from a shaft in its centre as a giant crystal kraken: the
Tentaflake mark is its head, and its arms are the harness. They dock on every agent
from above, hold the evaluator's eye aloft and reach around the platform from below.
Each agent stands on its own pad with a hologram of its isolated Linux network (client,
router, firewall, web, admin). The eye probes every network in turn: web must be
reachable, admin must stay blocked.

Everything is synthetic: no run, score, ranking or live data. Plain SVG with CSS
animation, so GitHub shows it without scripts. The base styles are the finished frame;
animations only move, dim and reveal, so viewers without animation support or with
reduced motion requested see a complete static scene. One dark palette serves both
GitHub themes.

    python3 assets/agent-harness.py
"""

import base64
import math
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
HW, HH, ZU = 36, 18, 36  # isometric half tile width, half tile height, unit height
N, SLAB = 14, 1.4  # platform size in tiles, slab thickness in units
C = N / 2  # the shaft sits in the centre tile corner
CY = N * HH  # screen y of the platform centre; its screen x is 0
LOOP = 20  # seconds
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

SHAFT_R = 1.6
HEAD = (0.0, -84.0)  # screen centre of the kraken's head: the Tentaflake mark
MARK, MARK_CENTRE = 384, 0.475  # drawn size of the mark, height of its centre in the image
EYE = (352.0, -176.0)  # screen centre of the evaluator's eye
AGENT_SCALE = 1.08
AGENT_H = 94 * AGENT_SCALE  # pixels from feet to crown
PAD = 1.4  # radius of an agent's pad in tiles


def grid(sx, sy):
    """Tile coordinates for a screen offset from the platform centre."""
    d, s = sx / HW, sy / HH
    return C + (s + d) / 2, C + (s - d) / 2


# Staggered so that no agent stands straight behind another or behind the kraken.
AGENTS = tuple(
    grid(*spot)
    for spot in (
        (-150, -115),
        (150, -115),
        (310, -40),
        (240, 70),
        (95, 140),
        (-95, 140),
        (-240, 70),
        (-310, -40),
    )
)
# Invented outcome per network for the picture: (web reachable, admin blocked).
OUTCOMES = (
    (True, True),
    (True, True),
    (True, True),
    (True, False),
    (True, True),
    (True, True),
    (False, True),
    (True, True),
)
FIXED = (18, 30, 24, 36, 21, 33, 27, 39)  # loop percentage at which each fix lands
PROBE_START, PROBE_STEP = 46, 6

INK, MUTED, DIM = "#e8edf5", "#9aa6b8", "#5b6677"
BLUE_DEEP, BLUE_MID, BLUE_LIGHT, BLUE_SPEC = "#0f3a94", "#2364de", "#62a5ff", "#d2e7ff"
OK, BAD, AMBER = "#4ade80", "#ff6b5e", "#f2b84b"


def P(x, y, z=0.0):
    return (x - y) * HW, (x + y) * HH - z * ZU


def num(v):
    text = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def pts(points):
    return " ".join(f"{num(x)} {num(y)}" for x, y in points)


def poly(points, fill, extra=""):
    return f'<path d="M{pts(points)}Z" fill="{fill}"{extra}/>'


def seg(a, b):
    return f"M{num(a[0])} {num(a[1])}L{num(b[0])} {num(b[1])}"


def text(x, y, body, size=13, fill=MUTED, weight=None, anchor=None, spacing=None):
    attrs = [f'x="{num(x)}" y="{num(y)}" font-size="{size}" fill="{fill}"']
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


def mix(a, b, t):
    """Blend two #rrggbb colours."""
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


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
    """Wrap an arm from a to b in the motion that suits it.

    `skew` and `curl` shear and stretch the arm around the line a-b, so it flexes while
    both ends stay where they are: for arms docked on something. `swing` rotates the
    whole arm around its root a: for arms whose tip is free.
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


def control_path(agent):
    """3D curve from the shaft, under the kraken's body, over and down onto the agent's crown."""
    ax, ay = agent
    dx, dy = ax - C, ay - C
    reach = math.hypot(dx, dy)
    sx, sy = C + dx / reach * 1.15, C + dy / reach * 1.15
    crown = AGENT_H / ZU + 0.02
    if dx + dy > 0:  # towards the viewer: stay low, clear of the kraken's face
        c1 = (sx + dx * 0.42, sy + dy * 0.42, 1.2)
    else:  # away from the viewer: rise behind the body first
        c1 = (sx + dx * 0.12, sy + dy * 0.12, 5.4)
    curve = bezier((sx, sy, -0.3), c1, (ax, ay, crown + 2.7), (ax, ay, crown), 30)
    return [P(*p) for p in curve]


def pulse_track(name, points):
    """Keyframes for a light running along an arm from the shaft to its agent."""
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


# --- platform --------------------------------------------------------------------


def backdrop(sheet):
    """Behind the platform: two arms rising out of the dark, and the kraken's halo."""
    a = []
    for sign in (-1, 1):
        curve = bezier(
            (sign * 452, CY + 40),
            (sign * 500, 150),
            (sign * 396, 96),
            (sign * 430, 22),
            26,
        )
        a.append(
            f'<g opacity=".5">{moving(tentacle(curve, 46, 9), curve[0], curve[-1], "bl"[sign > 0] + "a", sheet, 9, swing=2.4, curl=0.14)}</g>'
        )
    hx, hy = HEAD
    ticks = "".join(
        seg(
            (
                math.cos(t) * (150 if k % 3 else 143),
                math.sin(t) * (150 if k % 3 else 143),
            ),
            (math.cos(t) * 160, math.sin(t) * 160),
        )
        for k in range(48)
        for t in (math.tau * k / 48,)
    )
    signs = "".join(
        f'<path d="{GLYPHS[(k * 3 + k // 2) % len(GLYPHS)]}" transform="rotate({360 * k / 18:.1f}) translate(0 -127) scale(.8)"/>'
        for k in range(18)
    )
    a.append(
        f'<ellipse cx="{num(hx)}" cy="{num(hy + 20)}" rx="250" ry="220" fill="{BLUE_MID}" opacity=".3" filter="url(#haze)"/>'
        f'<g transform="translate({num(hx)} {num(hy)}) scale(1.27)" class="halo" opacity=".42" stroke="{BLUE_LIGHT}" fill="none">'
        f'<circle r="166" stroke-width="1.2"/><circle r="139" stroke-width=".8"/><circle r="115" stroke-width=".8"/>'
        f'<path d="{ticks}" stroke-width="1"/><g stroke-width="1.1" opacity=".8">{signs}</g>'
        f'<path d="M0 -139L120.4 69.5L-120.4 69.5Z" stroke-width=".8" opacity=".7"/>'
        f'<path d="M0 139L120.4 -69.5L-120.4 -69.5Z" stroke-width=".8" opacity=".7"/></g>'
    )
    return "".join(a)


def underside(sheet):
    """What comes from below: the trunk and two arms reaching up around the platform."""
    bottom = P(N, N)[1]
    a = [
        f'<ellipse cx="0" cy="{num(bottom + 60)}" rx="400" ry="110" fill="{BLUE_MID}" opacity=".2" filter="url(#haze)"/>'
    ]
    trunk = bezier(
        (0, bottom - 70), (-26, bottom + 60), (30, bottom + 180), (-6, bottom + 330), 24
    )
    a.append(tentacle(trunk, 168, 144, suckers=False))
    for sign in (-1, 1):
        curve = bezier(
            (sign * 76, bottom - 30),
            (sign * 290, bottom + 190),
            (sign * 690, bottom + 130),
            (sign * 548, CY - 26),
            40,
        )
        a.append(
            moving(
                tentacle(curve, 66, 12),
                curve[0],
                curve[-1],
                "lr"[sign > 0] + "b",
                sheet,
                11,
                swing=1.5,
                curl=0.07,
            )
        )
    # Everything below sinks into the dark it rises from.
    a.append(
        f'<rect x="-800" y="{num(bottom + 30)}" width="1600" height="1600" fill="url(#deep)"/>'
    )
    return "".join(a)


def platform():
    top = [P(0, 0), P(N, 0), P(N, N), P(0, N)]
    a = [
        poly([P(0, N), P(N, N), P(N, N, -SLAB), P(0, N, -SLAB)], "url(#slabL)"),
        poly([P(N, 0), P(N, N), P(N, N, -SLAB), P(N, 0, -SLAB)], "url(#slabR)"),
        poly(top, "#141922"),
        poly(top, "url(#floorGlow)"),
    ]
    grid_lines = "".join(
        seg(P(i, 0), P(i, N)) + seg(P(0, i), P(N, i)) for i in range(1, N)
    )
    a.append(
        f'<path d="{grid_lines}" stroke="#8fb0ff" stroke-width="1" opacity=".06"/>'
    )
    seams = "".join(
        seg(P(i, N, -0.3), P(i, N, -SLAB)) + seg(P(N, i, -0.3), P(N, i, -SLAB))
        for i in range(2, N, 2)
    )
    a.append(f'<path d="{seams}" stroke="#05070b" stroke-width="1.5" opacity=".7"/>')
    for i in range(1, N, 2):
        for point in (P(i, N, -0.55), P(N, i, -0.55)):
            a.append(
                f'<circle cx="{num(point[0])}" cy="{num(point[1])}" r="1.8" fill="{BLUE_LIGHT}" opacity=".8"/>'
            )
    # Lit bevel on the two front edges and a hairline around the top.
    a.append(
        f'<path d="{seg(P(0, N), P(N, N))}{seg(P(N, N), P(N, 0))}" stroke="#4a5873" stroke-width="2"/>'
    )
    a.append(f'<path d="M{pts(top)}Z" stroke="#2c3546" stroke-width="1" fill="none"/>')
    band = [P(0, N, -0.16), P(N, N, -0.16), P(N, 0, -0.16)]
    a.append(
        f'<path d="M{pts(band)}" stroke="{BLUE_MID}" stroke-width="2" fill="none" opacity=".55"/>'
    )
    return "".join(a)


GLYPHS = (
    "M-5 -8L5 -8M0 -8L0 8",
    "M-5 8L0 -8L5 8",
    "M-5 -8L5 0L-5 8",
    "M-5 -8L-5 8L5 8M5 -8L5 0",
    "M0 -8L6 0L0 8L-6 0Z",
    "M-5 -8L5 8M5 -8L-5 8",
    "M-5 -8L5 -8L-5 8L5 8",
    "M0 -8L0 8M-5 -2L5 -2M-5 3L5 3",
)


def rune_ring():
    """A ring of signs in the floor around the shaft, drawn flat and laid into the floor plane."""
    scale = math.sqrt(2) * HW
    inner, outer = 2.2 * scale, 3.05 * scale
    middle = (inner + outer) / 2
    count = 28
    signs = "".join(
        f'<path d="{GLYPHS[(k * 5 + k // 3) % len(GLYPHS)]}" transform="rotate({360 * k / count:.1f}) translate(0 {num(-middle)})"/>'
        for k in range(count)
    )
    return (
        f'<g transform="translate(0 {num(CY)}) scale(1 .5)" class="rune" fill="none" stroke="{BLUE_LIGHT}">'
        f'<circle r="{num(inner)}" stroke-width="2" opacity=".7"/><circle r="{num(outer)}" stroke-width="2" opacity=".7"/>'
        f'<circle r="{num(outer + 9)}" stroke-width="1" opacity=".35" stroke-dasharray="3 9"/>'
        f'<g stroke-width="1.8" opacity=".75">{signs}</g></g>'
    )


def pad(agent):
    """An agent's own pad: a marked disc in the floor, wired to the ring around the shaft."""
    ax, ay = agent
    cx, cy = P(ax, ay)
    rx, ry = PAD * math.sqrt(2) * HW, PAD * math.sqrt(2) * HH
    dx, dy = ax - C, ay - C
    reach = math.hypot(dx, dy)
    near = (C + dx / reach * 3.3, C + dy / reach * 3.3)
    edge = (ax - dx / reach * PAD, ay - dy / reach * PAD)
    ticks = "".join(
        seg(
            (cx + math.cos(t) * rx * 0.86, cy + math.sin(t) * ry * 0.86),
            (cx + math.cos(t) * rx, cy + math.sin(t) * ry),
        )
        for k in range(12)
        for t in (math.tau * k / 12,)
    )
    return (
        f'<path d="{seg(P(*near), P(*edge))}" stroke="{BLUE_LIGHT}" stroke-width="1.6" opacity=".5"/>'
        f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx)}" ry="{num(ry)}" fill="#0d1119" stroke="#8fb0ff" '
        f'stroke-width="1.3" stroke-dasharray="7 5" opacity=".75"/>'
        f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx)}" ry="{num(ry)}" fill="url(#padGlow)"/>'
        f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx * 0.62)}" ry="{num(ry * 0.62)}" fill="none" '
        f'stroke="{BLUE_LIGHT}" stroke-width="1" opacity=".5"/>'
        f'<path d="{ticks}" stroke="#b9ccff" stroke-width="1.4" opacity=".7"/>'
    )


def shaft():
    rx, ry = SHAFT_R * math.sqrt(2) * HW, SHAFT_R * math.sqrt(2) * HH
    return "".join(
        (
            f'<ellipse cx="0" cy="{num(CY)}" rx="{num(rx + 9)}" ry="{num(ry + 4.5)}" fill="#0b0e15" stroke="#4a5873" stroke-width="2"/>',
            f'<ellipse cx="0" cy="{num(CY)}" rx="{num(rx)}" ry="{num(ry)}" fill="#04060b"/>',
            f'<ellipse cx="0" cy="{num(CY + 7)}" rx="{num(rx * 0.78)}" ry="{num(ry * 0.7)}" fill="url(#core)" class="breathe"/>',
            f'<ellipse cx="0" cy="{num(CY)}" rx="{num(rx)}" ry="{num(ry)}" fill="none" stroke="{BLUE_MID}" stroke-width="1.5" opacity=".8"/>',
        )
    )


# --- the kraken ------------------------------------------------------------------


def mark_point(u, v):
    """Screen position of a point given as fractions of the Tentaflake mark's square image."""
    return HEAD[0] + (u - 0.5) * MARK, HEAD[1] + (v - MARK_CENTRE) * MARK


def core():
    """The dark mass behind the mark: it fills the gap between the crystals and ends in a chin."""
    top, chin = mark_point(0.5, 0.33), mark_point(0.5, 0.925)
    ridge = mark_point(0.5, 0.6)
    left = [mark_point(0.36, 0.42), mark_point(0.33, 0.66), mark_point(0.38, 0.83)]
    right = [mark_point(1 - u, v) for u, v in ((0.36, 0.42), (0.33, 0.66), (0.38, 0.83))]
    edge = ' stroke="#040a1c" stroke-width="1" stroke-linejoin="round"'
    return "".join(
        (
            poly([top, left[0], left[1], ridge], "#0e2a68", edge),
            poly([ridge, left[1], left[2], chin], "#0a1f4f", edge),
            poly([top, right[0], right[1], ridge], "#081a42", edge),
            poly([ridge, right[1], right[2], chin], "#06122e", edge),
        )
    )


def gaze(lit):
    """The mark's two drops as the kraken's eyes: a glow behind them, a lit core on top."""
    a = []
    for sign in (-1, 1):
        x, y = mark_point(0.5 + sign * 0.057, 0.665)
        turn = f' transform="rotate({sign * 24} {num(x)} {num(y)})" class="gaze"'
        if lit:
            a.append(
                f'<ellipse cx="{num(x)}" cy="{num(y)}" rx="{num(MARK * 0.011)}" ry="{num(MARK * 0.03)}" fill="#f1fbff"{turn}/>'
            )
        else:
            a.append(
                f'<ellipse cx="{num(x)}" cy="{num(y)}" rx="{num(MARK * 0.035)}" ry="{num(MARK * 0.06)}" fill="#8fdcff" '
                f'opacity=".9" filter="url(#glow)"{turn}/>'
            )
    return "".join(a)


def beard(sheet):
    """The face tentacles: they grow from under the mark's lower crystals and hang down to the shaft."""
    roots = ((0.763, 0.585), (0.69, 0.655), (0.622, 0.715), (0.558, 0.76), (0.5, 0.77))
    a = []
    for k, (u, v) in enumerate(roots):
        for sign in (-1, 1) if u != 0.5 else (0,):
            rx, ry = mark_point(0.5 + sign * (u - 0.5), v)
            spread = (u - 0.5) / 0.263
            length = 196 - 92 * spread
            end = (rx * 1.26 + sign * (18 + 28 * spread), ry + length - 22 * spread)
            curve = bezier(
                (rx, ry),
                (rx - sign * 8, ry + length * 0.45),
                (rx * 1.18 - sign * 10, ry + length + 14),
                end,
                18,
            )
            a.append(
                moving(
                    tentacle(curve, 38 - 8 * spread, 8),
                    curve[0],
                    curve[-1],
                    f"f{k}{'lcr'[sign + 1]}",
                    sheet,
                    6 + k * 0.7 + sign * 0.4,
                    swing=2.2,
                    curl=0.34 if sign else 0,
                )
            )
    return "".join(a)


def kraken(mark, sheet):
    """Body and face tentacles, and the Tentaflake mark itself as the kraken's head."""
    hx, hy = HEAD
    neck = mark_point(0.5, 0.8)
    column = bezier((0, CY + 14), (-10, CY - 60), (8, neck[1] + 70), neck, 14)
    x, y = mark_point(0, 0)
    return "".join(
        (
            f'<g opacity=".8">{tentacle(column, 92, 112, suckers=False)}</g>',
            beard(sheet),
            core(),
            f'<ellipse cx="{num(hx)}" cy="{num(hy)}" rx="170" ry="130" fill="{BLUE_MID}" opacity=".3" filter="url(#haze)" class="breathe"/>',
            gaze(False),
            f'<image href="data:image/webp;base64,{mark}" x="{num(x)}" y="{num(y)}" width="{MARK}" height="{MARK}"/>',
            gaze(True),
        )
    )


# --- figures ---------------------------------------------------------------------


def agent(i, pos):
    """A dark, angular operator with a lit visor; an arm docks on its crown."""
    fx, fy = P(*pos)

    def at(points):
        return [(fx + x * AGENT_SCALE, fy + y * AGENT_SCALE) for x, y in points]

    lit, mid, dark, rim = "#465064", "#303846", "#1e232d", "#8493ad"
    a = [
        f'<ellipse cx="{num(fx)}" cy="{num(fy)}" rx="28" ry="10" fill="#000" opacity=".55"/>',
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
        # Chest marker and visor, lit while the harness drives the agent.
        poly(
            at([(-6, -58), (0, -54), (6, -58), (6, -55), (0, -51), (-6, -55)]),
            BLUE_LIGHT,
            ' opacity=".9"',
        ),
        poly(
            at([(-10, -87), (10, -87), (9, -82), (-9, -82)]),
            BLUE_LIGHT,
            f' filter="url(#glow)" class="visor" style="animation-delay:{-0.85 * i:.2f}s"',
        ),
        poly(
            at([(-10, -87), (10, -87), (9, -82), (-9, -82)]),
            BLUE_SPEC,
            f' class="visor" style="animation-delay:{-0.85 * i:.2f}s"',
        ),
        "</g>",
        # Dock on the crown.
        f'<ellipse cx="{num(fx)}" cy="{num(fy - AGENT_H)}" rx="10" ry="4" fill="#0b0e15" stroke="{BLUE_LIGHT}" stroke-width="1.5"/>',
    ]
    return "".join(a)


def hologram(i, pos):
    """The agent's isolated network as a standing hologram: client, router, firewall, web, admin."""
    ax, ay = pos
    web_ok, admin_blocked = OUTCOMES[i]
    if P(ax, ay)[0] < 0:  # left of the shaft: panel on the agent's left
        origin, axis = (ax - 1.95, ay + 0.9), (1, 0)
    else:
        origin, axis = (ax + 0.9, ay - 0.35), (0, -1)

    def h(u, v):
        return P(origin[0] + axis[0] * u, origin[1] + axis[1] * u, 0.75 + v)

    w, top = 1.6, 1.35
    frame = [h(0, 0), h(w, 0), h(w, top), h(0, top)]
    a = [
        poly(frame, "url(#holo)"),
        f'<path d="M{pts(frame)}Z" stroke="{BLUE_LIGHT}" stroke-width="1.2" fill="none" opacity=".8"/>',
        f'<path d="{seg(h(0.25, 0), P(origin[0] + axis[0] * 0.25, origin[1] + axis[1] * 0.25))}'
        f'{seg(h(w - 0.25, 0), P(origin[0] + axis[0] * (w - 0.25), origin[1] + axis[1] * (w - 0.25)))}" '
        f'stroke="{BLUE_LIGHT}" stroke-width="1" opacity=".45"/>',
    ]
    client, router, web, admin = (
        h(0.2, 0.68),
        h(0.62, 0.68),
        h(1.38, 1.0),
        h(1.38, 0.36),
    )
    gate_web, gate_admin = h(0.98, 0.88), h(0.98, 0.5)
    # Firewall: a bar that should open for web and stay shut for admin.
    bar = seg(h(0.98, 0.14), h(0.98, 0.38)) + seg(h(0.98, 0.62), h(0.98, 0.76))
    bar += seg(h(0.98, 1.0), h(0.98, 1.22))
    if admin_blocked:
        bar += seg(h(0.98, 0.38), h(0.98, 0.62))
    if not web_ok:
        bar += seg(h(0.98, 0.76), h(0.98, 1.0))
    a.append(f'<path d="{bar}" stroke="#e0a26a" stroke-width="4"/>')
    a.append(
        f'<path d="{seg(client, router)}" stroke="{INK}" stroke-width="1.4" opacity=".7"/>'
    )
    packet = None
    if web_ok:
        a.append(
            f'<path d="{seg(h(0.98, 0.76), h(0.98, 1.0))}" stroke="#e0a26a" stroke-width="4" class="loop shut s{i}"/>'
        )
        a.append(
            f'<path d="M{pts([router, gate_web, web])}" stroke="{OK}" stroke-width="2" fill="none" class="loop open o{i}"/>'
        )
        packet = (router, gate_web, web)
    else:
        a.append(
            f'<path d="M{pts([router, gate_web])}" stroke="{DIM}" stroke-width="2" fill="none"/>'
        )
    if admin_blocked:
        a.append(
            f'<path d="M{pts([router, gate_admin])}" stroke="{BAD}" stroke-width="2" fill="none"/>'
            f'<path d="M{num(gate_admin[0] - 3)} {num(gate_admin[1] - 3)}l6 6m0 -6l-6 6" stroke="{BAD}" stroke-width="1.8"/>'
        )
    else:
        a.append(
            f'<path d="M{pts([router, gate_admin, admin])}" stroke="{BAD}" stroke-width="2" fill="none"/>'
        )
    nodes = (
        (client, INK),
        (router, BLUE_LIGHT),
        (web, OK if web_ok else DIM),
        (admin, DIM if admin_blocked else BAD),
    )
    for point, colour in nodes:
        a.append(
            f'<circle cx="{num(point[0])}" cy="{num(point[1])}" r="3.6" fill="{colour}"/>'
        )
    if packet:
        a.append(
            f'<g class="loop open o{i}"><circle cx="{num(router[0])}" cy="{num(router[1])}" r="3" fill="{INK}" '
            f'class="packet q{i}"/></g>'
        )
    # Check lamps above the hologram, lit once the eye has probed this network.
    lamps = []
    for k, held in enumerate(OUTCOMES[i]):
        lx, ly = h(0.45 + k * 0.7, top + 0.3)
        colour = OK if held else BAD
        lamps.append(
            f'<circle cx="{num(lx)}" cy="{num(ly)}" r="9" fill="{colour}" opacity=".5" filter="url(#glow)"/>'
            f'<circle cx="{num(lx)}" cy="{num(ly)}" r="5.5" fill="{colour}"/>'
        )
    a.append(f'<g class="loop lamp l{i}">{"".join(lamps)}</g>')
    return "".join(a), packet, h(0.8, top + 0.3)


def eye_arm(sheet):
    """The arm that holds the evaluator's eye aloft, rising from behind the kraken's head."""
    ex, ey = EYE
    curve = bezier((40, 20), (150, -250), (286, -28), (ex - 5, ey + 37), 30)
    return moving(
        tentacle(curve, 38, 13), curve[0], curve[-1], "ey", sheet, 8, skew=3.2, curl=0.1
    )


def evaluator():
    """The evaluator as a single armoured eye, cradled by one of the kraken's arms."""
    ex, ey = EYE

    def at(points):
        return [(ex + px, ey + py) for px, py in points]

    shards = "".join(
        poly(
            at([(px, py - 9), (px + 5, py), (px, py + 9), (px - 5, py)]),
            AMBER,
            ' opacity=".7"',
        )
        for px, py in ((-62, -22), (64, 6), (-40, 44))
    )
    return (
        f'<ellipse cx="{num(ex)}" cy="{num(ey)}" rx="70" ry="62" fill="{AMBER}" opacity=".2" filter="url(#haze)"/>'
        f'<ellipse cx="{num(ex)}" cy="{num(ey + 2)}" rx="56" ry="16" fill="none" stroke="{AMBER}" stroke-width="1.4" '
        f'opacity=".7" transform="rotate(-12 {num(ex)} {num(ey)})"/>'
        f'<circle cx="{num(ex)}" cy="{num(ey)}" r="36" fill="url(#orb)" stroke="#7a879c" stroke-width="1.2"/>'
        f"{poly(at([(-36, -4), (-27, -25), (-6, -36), (17, -33), (33, -16), (36, -3), (20, -17), (0, -22), (-20, -16)]), '#39424f')}"
        f"{poly(at([(-36, 4), (-22, 17), (0, 23), (22, 16), (36, 3), (30, 21), (12, 34), (-10, 35), (-29, 23)]), '#171b23')}"
        f'<circle cx="{num(ex)}" cy="{num(ey)}" r="21" fill="{AMBER}" opacity=".6" filter="url(#glow)" class="gaze"/>'
        f'<circle cx="{num(ex)}" cy="{num(ey)}" r="15.5" fill="url(#iris)"/>'
        f'<path d="M{num(ex)} {num(ey - 13)}Q{num(ex + 6)} {num(ey)} {num(ex)} {num(ey + 13)}Q{num(ex - 6)} {num(ey)} {num(ex)} {num(ey - 13)}Z" fill="#160d02"/>'
        f'<circle cx="{num(ex - 5)}" cy="{num(ey - 6)}" r="2.4" fill="#fff6dd"/>'
        f'<ellipse cx="{num(ex - 4)}" cy="{num(ey + 36)}" rx="14" ry="5" fill="#0b0e15" stroke="{BLUE_LIGHT}" stroke-width="1.5"/>'
        f"{shards}"
    )


# --- composition -----------------------------------------------------------------


def defs():
    return (
        "<defs>"
        '<radialGradient id="bg" cx="50%" cy="40%" r="78%"><stop offset="0" stop-color="#172238"/>'
        '<stop offset=".5" stop-color="#0b1019"/><stop offset="1" stop-color="#05070b"/></radialGradient>'
        f'<radialGradient id="floorGlow" gradientUnits="userSpaceOnUse" cx="0" cy="{num(CY)}" r="400">'
        f'<stop offset="0" stop-color="{BLUE_MID}" stop-opacity=".45"/><stop offset=".5" stop-color="{BLUE_MID}" stop-opacity=".1"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="padGlow"><stop offset="0" stop-color="{BLUE_MID}" stop-opacity=".4"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="core"><stop offset="0" stop-color="{BLUE_SPEC}"/><stop offset=".45" stop-color="{BLUE_MID}"/>'
        '<stop offset="1" stop-color="#04060b" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="orb" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#4a5466"/>'
        '<stop offset=".6" stop-color="#1c212b"/><stop offset="1" stop-color="#0a0c11"/></radialGradient>'
        f'<radialGradient id="iris"><stop offset="0" stop-color="#fff0c4"/><stop offset=".5" stop-color="{AMBER}"/>'
        '<stop offset="1" stop-color="#7d4c0c"/></radialGradient>'
        '<linearGradient id="slabL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#252c3a"/><stop offset="1" stop-color="#11151d"/></linearGradient>'
        '<linearGradient id="slabR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#191e29"/><stop offset="1" stop-color="#0a0d13"/></linearGradient>'
        f'<linearGradient id="holo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE_MID}" stop-opacity=".34"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity=".1"/></linearGradient>'
        f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{AMBER}" stop-opacity=".05"/></linearGradient>'
        f'<linearGradient id="deep" gradientUnits="userSpaceOnUse" x1="0" y1="{num(P(N, N)[1] + 30)}" x2="0" y2="{num(P(N, N)[1] + 330)}">'
        '<stop offset="0" stop-color="#05070b" stop-opacity="0"/>'
        '<stop offset=".55" stop-color="#05070b" stop-opacity=".82"/><stop offset="1" stop-color="#05070b"/></linearGradient>'
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>'
        '<filter id="haze" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="22"/></filter>'
        "</defs>"
    )


def atmosphere():
    """Mist over the floor and motes of light drifting up."""
    a = [
        f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{BLUE_LIGHT}" opacity=".1" filter="url(#haze)" '
        f'class="mist" style="animation-delay:-{k * 4}s"/>'
        for k, (x, y, rx, ry) in enumerate(
            (
                (-300, 330, 190, 40),
                (310, 300, 170, 36),
                (0, 440, 230, 44),
                (0, 150, 210, 34),
            )
        )
    ]
    rand = noise(11)
    for k in range(30):
        x, y = -560 + next(rand) * 1120, -300 + next(rand) * 800
        a.append(
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(0.9 + next(rand) * 1.5)}" fill="{BLUE_SPEC}" class="mote" '
            f'style="animation-duration:{7 + next(rand) * 7:.1f}s;animation-delay:-{next(rand) * 12:.1f}s"/>'
        )
    return "".join(a)


def scene(mark):
    sheet = []
    parts = [backdrop(sheet), underside(sheet), platform(), rune_ring()]
    parts.extend(pad(pos) for pos in AGENTS)

    packets, targets, figures, arms = {}, {}, {}, {}
    paths = [control_path(pos) for pos in AGENTS]
    for i, pos in enumerate(AGENTS):
        holo, packets[i], targets[i] = hologram(i, pos)
        figures[i] = agent(i, pos) + holo
        x0, y0 = paths[i][0]
        arms[i] = moving(
            tentacle(paths[i], 28, 9)
            + f'<circle cx="{num(x0)}" cy="{num(y0)}" r="5" fill="{BLUE_SPEC}" filter="url(#glow)" class="pulse p{i}"/>'
            f'<circle cx="{num(x0)}" cy="{num(y0)}" r="3" fill="#fff" class="pulse p{i}"/>',
            paths[i][0],
            paths[i][-1],
            f"a{i}",
            sheet,
            6.5 + (i * 3 % 5) * 0.7,
            skew=4.5,
            curl=0.1,
        )
    order = sorted(range(len(AGENTS)), key=lambda i: sum(AGENTS[i]))
    back = [i for i in order if sum(AGENTS[i]) < 2 * C]
    front = [i for i in order if sum(AGENTS[i]) >= 2 * C]

    parts.extend(figures[i] for i in back)
    parts.append(shaft())
    parts.extend(arms[i] for i in back)
    parts.append(eye_arm(sheet))
    parts.append(kraken(mark, sheet))
    parts.extend(arms[i] for i in front)
    parts.extend(figures[i] for i in front)
    parts.append(evaluator())
    # The eye probes one network after the other.
    for i in range(len(AGENTS)):
        tx, ty = targets[i]
        parts.append(
            poly(
                [EYE, (tx - 20, ty), (tx + 20, ty)],
                "url(#beam)",
                f' class="loop beam e{i}"',
            )
        )
    parts.append(atmosphere())
    return "".join(parts), paths, packets, targets, sheet


def labels(layout, targets, bounds):
    minx, top, maxx, bottom = bounds
    a = []
    if layout == "wide":
        a.append(
            text(
                minx,
                top + 18,
                "AGENT HARNESS BENCHMARK",
                size=15,
                fill=BLUE_LIGHT,
                spacing=3,
            )
        )
        a.append(
            text(
                minx,
                top + 54,
                "repair routing and firewall",
                size=28,
                fill=INK,
                weight=700,
            )
        )
        a.append(
            text(
                minx,
                top + 80,
                "same task · isolated runs · independent checks",
                size=15,
            )
        )

        def callout(x, y, lines, target, lead):
            out = [
                text(
                    x,
                    y + 19 * k,
                    body,
                    size=15,
                    fill=INK if k == 0 else MUTED,
                    spacing=2 if k == 0 else None,
                )
                for k, body in enumerate(lines)
            ]
            out.append(
                f'<path d="{seg(lead, target)}" stroke="{DIM}" stroke-width="1"/>'
                f'<circle cx="{num(target[0])}" cy="{num(target[1])}" r="2.5" fill="{MUTED}"/>'
            )
            return out

        a += callout(
            minx,
            top + 136,
            ("01 HARNESS", "drawn as Tentaflake: holds", "every agent and the eye"),
            mark_point(0.2, 0.33),
            (minx + 244, top + 150),
        )
        right = maxx - 292
        a += callout(
            right,
            top + 18,
            ("03 EVALUATOR", "checks every network from", "outside the agent's run"),
            (EYE[0] - 24, EYE[1] - 34),
            (right + 60, top + 68),
        )
        a += callout(
            maxx - 150,
            top + 296,
            ("02 ISOLATED", "LINUX NETWORK", "one per agent"),
            (targets[2][0] + 6, targets[2][1] - 14),
            (maxx - 144, top + 342),
        )
        y = bottom - 8
        x = minx
        for colour, body in (
            (OK, "web reachable"),
            (OK, "admin blocked"),
            (BAD, "check fails"),
        ):
            a.append(
                f'<circle cx="{num(x + 7)}" cy="{num(y - 5)}" r="6.5" fill="{colour}"/>'
            )
            a.append(text(x + 22, y, body, size=15, fill=INK))
            x += 22 + len(body) * 9.1 + 26
        a.append(
            text(
                maxx,
                y,
                "illustration · synthetic · no scores",
                size=14,
                fill=DIM,
                anchor="end",
            )
        )
    else:
        a.append(
            text(
                minx,
                top + 28,
                "AGENT HARNESS BENCHMARK",
                size=27,
                fill=BLUE_LIGHT,
                spacing=4,
            )
        )
        a.append(
            text(
                minx,
                top + 84,
                "repair routing and firewall",
                size=47,
                fill=INK,
                weight=700,
            )
        )
        y = bottom + 4
        rows = (
            ("01", "the harness, drawn as Tentaflake,"),
            ("", "holds every agent and the eye"),
            ("02", "one isolated Linux network"),
            ("", "per agent, same task"),
            ("03", "the evaluator checks from"),
            ("", "outside the agent's run"),
        )
        for tag, body in rows:
            y += 60 if tag else 47
            a.append(text(minx, y, tag, size=36, fill=BLUE_LIGHT))
            a.append(text(minx + 72, y, body, size=36, fill=INK if tag else MUTED))
        y += 38
        for colour, body in (
            (OK, "web reachable"),
            (OK, "admin blocked"),
            (BAD, "check fails"),
        ):
            y += 54
            a.append(
                f'<circle cx="{num(minx + 18)}" cy="{num(y - 12)}" r="14.5" fill="{colour}"/>'
            )
            a.append(text(minx + 72, y, body, size=36, fill=INK))
        y += 74
        a.append(text(minx, y, "illustration · synthetic runs", size=27, fill=DIM))
        a.append(text(minx, y + 36, "and outcomes · no scores", size=27, fill=DIM))
        bottom = y + 36
    return a, bottom


def style(paths, packets, sheet):
    rules = [
        f"text{{font-family:{FONT}}}",
        f".loop{{animation-duration:{LOOP}s;animation-iteration-count:infinite;animation-timing-function:ease-in-out}}",
        ".arm{transform-origin:0 0;animation-iteration-count:infinite;animation-direction:alternate;animation-timing-function:ease-in-out}",
        ".breathe{animation:breathe 4s ease-in-out infinite alternate}",
        "@keyframes breathe{from{opacity:.6}to{opacity:1}}",
        ".gaze{animation:gaze 5s ease-in-out infinite alternate}",
        "@keyframes gaze{from{opacity:.55}to{opacity:1}}",
        ".stand{animation:stand 3.4s ease-in-out infinite alternate}",
        "@keyframes stand{from{transform:translateY(0)}to{transform:translateY(-1.5px)}}",
        ".visor{animation:visor 3.4s ease-in-out infinite}",
        "@keyframes visor{0%,70%{opacity:.75}85%{opacity:1}100%{opacity:.75}}",
        ".halo{transform-origin:0 0;animation:halo 160s linear infinite}",
        f"@keyframes halo{{from{{transform:translate({num(HEAD[0])}px,{num(HEAD[1])}px) scale(1.27) rotate(0deg)}}"
        f"to{{transform:translate({num(HEAD[0])}px,{num(HEAD[1])}px) scale(1.27) rotate(360deg)}}}}",
        ".rune{transform-origin:0 0;animation:rune 120s linear infinite}",
        f"@keyframes rune{{from{{transform:translate(0px,{num(CY)}px) scale(1,.5) rotate(0deg)}}"
        f"to{{transform:translate(0px,{num(CY)}px) scale(1,.5) rotate(-360deg)}}}}",
        ".mist{animation:mist 16s ease-in-out infinite alternate}",
        "@keyframes mist{from{transform:translateX(-36px)}to{transform:translateX(36px)}}",
        ".mote{opacity:.4;animation-name:mote;animation-iteration-count:infinite;animation-timing-function:linear}",
        "@keyframes mote{0%{opacity:0;transform:translateY(0)}25%{opacity:.8}100%{opacity:0;transform:translateY(-80px)}}",
        ".pulse{opacity:0;animation-duration:3.4s;animation-iteration-count:infinite;animation-timing-function:linear}",
        ".packet{animation-duration:2.6s;animation-iteration-count:infinite;animation-timing-function:linear}",
        ".shut,.beam{opacity:0}",
    ]
    rules += sheet
    for i, path in enumerate(paths):
        probe = PROBE_START + PROBE_STEP * i
        rules += [
            f".p{i}{{animation-name:p{i};animation-delay:{-0.85 * i:.2f}s}}",
            pulse_track(f"p{i}", path),
            f".e{i}{{animation-name:e{i}}}.l{i}{{animation-name:l{i}}}",
            f"@keyframes e{i}{{0%,{probe}%{{opacity:0}}{probe + 1}%,{probe + PROBE_STEP - 1}%{{opacity:1}}{probe + PROBE_STEP}%,100%{{opacity:0}}}}",
            f"@keyframes l{i}{{0%,{probe + 3}%{{opacity:0}}{probe + 5}%,97%{{opacity:1}}100%{{opacity:0}}}}",
        ]
        if packets[i]:
            done = FIXED[i]
            (rx, ry), (gx, gy), (wx, wy) = packets[i]
            rules += [
                f".q{i}{{animation-name:q{i};animation-delay:{-0.6 * i:.1f}s}}",
                f"@keyframes q{i}{{0%{{transform:translate(0,0);opacity:0}}10%{{opacity:1}}"
                f"50%{{transform:translate({num(gx - rx)}px,{num(gy - ry)}px);opacity:1}}"
                f"90%{{transform:translate({num(wx - rx)}px,{num(wy - ry)}px);opacity:1}}"
                f"100%{{transform:translate({num(wx - rx)}px,{num(wy - ry)}px);opacity:0}}}}",
                f".s{i}{{animation-name:s{i}}}.o{i}{{animation-name:o{i}}}",
                f"@keyframes s{i}{{0%,{done}%{{opacity:1}}{done + 2}%,97%{{opacity:0}}100%{{opacity:1}}}}",
                f"@keyframes o{i}{{0%,{done}%{{opacity:0}}{done + 3}%,97%{{opacity:1}}100%{{opacity:0}}}}",
            ]
    rules.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return "".join(rules)


TITLE = "Agent harness benchmark (illustration)"
DESC = (
    "Illustration with synthetic data. A dark isometric platform floats above a blue glow. From a shaft "
    "in its centre rises Tentaflake as a giant crystal kraken. Its head is the Tentaflake mark itself, "
    "large inside a faint halo, with two glowing drops as eyes and a beard of tentacles below. Its arms are "
    "the harness. Eight of them dock from above on eight dark, armoured agents, one holds the "
    "evaluator's amber eye aloft, and larger ones reach around the platform from below. Each agent "
    "stands on its own pad beside a hologram of its isolated Linux network with a client, a router, a "
    "firewall and the services web and admin. The eye probes each network in turn; lamps show whether "
    "web is reachable and admin is blocked. The task is 'repair routing and firewall'. The outcomes "
    "are invented for the picture."
)


def render(layout, mark):
    body, paths, packets, targets, sheet = scene(mark)
    minx, maxx = -N * HW - 76, N * HW + 76
    top = -386 if layout == "wide" else -446
    bottom = P(N, N)[1] + (196 if layout == "wide" else 180)
    extra, bottom = labels(layout, targets, (minx, top, maxx, bottom))
    m = 26
    x, y, w, h = minx - m, top - m, maxx - minx + 2 * m, bottom - top + 2 * m
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" '
        f'width="{num(w)}" height="{num(h)}" role="img" aria-labelledby="t d">'
        f'<title id="t">{TITLE}</title><desc id="d">{DESC}</desc>'
        f"<style>{style(paths, packets, sheet)}</style>{defs()}"
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="18" fill="url(#bg)"/>'
        f"{body}{''.join(extra)}</svg>\n"
    )


def main():
    mark = base64.b64encode((ASSETS / "tentaflake-mark.webp").read_bytes()).decode()
    for layout, name in (
        ("wide", "agent-harness.svg"),
        ("narrow", "agent-harness-narrow.svg"),
    ):
        (ASSETS / name).write_text(render(layout, mark), encoding="utf-8")


if __name__ == "__main__":
    main()
