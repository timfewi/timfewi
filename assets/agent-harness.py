#!/usr/bin/env python3
"""Render the README's benchmark scene as animated SVGs, wide and narrow.

A dark isometric platform for one agent-harness benchmark task, "repair routing and
firewall". Tentacles in the style of the Tentaflake mark rise from a shaft below the
platform and hold every agent from above: the harness. Each agent stands in its own
marked field with a hologram of its isolated Linux network (client, router, firewall,
web, admin). An independent evaluator hovers on a separate plate, attached to no
tentacle, and probes every network: web must be reachable, admin must stay blocked.

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
N, SLAB = 12, 1.4  # platform size in tiles, slab thickness in units
LOOP = 16  # seconds
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

SHAFT, SHAFT_R = (6.0, 6.0), 1.4
AGENTS = (
    (2.6, 6.0),
    (6.0, 2.6),
    (9.4, 6.0),
    (6.0, 9.4),
)  # upper left, upper right, lower right, lower left
AGENT_SCALE = 1.18
AGENT_H = 94 * AGENT_SCALE  # pixels from feet to crown
FIELD = 1.9  # half size of an agent's field in tiles
# Invented outcome per network for the picture: (web reachable, admin blocked).
OUTCOMES = ((True, True), (True, True), (True, False), (True, True))
FIXED = (20, 30, 38, 26)  # loop percentage at which each agent's fix lands
PROBE_START, PROBE_STEP = 56, 8

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


def control_path(agent):
    """3D curve from the shaft up and over, descending onto the agent's crown."""
    ax, ay = agent
    sx = SHAFT[0] + 0.45 * math.copysign(1, ax - SHAFT[0]) * (ax != SHAFT[0])
    sy = SHAFT[1] + 0.45 * math.copysign(1, ay - SHAFT[1]) * (ay != SHAFT[1])
    crown = AGENT_H / ZU + 0.02
    curve = bezier((sx, sy, -0.3), (sx, sy, 4.6), (ax, ay, 5.4), (ax, ay, crown), 36)
    return [P(*p) for p in curve]


def pulse_track(name, points):
    """Keyframes for a light running along a tentacle from the shaft to its agent."""
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


def underside():
    """What comes from below: the trunk and two arms reaching up around the platform."""
    bottom = P(N, N)[1]
    a = [f'<ellipse cx="0" cy="{num(bottom + 60)}" rx="360" ry="110" fill="{BLUE_MID}" opacity=".2" filter="url(#haze)"/>']
    trunk = bezier((0, bottom - 70), (-26, bottom + 60), (30, bottom + 180), (-6, bottom + 330), 30)
    a.append(tentacle(trunk, 176, 150, suckers=False))
    for sign, origin in ((-1, "100% 100%"), (1, "0% 100%")):
        curve = bezier((sign * 70, bottom - 30), (sign * 250, bottom + 185), (sign * 600, bottom + 120),
                       (sign * 474, 196), 44)
        a.append(f'<g class="sway" style="transform-origin:{origin};animation-delay:{-3 if sign > 0 else 0}s">'
                 f"{tentacle(curve, 64, 12)}</g>")
    # Everything below sinks into the dark it rises from.
    a.append(f'<rect x="-700" y="{num(bottom + 30)}" width="1400" height="1600" fill="url(#deep)"/>')
    return "".join(a)


def platform():
    top = [P(0, 0), P(N, 0), P(N, N), P(0, N)]
    a = [
        poly([P(0, N), P(N, N), P(N, N, -SLAB), P(0, N, -SLAB)], "url(#slabL)"),
        poly([P(N, 0), P(N, N), P(N, N, -SLAB), P(N, 0, -SLAB)], "url(#slabR)"),
        poly(top, "#161b25"),
        poly(top, "url(#floorGlow)"),
    ]
    grid = "".join(seg(P(i, 0), P(i, N)) + seg(P(0, i), P(N, i)) for i in range(1, N))
    a.append(f'<path d="{grid}" stroke="#8fb0ff" stroke-width="1" opacity=".07"/>')
    seams = "".join(seg(P(i, N, -0.3), P(i, N, -SLAB)) + seg(P(N, i, -0.3), P(N, i, -SLAB)) for i in range(2, N, 2))
    a.append(f'<path d="{seams}" stroke="#05070b" stroke-width="1.5" opacity=".7"/>')
    for i in range(1, N, 2):
        for point in (P(i, N, -0.55), P(N, i, -0.55)):
            a.append(f'<circle cx="{num(point[0])}" cy="{num(point[1])}" r="1.8" fill="{BLUE_LIGHT}" opacity=".8"/>')
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


def field(i, agent):
    """An agent's own marked field: floor tint, dashed outline and two faint back walls."""
    ax, ay = agent
    x0, y0, x1, y1 = ax - FIELD, ay - FIELD, ax + FIELD, ay + FIELD
    h = 1.5
    a = [
        poly([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)], "#8fb0ff", ' opacity=".05"'),
        poly([P(x0, y0), P(x1, y0), P(x1, y0, h), P(x0, y0, h)], "url(#wall)"),
        poly([P(x0, y0), P(x0, y1), P(x0, y1, h), P(x0, y0, h)], "url(#wall)"),
        f'<path d="M{pts([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)])}Z" stroke="#8fb0ff" stroke-width="1.3" '
        f'stroke-dasharray="7 5" fill="none" opacity=".55"/>',
    ]
    posts = "".join(
        seg(P(x, y), P(x, y, 0.45)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    )
    a.append(f'<path d="{posts}" stroke="#b9ccff" stroke-width="2" opacity=".8"/>')
    # Trace in the floor from the shaft to the field.
    edge = (ax + (SHAFT[0] - ax) * 0.52, ay + (SHAFT[1] - ay) * 0.52)
    near = (ax + (SHAFT[0] - ax) * 0.62, ay + (SHAFT[1] - ay) * 0.62)
    a.append(
        f'<path d="{seg(P(*edge), P(*near))}" stroke="{BLUE_LIGHT}" stroke-width="2" opacity=".6"/>'
    )
    return "".join(a)


def shaft():
    cx, cy = P(*SHAFT)
    rx, ry = SHAFT_R * math.sqrt(2) * HW, SHAFT_R * math.sqrt(2) * HH
    return "".join(
        (
            f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx + 9)}" ry="{num(ry + 4.5)}" fill="#0b0e15" stroke="#4a5873" stroke-width="2"/>',
            f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx)}" ry="{num(ry)}" fill="#04060b"/>',
            f'<ellipse cx="{num(cx)}" cy="{num(cy + 7)}" rx="{num(rx * 0.78)}" ry="{num(ry * 0.7)}" fill="url(#core)" class="breathe"/>',
            f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx)}" ry="{num(ry)}" fill="none" stroke="{BLUE_MID}" stroke-width="1.5" opacity=".8"/>',
        )
    )


# --- figures ---------------------------------------------------------------------


def agent(i, pos):
    """A dark, angular operator with a lit visor; the tentacle docks on its crown."""
    fx, fy = P(*pos)

    def at(points):
        return [(fx + x * AGENT_SCALE, fy + y * AGENT_SCALE) for x, y in points]

    lit, mid, dark, rim = "#465064", "#303846", "#1e232d", "#8493ad"
    a = [
        f'<ellipse cx="{num(fx)}" cy="{num(fy)}" rx="30" ry="11" fill="#000" opacity=".5"/>',
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
    # Firewall: a bar with an opening for web once the fix has landed.
    a.append(
        f'<path d="{seg(h(0.98, 0.14), h(0.98, 0.76))}{seg(h(0.98, 1.0), h(0.98, 1.22))}" stroke="#e0a26a" stroke-width="4"/>'
    )
    a.append(
        f'<path d="{seg(h(0.98, 0.76), h(0.98, 1.0))}" stroke="#e0a26a" stroke-width="4" class="loop shut s{i}"/>'
    )
    a.append(
        f'<path d="{seg(client, router)}" stroke="{INK}" stroke-width="1.4" opacity=".7"/>'
    )
    a.append(
        f'<path d="M{pts([router, gate_web, web])}" stroke="{OK}" stroke-width="2" fill="none" class="loop open o{i}"/>'
    )
    a.append(
        f'<path d="M{pts([router, gate_admin])}" stroke="{BAD}" stroke-width="2" fill="none"/>'
    )
    for point, colour in ((client, INK), (router, BLUE_LIGHT), (web, OK), (admin, DIM)):
        a.append(
            f'<circle cx="{num(point[0])}" cy="{num(point[1])}" r="3.6" fill="{colour}"/>'
        )
    a.append(
        f'<path d="M{num(gate_admin[0] - 3)} {num(gate_admin[1] - 3)}l6 6m0 -6l-6 6" stroke="{BAD}" stroke-width="1.8"/>'
    )
    a.append(
        f'<g class="loop open o{i}"><circle cx="{num(router[0])}" cy="{num(router[1])}" r="3" fill="{INK}" '
        f'class="packet k{i}"/></g>'
    )
    # Check lamps above the hologram, lit once the evaluator has probed this network.
    lamps = []
    for k, held in enumerate(OUTCOMES[i]):
        lx, ly = h(0.45 + k * 0.7, top + 0.3)
        colour = OK if held else BAD
        lamps.append(
            f'<circle cx="{num(lx)}" cy="{num(ly)}" r="9" fill="{colour}" opacity=".5" filter="url(#glow)"/>'
            f'<circle cx="{num(lx)}" cy="{num(ly)}" r="5.5" fill="{colour}"/>'
        )
    a.append(f'<g class="loop lamp l{i}">{"".join(lamps)}</g>')
    packet = (router, gate_web, web)
    return "".join(a), packet, h(0.8, top + 0.3)


def evaluator():
    """A drone on its own plate above the back corner, attached to no tentacle."""
    x, y, z, s, t = -2.5, -2.5, 1.0, 1.7, 0.22
    a = [
        f'<ellipse cx="{num(P(x + s / 2, y + s / 2, z - 0.6)[0])}" cy="{num(P(x + s / 2, y + s / 2, z - 0.6)[1])}" rx="46" ry="14" fill="{AMBER}" opacity=".16" filter="url(#haze)"/>',
        poly(
            [
                P(x, y + s, z),
                P(x + s, y + s, z),
                P(x + s, y + s, z - t),
                P(x, y + s, z - t),
            ],
            "#232a36",
        ),
        poly(
            [
                P(x + s, y, z),
                P(x + s, y + s, z),
                P(x + s, y + s, z - t),
                P(x + s, y, z - t),
            ],
            "#171b24",
        ),
        poly(
            [P(x, y, z), P(x + s, y, z), P(x + s, y + s, z), P(x, y + s, z)], "#2b3342"
        ),
        f'<path d="{seg(P(x, y + s, z), P(x + s, y + s, z))}{seg(P(x + s, y + s, z), P(x + s, y, z))}" stroke="{AMBER}" stroke-width="1.5" opacity=".8"/>',
    ]
    cx, cy = P(x + s / 2, y + s / 2, z + 1.5)

    def at(points):
        return [(cx + px * 1.35, cy + py * 1.35) for px, py in points]

    a.append('<g class="hover">')
    a.append(
        f'<ellipse cx="{num(cx)}" cy="{num(cy + 2)}" rx="54" ry="15" fill="none" stroke="{AMBER}" stroke-width="1.5" opacity=".75" transform="rotate(-10 {num(cx)} {num(cy)})"/>'
    )
    a.append(poly(at([(0, -34), (-26, -4), (0, 6)]), "#4d5769"))
    a.append(poly(at([(0, -34), (0, 6), (26, -4)]), "#363e4c"))
    a.append(poly(at([(-26, -4), (0, 28), (0, 6)]), "#2a303b"))
    a.append(poly(at([(0, 6), (0, 28), (26, -4)]), "#1c2029"))
    a.append(
        f'<path d="M{pts(at([(-26, -4), (0, -34), (26, -4)]))}" stroke="#7a879c" stroke-width="1" fill="none"/>'
    )
    a.append(
        f'<circle cx="{num(cx)}" cy="{num(cy + 5)}" r="15" fill="{AMBER}" opacity=".55" filter="url(#glow)"/>'
    )
    a.append(f'<circle cx="{num(cx)}" cy="{num(cy + 5)}" r="9.5" fill="{AMBER}"/>')
    a.append(f'<circle cx="{num(cx)}" cy="{num(cy + 5)}" r="4" fill="#fff6dd"/>')
    a.append("</g>")
    return "".join(a), (cx, cy + 5)


# --- composition -----------------------------------------------------------------


def defs(mark):
    return (
        "<defs>"
        '<radialGradient id="bg" cx="50%" cy="46%" r="75%"><stop offset="0" stop-color="#1a2438"/>'
        '<stop offset=".55" stop-color="#0e131d"/><stop offset="1" stop-color="#07090e"/></radialGradient>'
        f'<radialGradient id="floorGlow" gradientUnits="userSpaceOnUse" cx="{num(P(*SHAFT)[0])}" cy="{num(P(*SHAFT)[1])}" r="330">'
        f'<stop offset="0" stop-color="{BLUE_MID}" stop-opacity=".42"/><stop offset=".5" stop-color="{BLUE_MID}" stop-opacity=".1"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="core"><stop offset="0" stop-color="{BLUE_SPEC}"/><stop offset=".45" stop-color="{BLUE_MID}"/>'
        '<stop offset="1" stop-color="#04060b" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="slabL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#252c3a"/><stop offset="1" stop-color="#11151d"/></linearGradient>'
        '<linearGradient id="slabR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#191e29"/><stop offset="1" stop-color="#0a0d13"/></linearGradient>'
        '<linearGradient id="wall" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#8fb0ff" stop-opacity=".2"/>'
        '<stop offset="1" stop-color="#8fb0ff" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="holo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE_MID}" stop-opacity=".34"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity=".1"/></linearGradient>'
        f'<linearGradient id="trunk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE_MID}"/>'
        f'<stop offset=".45" stop-color="{BLUE_DEEP}"/><stop offset="1" stop-color="{BLUE_DEEP}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{AMBER}" stop-opacity=".05"/></linearGradient>'
        f'<linearGradient id="deep" gradientUnits="userSpaceOnUse" x1="0" y1="{num(P(N, N)[1] + 30)}" x2="0" y2="{num(P(N, N)[1] + 330)}">'
        '<stop offset="0" stop-color="#07090e" stop-opacity="0"/>'
        '<stop offset=".55" stop-color="#07090e" stop-opacity=".82"/><stop offset="1" stop-color="#07090e"/></linearGradient>'
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>'
        '<filter id="haze" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="22"/></filter>'
        "</defs>"
    )


def scene(mark):
    parts = [underside(), platform()]
    ev_svg, lens = evaluator()
    parts.append(ev_svg)
    parts.extend(field(i, pos) for i, pos in enumerate(AGENTS))

    packets, targets, front = {}, {}, []
    paths = [control_path(pos) for pos in AGENTS]
    for i, pos in enumerate(AGENTS):
        holo, packets[i], targets[i] = hologram(i, pos)
        figure = agent(i, pos) + holo
        if sum(pos) < sum(
            SHAFT
        ):  # behind the shaft: figure first, its tentacle over it
            parts.append(figure)
        else:
            front.append(figure)
    parts.append(shaft())
    cx, cy = P(*SHAFT)
    for i, path in enumerate(paths):
        parts.append(tentacle(path, 30, 9))
        x0, y0 = path[0]
        parts.append(
            f'<circle cx="{num(x0)}" cy="{num(y0)}" r="5" fill="{BLUE_SPEC}" filter="url(#glow)" class="pulse p{i}"/>'
            f'<circle cx="{num(x0)}" cy="{num(y0)}" r="3" fill="#fff" class="pulse p{i}"/>'
        )
    # The Tentaflake mark as a crystal crown over the shaft, in front of the arms' roots.
    size = 112
    parts.append(f'<ellipse cx="{num(cx)}" cy="{num(cy - 62)}" rx="62" ry="50" fill="{BLUE_MID}" opacity=".35" filter="url(#haze)"/>')
    parts.append(f'<g class="float"><image href="data:image/webp;base64,{mark}" x="{num(cx - size / 2)}" '
                 f'y="{num(cy - size - 6)}" width="{size}" height="{size}"/></g>')
    parts.extend(front)
    # Evaluator probes: one beam per network, in turn.
    for i in range(len(AGENTS)):
        tx, ty = targets[i]
        parts.append(
            poly(
                [lens, (tx - 20, ty), (tx + 20, ty)],
                "url(#beam)",
                f' class="loop beam e{i}"',
            )
        )
    return "".join(parts), paths, packets, lens


def labels(layout, lens, bounds):
    minx, top, maxx, bottom = bounds
    a = []
    if layout == "wide":
        a.append(
            text(
                minx,
                top + 16,
                "AGENT HARNESS BENCHMARK",
                size=13,
                fill=BLUE_LIGHT,
                spacing=3,
            )
        )
        a.append(
            text(
                minx,
                top + 48,
                "repair routing and firewall",
                size=25,
                fill=INK,
                weight=700,
            )
        )
        a.append(
            text(
                minx,
                top + 72,
                "same task · isolated runs · independent checks",
                size=13,
            )
        )

        def callout(x, y, anchor, lines, target, lead=None):
            out = [
                text(
                    x,
                    y + 16 * k,
                    body,
                    size=13,
                    fill=INK if k == 0 else MUTED,
                    anchor=anchor,
                    spacing=2 if k == 0 else None,
                )
                for k, body in enumerate(lines)
            ]
            start = lead or (x + (8 if anchor == "end" else -8), y - 4)
            out.append(
                f'<path d="{seg(start, target)}" stroke="{DIM}" stroke-width="1"/>'
                f'<circle cx="{num(target[0])}" cy="{num(target[1])}" r="2.5" fill="{MUTED}"/>'
            )
            return out

        a += callout(maxx - 250, top + 16, "start", ("03 INDEPENDENT EVALUATOR", "on its own plate, outside", "the harness"),
                     (lens[0] + 46, lens[1] - 10))
        arm = control_path(AGENTS[0])[20]
        a += callout(minx, top + 118, "start", ("01 HARNESS", "rises from below,", "holds every agent"),
                     (arm[0] - 12, arm[1] - 10), lead=(minx + 152, top + 132))
        field_corner = P(AGENTS[1][0] + FIELD, AGENTS[1][1] - FIELD)
        a += callout(maxx - 250, top + 100, "start", ("02 ISOLATED LINUX NETWORK", "one per agent"),
                     (field_corner[0], field_corner[1] - 4))
        y = bottom - 8
        x = minx
        for colour, body in (
            (OK, "web reachable"),
            (OK, "admin blocked"),
            (BAD, "check fails"),
        ):
            a.append(
                f'<circle cx="{num(x + 6)}" cy="{num(y - 4.5)}" r="5.5" fill="{colour}"/>'
            )
            a.append(text(x + 18, y, body, size=13, fill=INK))
            x += 18 + len(body) * 7.9 + 22
        a.append(
            text(
                maxx,
                y,
                "illustration · synthetic · no scores",
                size=12,
                fill=DIM,
                anchor="end",
            )
        )
    else:
        a.append(text(minx, top + 26, "AGENT HARNESS BENCHMARK", size=24, fill=BLUE_LIGHT, spacing=4))
        a.append(text(minx, top + 76, "repair routing and firewall", size=42, fill=INK, weight=700))
        y = bottom + 4
        rows = (("01", "the harness rises from below"), ("", "and holds every agent"),
                ("02", "one isolated Linux network"), ("", "per agent, same task"),
                ("03", "an independent evaluator,"), ("", "outside the harness"))
        for tag, body in rows:
            y += 54 if tag else 42
            a.append(text(minx, y, tag, size=32, fill=BLUE_LIGHT))
            a.append(text(minx + 64, y, body, size=32, fill=INK if tag else MUTED))
        y += 34
        for colour, body in ((OK, "web reachable"), (OK, "admin blocked"), (BAD, "check fails")):
            y += 48
            a.append(f'<circle cx="{num(minx + 16)}" cy="{num(y - 11)}" r="13" fill="{colour}"/>')
            a.append(text(minx + 64, y, body, size=32, fill=INK))
        y += 66
        a.append(text(minx, y, "illustration · synthetic runs", size=24, fill=DIM))
        a.append(text(minx, y + 32, "and outcomes · no scores", size=24, fill=DIM))
        bottom = y + 32
    return a, bottom


def style(paths, packets):
    rules = [
        f"text{{font-family:{FONT}}}",
        f".loop{{animation-duration:{LOOP}s;animation-iteration-count:infinite;animation-timing-function:ease-in-out}}",
        ".breathe{animation:breathe 4s ease-in-out infinite alternate}",
        "@keyframes breathe{from{opacity:.65}to{opacity:1}}",
        ".float{animation:float 5s ease-in-out infinite alternate}",
        "@keyframes float{from{transform:translateY(0)}to{transform:translateY(-6px)}}",
        ".hover{animation:float 3.6s ease-in-out infinite alternate}",
        ".stand{animation:stand 3.4s ease-in-out infinite alternate}",
        "@keyframes stand{from{transform:translateY(0)}to{transform:translateY(-1.5px)}}",
        ".visor{animation:visor 3.4s ease-in-out infinite}",
        "@keyframes visor{0%,70%{opacity:.75}85%{opacity:1}100%{opacity:.75}}",
        ".sway{transform-box:fill-box;animation:sway 9s ease-in-out infinite alternate}",
        "@keyframes sway{from{transform:rotate(-1.6deg)}to{transform:rotate(1.6deg)}}",
        ".sway2{transform-box:fill-box;transform-origin:50% 100%;animation:sway2 7s ease-in-out infinite alternate}",
        "@keyframes sway2{from{transform:rotate(-3deg)}to{transform:rotate(3deg)}}",
        ".pulse{opacity:0;animation-duration:3.4s;animation-iteration-count:infinite;animation-timing-function:linear}",
        ".packet{animation-duration:2.6s;animation-iteration-count:infinite;animation-timing-function:linear}",
        ".shut,.beam{opacity:0}",
    ]
    for i, path in enumerate(paths):
        done = FIXED[i]
        probe = PROBE_START + PROBE_STEP * i
        (rx, ry), (gx, gy), (wx, wy) = packets[i]
        rules += [
            f".p{i}{{animation-name:p{i};animation-delay:{-0.85 * i:.2f}s}}",
            pulse_track(f"p{i}", path),
            f".k{i}{{animation-name:k{i};animation-delay:{-0.6 * i:.1f}s}}",
            f"@keyframes k{i}{{0%{{transform:translate(0,0);opacity:0}}10%{{opacity:1}}"
            f"50%{{transform:translate({num(gx - rx)}px,{num(gy - ry)}px);opacity:1}}"
            f"90%{{transform:translate({num(wx - rx)}px,{num(wy - ry)}px);opacity:1}}"
            f"100%{{transform:translate({num(wx - rx)}px,{num(wy - ry)}px);opacity:0}}}}",
            f".s{i}{{animation-name:s{i}}}.o{i}{{animation-name:o{i}}}",
            f"@keyframes s{i}{{0%,{done}%{{opacity:1}}{done + 2}%,97%{{opacity:0}}100%{{opacity:1}}}}",
            f"@keyframes o{i}{{0%,{done}%{{opacity:0}}{done + 3}%,97%{{opacity:1}}100%{{opacity:0}}}}",
            f".e{i}{{animation-name:e{i}}}.l{i}{{animation-name:l{i}}}",
            f"@keyframes e{i}{{0%,{probe}%{{opacity:0}}{probe + 1}%,{probe + PROBE_STEP - 1}%{{opacity:1}}{probe + PROBE_STEP}%,100%{{opacity:0}}}}",
            f"@keyframes l{i}{{0%,{probe + 3}%{{opacity:0}}{probe + 5}%,97%{{opacity:1}}100%{{opacity:0}}}}",
        ]
    rules.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return "".join(rules)


TITLE = "Agent harness benchmark (illustration)"
DESC = (
    "Illustration with synthetic data. A dark isometric platform floats above a glow. From a shaft in its "
    "centre, around the crystal Tentaflake mark, blue tentacles rise and hold four dark, armoured agents "
    "from above: the harness. Two larger tentacles reach around the platform from below. Each agent stands "
    "in its own marked field beside a hologram of its isolated Linux network with a client, a router, a "
    "firewall and the services web and admin. An evaluator drone hovers on a separate plate, attached to "
    "no tentacle, and probes each network in turn; lamps show whether web is reachable and admin is "
    "blocked. The task is 'repair routing and firewall'. The outcomes are invented for the picture."
)


def render(layout, mark):
    body, paths, packets, lens = scene(mark)
    minx, maxx = -N * HW - 76, N * HW + 76
    top = -262 if layout == "wide" else -322
    bottom = P(N, N)[1] + (196 if layout == "wide" else 180)
    extra, bottom = labels(layout, lens, (minx, top, maxx, bottom))
    m = 26
    x, y, w, h = minx - m, top - m, maxx - minx + 2 * m, bottom - top + 2 * m
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" '
        f'width="{num(w)}" height="{num(h)}" role="img" aria-labelledby="t d">'
        f'<title id="t">{TITLE}</title><desc id="d">{DESC}</desc>'
        f"<style>{style(paths, packets)}</style>{defs(mark)}"
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
