#!/usr/bin/env python3
"""Render the README's "How I test agent work" banner as animated SVGs, wide and narrow.

A calm isometric illustration of one principle: same task, isolated runs, independent
checks. The original Tentaflake mark, embedded unchanged, hovers over a small plinth
and stands for the harness. One blue line runs from the plinth to each of four
identical agents. Every agent stands on its own platform with a reduced drawing of
its Linux network (client, router, firewall, one open and one blocked service). No
line joins two agents. A golden eye, the independent evaluator, floats apart on the
right without any blue line; an amber ring on each network marks what it inspects.

Nothing here is a result: no run, score, ranking or live data. Plain SVG with CSS
animation, so GitHub shows it without scripts. The base styles are the finished frame;
animations only move and brighten, so viewers without animation support or with reduced
motion requested see a complete static picture. One dark palette serves both GitHub
themes.

    python3 assets/agent-harness.py
"""

import base64
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
SANS = (
    "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
)
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
LOOP = 16  # seconds for one round of the evaluator's inspection

# The illustration is drawn around x = 0, the harness; y runs down from the banner's top.
MARK = 230  # drawn size of the Tentaflake mark's square image
PLINTH = (0, 268, 76, 38)  # centre x, centre y, half width, half height
ROW_Y = 455  # centre line of the agents' platforms
PLATFORM = (114, 57, 16)  # half width, half height, slab thickness
AGENTS_X = (-375, -125, 125, 375)
AGENT_SCALE = 0.84
AGENT_BACK = 27  # how far behind the platform's centre line an agent stands
EYE = (620, 250)

INK, MUTED = "#eef2f8", "#a9b4c6"
BLUE_MID, BLUE_LIGHT, BLUE_SPEC = "#2364de", "#62a5ff", "#d2e7ff"
CYAN, AMBER = "#5fd8e6", "#f2b84b"


def num(v):
    text = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def pts(points):
    return " ".join(f"{num(x)} {num(y)}" for x, y in points)


def poly(points, fill, extra=""):
    return f'<path d="M{pts(points)}Z" fill="{fill}"{extra}/>'


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


def diamond(cx, cy, w, h):
    return [(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)]


# --- harness ---------------------------------------------------------------------


def harness(mark):
    """The unchanged Tentaflake mark over a small lit plinth."""
    cx, cy, w, h = PLINTH
    top = diamond(cx, cy, w, h)
    depth = 12
    return "".join(
        (
            f'<ellipse cx="{cx}" cy="{cy - 110}" rx="190" ry="150" fill="{BLUE_MID}" opacity=".28" filter="url(#haze)" class="breathe"/>',
            poly(
                [top[3], top[2], (cx, cy + h + depth), (cx - w, cy + depth)], "#141b29"
            ),
            poly(
                [top[1], top[2], (cx, cy + h + depth), (cx + w, cy + depth)], "#0c111b"
            ),
            poly(top, "#182132"),
            poly(top, "url(#plinthGlow)"),
            f'<path d="M{pts(top)}Z" fill="none" stroke="{BLUE_LIGHT}" stroke-width="1.5" opacity=".8"/>',
            f'<path d="M{pts(diamond(cx, cy, w * 0.62, h * 0.62))}Z" fill="none" stroke="{CYAN}" stroke-width="1.2" opacity=".55"/>',
            # Light rising from the plinth to the mark.
            poly(
                [
                    (cx - w * 0.5, cy),
                    (cx + w * 0.5, cy),
                    (cx + 96, cy - 150),
                    (cx - 96, cy - 150),
                ],
                "url(#column)",
            ),
            f'<g class="float"><image href="data:image/webp;base64,{mark}" x="{num(cx - MARK / 2)}" '
            f'y="{num(cy - 230)}" width="{MARK}" height="{MARK}"/></g>',
        )
    )


def cable(i, x):
    """One blue line from the plinth, out along the floor's diagonal and down onto an agent's crown."""
    cx, cy, w, h = PLINTH
    side = -1 if x < 0 else 1
    t = 0.3 if abs(x) > 200 else 0.75  # outer lines leave higher up the plinth's edge
    sx, sy = cx + side * w * (1 - t), cy + h * t
    crown = ROW_Y - AGENT_BACK - 94 * AGENT_SCALE
    r = 16
    d = f"M{num(sx)} {num(sy)}H{num(x - side * r)}Q{num(x)} {num(sy)} {num(x)} {num(sy + r)}V{num(crown)}"
    track = [
        (sx, sy),
        (x - side * r, sy),
        (x - side * r * 0.3, sy + r * 0.3),
        (x, sy + r),
        (x, crown),
    ]
    lengths = [0.0]
    for a, b in zip(track, track[1:]):
        lengths.append(lengths[-1] + abs(b[0] - a[0]) + abs(b[1] - a[1]))
    frames = ["0%{opacity:0;transform:translate(0,0)}"]
    for (px, py), run in zip(track, lengths):
        pct = 6 + 86 * run / lengths[-1]
        frames.append(
            f"{pct:.0f}%{{opacity:1;transform:translate({num(px - sx)}px,{num(py - sy)}px)}}"
        )
    frames.append(
        f"100%{{opacity:0;transform:translate({num(x - sx)}px,{num(crown - sy)}px)}}"
    )
    css = f".p{i}{{animation-name:p{i};animation-delay:{-1.1 * i:.1f}s}}@keyframes p{i}{{{''.join(frames)}}}"
    svg = (
        f'<path d="{d}" fill="none" stroke="{BLUE_MID}" stroke-width="9" opacity=".3" filter="url(#glow)"/>'
        f'<path d="{d}" fill="none" stroke="{BLUE_MID}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="{d}" fill="none" stroke="{BLUE_LIGHT}" stroke-width="1.8" stroke-linecap="round"/>'
        f'<circle cx="{num(sx)}" cy="{num(sy)}" r="5" fill="{BLUE_SPEC}" stroke="{BLUE_MID}" stroke-width="2"/>'
        f'<circle cx="{num(sx)}" cy="{num(sy)}" r="4" fill="#fff" class="pulse p{i}"/>'
    )
    return svg, css


# --- agents ----------------------------------------------------------------------


def platform(i, cx):
    """An agent's own floating platform with a reduced drawing of its Linux network."""
    w, h, depth = PLATFORM
    cy = ROW_Y
    top = diamond(cx, cy, w, h)
    y0 = cy + 10  # the network's main line across the platform
    router, gate = (cx - 28, y0), (cx + 5, y0 + 4)
    web, admin = (cx + 50, y0 - 8), (cx + 32, y0 + 15)
    wall = [(cx - 7, y0 + 11), (cx + 17, y0 - 1), (cx + 17, y0 - 19), (cx - 7, y0 - 7)]

    def disc(point, rx, fill, extra=""):
        return f'<ellipse cx="{num(point[0])}" cy="{num(point[1])}" rx="{rx}" ry="{rx / 2}" fill="{fill}"{extra}/>'

    return "".join(
        (
            f'<ellipse cx="{cx}" cy="{cy + h + 34}" rx="{w * 0.8}" ry="16" fill="{BLUE_MID}" opacity=".22" filter="url(#haze)"/>',
            poly(
                [top[3], top[2], (cx, cy + h + depth), (cx - w, cy + depth)],
                "url(#slabL)",
            ),
            poly(
                [top[1], top[2], (cx, cy + h + depth), (cx + w, cy + depth)],
                "url(#slabR)",
            ),
            poly(top, "#1b2333"),
            f'<path d="M{pts(top[1:])}" fill="none" stroke="#51607c" stroke-width="2"/>',
            f'<path d="M{pts(top)}Z" fill="none" stroke="#44516a" stroke-width="1.2"/>',
            f'<path d="M{pts(diamond(cx, cy, w * 0.88, h * 0.88))}Z" fill="none" stroke="#8fb0ff" stroke-width="1.3" '
            f'stroke-dasharray="7 6" opacity=".5"/>',
            # What the evaluator inspects.
            f'<ellipse cx="{num(cx - 4)}" cy="{num(y0 + 2)}" rx="76" ry="24" fill="{AMBER}" opacity=".07"/>',
            f'<ellipse cx="{num(cx - 4)}" cy="{num(y0 + 2)}" rx="76" ry="24" fill="none" stroke="{AMBER}" '
            f'stroke-width="1.6" opacity=".6" class="loop scan c{i}"/>',
            # Client, router, firewall; one service open, one blocked.
            f'<path d="M{num(cx - 62)} {num(y0)}H{num(router[0])}" stroke="{INK}" stroke-width="2" opacity=".75"/>',
            f'<path d="M{pts([router, gate])}" stroke="{CYAN}" stroke-width="2.5"/>',
            f'<path d="M{pts([gate, admin])}" stroke="#8b97aa" stroke-width="2" stroke-dasharray="3 4"/>',
            disc(admin, 7, "#1b2333", ' stroke="#8b97aa" stroke-width="2"'),
            poly(wall, "#8696b3"),
            f'<path d="M{pts(wall[2:])}" stroke="#c6d2e8" stroke-width="1.5"/>',
            f'<path d="M{pts([(cx + 9, y0 - 4), web])}" stroke="{CYAN}" stroke-width="2.5"/>',
            disc((cx - 62, y0), 7, INK),
            disc(router, 9, BLUE_LIGHT),
            disc(web, 8, CYAN),
        )
    )


def agent(i, fx):
    """A dark, angular operator with a lit visor; the harness line docks on its crown."""
    fy = ROW_Y - AGENT_BACK

    def at(points):
        return [(fx + x * AGENT_SCALE, fy + y * AGENT_SCALE) for x, y in points]

    lit, mid, dark, rim = "#4a556a", "#333c4b", "#1f242e", "#8a99b3"
    visor = at([(-10, -87), (10, -87), (9, -82), (-9, -82)])
    return "".join(
        (
            f'<ellipse cx="{fx}" cy="{fy}" rx="21" ry="8" fill="#000" opacity=".5"/>',
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
            f'<ellipse cx="{fx}" cy="{num(fy - 94 * AGENT_SCALE)}" rx="8" ry="3.4" fill="#0b0e15" stroke="{BLUE_LIGHT}" stroke-width="1.5"/>',
        )
    )


# --- evaluator -------------------------------------------------------------------


def evaluator():
    """The independent evaluator: a golden eye floating apart, tied to nothing."""
    ex, ey = EYE

    def at(points):
        return [(ex + px, ey + py) for px, py in points]

    return (
        f'<ellipse cx="{ex}" cy="{ey}" rx="92" ry="80" fill="{AMBER}" opacity=".2" filter="url(#haze)"/>'
        '<g class="hover">'
        f'<ellipse cx="{ex}" cy="{ey + 2}" rx="60" ry="17" fill="none" stroke="{AMBER}" stroke-width="1.6" '
        f'opacity=".75" transform="rotate(-12 {ex} {ey})"/>'
        f'<circle cx="{ex}" cy="{ey}" r="38" fill="url(#orb)" stroke="#8a7650" stroke-width="1.3"/>'
        f"{poly(at([(-38, -4), (-28, -26), (-6, -38), (18, -35), (35, -17), (38, -3), (21, -18), (0, -23), (-21, -17)]), '#3c4350')}"
        f"{poly(at([(-38, 4), (-23, 18), (0, 24), (23, 17), (38, 3), (32, 22), (13, 36), (-11, 37), (-31, 24)]), '#181c24')}"
        f'<circle cx="{ex}" cy="{ey}" r="23" fill="{AMBER}" opacity=".6" filter="url(#glow)" class="gaze"/>'
        f'<circle cx="{ex}" cy="{ey}" r="16.5" fill="url(#iris)"/>'
        f'<path d="M{ex} {ey - 14}Q{ex + 6.5} {ey} {ex} {ey + 14}Q{ex - 6.5} {ey} {ex} {ey - 14}Z" fill="#160d02"/>'
        f'<circle cx="{ex - 5.5}" cy="{ey - 6.5}" r="2.6" fill="#fff6dd"/>'
        "</g>"
    )


# --- composition -----------------------------------------------------------------


def defs():
    return (
        "<defs>"
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1526"/>'
        '<stop offset=".55" stop-color="#0c1019"/><stop offset="1" stop-color="#15181e"/></linearGradient>'
        '<radialGradient id="vignette" cx="58%" cy="48%" r="70%"><stop offset="0" stop-color="#0c1019" stop-opacity="0"/>'
        '<stop offset=".6" stop-color="#0c1019" stop-opacity=".35"/><stop offset="1" stop-color="#090c12" stop-opacity=".95"/></radialGradient>'
        f'<radialGradient id="plinthGlow"><stop offset="0" stop-color="{BLUE_LIGHT}" stop-opacity=".7"/>'
        f'<stop offset="1" stop-color="{BLUE_MID}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="column" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{BLUE_LIGHT}" stop-opacity=".3"/>'
        f'<stop offset="1" stop-color="{BLUE_LIGHT}" stop-opacity="0"/></linearGradient>'
        '<linearGradient id="slabL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#262e3d"/><stop offset="1" stop-color="#121720"/></linearGradient>'
        '<linearGradient id="slabR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a202c"/><stop offset="1" stop-color="#0b0e15"/></linearGradient>'
        '<radialGradient id="orb" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#535b6b"/>'
        '<stop offset=".6" stop-color="#1e232d"/><stop offset="1" stop-color="#0b0d12"/></radialGradient>'
        f'<radialGradient id="iris"><stop offset="0" stop-color="#fff0c4"/><stop offset=".5" stop-color="{AMBER}"/>'
        '<stop offset="1" stop-color="#7d4c0c"/></radialGradient>'
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>'
        '<filter id="haze" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="22"/></filter>'
        "</defs>"
    )


def backdrop(x, y, w, h):
    """Rounded dark card with a faint isometric floor grid that fades towards the edges."""
    lines = []
    for k in range(-40, 60):
        x0 = x + k * 96
        lines.append(
            f"M{num(x0)} {num(y)}l{num(2 * h)} {num(h)}M{num(x0)} {num(y)}l{num(-2 * h)} {num(h)}"
        )
    return (
        f'<clipPath id="card"><rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="20"/></clipPath>'
        f'<g clip-path="url(#card)"><rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" fill="url(#bg)"/>'
        f'<path d="{"".join(lines)}" stroke="#8fb0ff" stroke-width="1" opacity=".07"/>'
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" fill="url(#vignette)"/></g>'
    )


def illustration(mark, label):
    """Harness, lines, agents and evaluator around x = 0, with labels at the given size."""
    parts, css = [harness(mark)], []
    for i, x in enumerate(AGENTS_X):
        parts.append(platform(i, x))
    for i, x in enumerate(AGENTS_X):
        svg, rule = cable(i, x)
        parts.append(svg)
        css.append(rule)
    parts.extend(agent(i, x) for i, x in enumerate(AGENTS_X))
    parts.append(evaluator())

    step = label * 1.25
    blue, gold = "#a9c4f5", "#f0cf8d"
    cx, cy, w, _ = PLINTH
    parts.append(
        f'<path d="M{num(cx + 112)} {num(cy - 118)}h26" stroke="{blue}" stroke-width="1.5" opacity=".7"/>'
        + text(cx + 150, cy - 118 + label * 0.35, "HARNESS", label, blue, spacing=3)
    )
    parts.append(
        text(
            0,
            ROW_Y + PLATFORM[1] + PLATFORM[2] + 22 + label,
            "ISOLATED LINUX NETWORKS",
            label,
            blue,
            anchor="middle",
            spacing=3,
        )
    )
    ex, ey = EYE
    parts.append(
        text(
            ex, ey + 68 + label, "INDEPENDENT", label, gold, anchor="middle", spacing=3
        )
    )
    parts.append(
        text(
            ex,
            ey + 68 + label + step,
            "EVALUATOR",
            label,
            gold,
            anchor="middle",
            spacing=3,
        )
    )
    return "".join(parts), "".join(css)


def style(cable_css):
    rules = [
        f".loop{{animation-duration:{LOOP}s;animation-iteration-count:infinite;animation-timing-function:ease-in-out}}",
        ".breathe{animation:breathe 5s ease-in-out infinite alternate}",
        "@keyframes breathe{from{opacity:.2}to{opacity:.34}}",
        ".float{animation:float 6s ease-in-out infinite alternate}",
        "@keyframes float{from{transform:translateY(0)}to{transform:translateY(-5px)}}",
        ".hover{animation:float 4.6s ease-in-out infinite alternate}",
        ".gaze{animation:gaze 4s ease-in-out infinite alternate}",
        "@keyframes gaze{from{opacity:.45}to{opacity:.85}}",
        ".visor{animation:gaze 3.6s ease-in-out infinite alternate}",
        ".pulse{opacity:0;animation-duration:4.4s;animation-iteration-count:infinite;animation-timing-function:linear}",
        cable_css,
    ]
    share = 100 / len(AGENTS_X)
    for i in range(len(AGENTS_X)):
        a, b = share * i, share * (i + 1)
        rules.append(
            f".c{i}{{animation-name:c{i}}}@keyframes c{i}{{0%,{a:.0f}%{{opacity:.35;stroke-width:1.6px}}"
            f"{a + 5:.0f}%,{b - 5:.0f}%{{opacity:1;stroke-width:2.6px}}{b:.0f}%,100%{{opacity:.35;stroke-width:1.6px}}}}"
        )
    rules.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return "".join(rules)


TITLE = "How I test agent work"
TAGLINE = ("Same task.", "Isolated runs.", "Independent checks.")
DESC = (
    "Illustration, not a recording or a result. Title: How I test agent work. Same task. Isolated runs. "
    "Independent checks. On a dark background the Tentaflake mark, a symmetric cluster of blue crystals, "
    "hovers over a small lit plinth and stands for the harness. One blue line runs from the plinth to each "
    "of four identical dark agents. Every agent stands on its own separate platform, marked with a drawing "
    "of its isolated Linux network: a client, a router, a firewall, one open service and one blocked "
    "service. No line joins two agents. On the right a golden eye, the independent evaluator, floats apart "
    "from the harness with no blue line to it; an amber ring on each network marks what it inspects."
)


def render(layout, mark):
    if layout == "wide":
        w, h, origin, label = 1800, 600, (1030, 0), 24
        body, cable_css = illustration(mark, label)
        words = [
            f'<rect x="84" y="150" width="64" height="5" rx="2.5" fill="{BLUE_LIGHT}"/>',
            text(80, 240, "How I test", 76, INK, SANS, weight=700),
            text(80, 322, "agent work", 76, INK, SANS, weight=700),
        ]
        words += [
            text(84, 384 + 40 * k, line, 31, MUTED, SANS)
            for k, line in enumerate(TAGLINE)
        ]
    else:
        w, h, origin, label = 1300, 880, (522, 262), 34
        body, cable_css = illustration(mark, label)
        words = [
            f'<rect x="54" y="50" width="76" height="6" rx="3" fill="{BLUE_LIGHT}"/>',
            text(50, 142, TITLE, 88, INK, SANS, weight=700),
            text(54, 204, " ".join(TAGLINE), 42, MUTED, SANS),
        ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d">'
        f'<title id="t">{TITLE}</title><desc id="d">{DESC}</desc>'
        f"<style>{style(cable_css)}</style>{defs()}{backdrop(0, 0, w, h)}"
        f'<g transform="translate({origin[0]} {origin[1]})">{body}</g>{"".join(words)}</svg>\n'
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
