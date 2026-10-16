#!/usr/bin/env python3
"""Render the README's agent office as two animated SVGs, one per colour scheme.

A small isometric office in the spirit of the agent world on timwitter.com: three
agents take a task from the board, code at their desk, deploy at the rack, check the
dashboard and file the result, while the Tentaflake hub reaches every station.
Plain SVG and CSS animation, so GitHub shows it without scripts.

    python3 assets/agent-office.py
"""

import base64
import math
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
COLS, ROWS = 16, 11
HW, HH, ZU = 32, 16, 32
WALL, THICK, SLAB = 2.4, 0.3, 0.35
SPEED = 1.7  # tiles per second
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "light": dict(paper=(247, 248, 250), ink=(28, 34, 43), muted=(86, 95, 109), accent=(41, 67, 214)),
    "dark": dict(paper=(21, 25, 31), ink=(237, 240, 245), muted=(177, 186, 200), accent=(163, 180, 255)),
}
# Colours of the mascots on timwitter.com.
RUNTIMES = {
    "hermes": dict(suit=(55, 62, 76), shell=(28, 31, 40), skin=(220, 187, 165), brand=(91, 119, 162)),
    "zeroclaw": dict(suit=(57, 91, 127), shell=(96, 155, 197), skin=(204, 219, 225), brand=(97, 151, 197)),
    "openclaw": dict(suit=(126, 58, 49), shell=(192, 87, 66), skin=(226, 200, 172), brand=(183, 87, 72)),
}
CODE = ((163, 180, 255), (126, 200, 160), (230, 200, 120), (177, 186, 200))

# Desks along x; each agent sits in front of its desk, facing the monitor.
DESK_Y, DESK_D, DESK_W, SEAT_Y = 4.4, 0.8, 1.8, 5.75
DESKS = (2.6, 6.4, 10.2)
AISLES = (1.75, 5.4, 9.2, 13.0)
HUB = (12.6, 9.4)
RACKS = (11.0, 12.1, 13.2, 14.3)

# Each agent: runtime, desk, its spots at the board (y), dashboard (x) and rack (x),
# the back lane it walks along, the loop of work and a phase offset in seconds.
AGENTS = (
    dict(runtime="hermes", desk=0, board=2.0, dash=4.6, rack=11.5, lane=2.45, delay=0,
         plan=(("code", 6.0), ("pick", 1.6), ("code", 5.0), ("deploy", 2.6), ("check", 2.2), ("file", 1.2))),
    dict(runtime="zeroclaw", desk=1, board=2.9, dash=6.2, rack=12.9, lane=2.75, delay=-13,
         plan=(("code", 4.5), ("pick", 1.4), ("code", 5.5), ("deploy", 3.0), ("check", 2.4), ("file", 1.2))),
    dict(runtime="openclaw", desk=2, board=3.8, dash=3.0, rack=14.3, lane=3.05, delay=-27,
         plan=(("code", 5.0), ("pick", 1.4), ("code", 4.0), ("deploy", 2.8), ("check", 2.2), ("file", 1.2))),
)
STATION = {"code": "seat", "pick": "board", "file": "board", "deploy": "rack", "check": "dash"}


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def css(color, alpha=1.0):
    r, g, b = (max(0, min(255, round(v))) for v in color)
    return f"#{r:02x}{g:02x}{b:02x}" if alpha >= 1 else f"rgba({r},{g},{b},{alpha:g})"


def num(value):
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def P(x, y, z=0.0):
    return (x - y) * HW, (x + y) * HH - z * ZU


def poly(points, fill):
    return f'<path d="M{" ".join(f"{num(x)} {num(y)}" for x, y in points)}Z" fill="{fill}"/>'


def box(x, y, z, w, d, h, m):
    left = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    right = [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)]
    top = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    return poly(left, m["left"]) + poly(right, m["right"]) + poly(top, m["top"])


def plane(kind, x, y, z):
    """A group whose units are tiles on a floor or wall plane; on walls w grows downwards."""
    ex, ey = (num(v) for v in P(x, y, z))
    matrix = {"floor": "32 16 -32 16", "xz": "32 16 0 32", "yz": "32 -16 0 32"}[kind]
    return f'<g transform="matrix({matrix} {ex} {ey})">'


def palette(theme):
    paper, ink, accent = theme["paper"], theme["ink"], theme["accent"]
    dark = sum(paper) / 3 < 128

    def m(base):
        return dict(
            top=css(mix(base, ink, 0.1) if dark else base),
            left=css(mix(base, paper if dark else ink, 0 if dark else 0.07)),
            right=css(mix(base, (0, 0, 0) if dark else ink, 0.22 if dark else 0.15)),
        )

    def tinted(t):
        return mix(paper, ink, t)

    screen = mix(paper, (0, 0, 0), 0.55) if dark else mix(ink, paper, 0.06)
    return dict(
        dark=dark, ink=css(ink), muted=css(theme["muted"]), paper=css(paper),
        accent=css(accent), accent_soft=css(accent, 0.18), seam=css(ink, 0.07), line=css(ink, 0.2),
        floor=css(tinted(0.03)), carpet=css(mix(tinted(0.05), accent, 0.1)),
        rug=css(mix(tinted(0.04), accent, 0.2)), server_floor=css(tinted(0.0 if dark else 0.22)),
        slab=m(tinted(0.0 if dark else 0.18)), wall=m(tinted(0.1 if dark else 0.04)),
        desk=m(tinted(0.3 if dark else 0.02)), leg=m(tinted(0.35)), rack=m(tinted(0.0 if dark else 0.62)),
        metal=m(tinted(0.4)), sofa=m(mix(tinted(0.28), accent, 0.32)), table=m(tinted(0.34 if dark else 0.0)),
        pot=m(tinted(0.25 if dark else 0.15)), leaf=m(mix(tinted(0.3), (86, 160, 104), 0.6)),
        screen=css(screen), panel=css(mix(screen, paper, 0.3 if dark else 0.55)),
        board=css(tinted(0.16 if dark else 0.0)), slot=css(mix(screen, paper, 0.1)),
        sky=css(mix(paper, accent, 0.18) if dark else mix(tinted(0.04), accent, 0.22)),
        frame=css(ink, 0.35), note=css(mix(paper, (250, 210, 90), 0.7 if dark else 0.8)),
        done=css(mix(paper, (86, 160, 104), 0.45 if dark else 0.35)),
        orb=css((235, 240, 250) if dark else (250, 206, 110)),
        tentacle=m(mix((43, 113, 206), tinted(0.26 if dark else 0.5), 0.18)),
        highlight=css(mix(paper, (129, 183, 228), 0.35), 0.5), core=css(accent, 0.7),
        shadow=css(ink, 0.16), surface=css(mix(paper, ink, 0.08) if dark else (255, 255, 255)),
        outline=css(ink, 0.35) if dark else "none", ink_rgb=ink,
        hue={name: css(mix(r["brand"], paper if dark else ink, 0.35 if dark else 0.12)) for name, r in RUNTIMES.items()},
    )


# --- The agents' routes -------------------------------------------------------------


def station_path(agent, station):
    """Points from the agent's back lane to its spot at a station, and its facing there."""
    lane = agent["lane"]
    if station == "board":
        y = agent["board"]
        return [(AISLES[0], lane), (AISLES[0], y), (0.95, y)], "-x"
    if station == "dash":
        x = agent["dash"]
        return [(x, lane), (x, 0.95)], "-y"
    if station == "rack":
        x = agent["rack"]
        return [(x, lane), (x, 1.85)], "-y"
    raise ValueError(station)


def seat(agent):
    return DESKS[agent["desk"]] + DESK_W / 2, SEAT_Y


def route(agent, pos, here, there, target):
    """Walk from one station to the next along aisles and the agent's back lane."""
    lane, (sx, sy) = agent["lane"], seat(agent)
    left, right = AISLES[agent["desk"]], AISLES[agent["desk"] + 1]
    if here == "seat":
        aisle = min((left, right), key=lambda a: abs(a - target[0]))
        points = [(aisle, sy), (aisle, lane)]
    elif here == "board":
        points = [(AISLES[0], pos[1]), (AISLES[0], lane)]
    else:
        points = [(pos[0], lane)]
    if there == "seat":
        aisle = min((left, right), key=lambda a: abs(a - points[-1][0]))
        points += [(aisle, lane), (aisle, sy), (sx, sy)]
    else:
        points += station_path(agent, there)[0]
    return points


def simplify(start, points):
    """Drop repeated points and middle points of straight runs, so each leg is one move."""
    out = [start]
    for p in points:
        if math.dist(p, out[-1]) < 1e-9:
            continue
        if len(out) >= 2:
            a, b = out[-2], out[-1]
            if (a[0] == b[0] == p[0]) or (a[1] == b[1] == p[1]):
                out[-1] = p
                continue
        out.append(p)
    return out[1:]


FACING = {"+x": ("front", 1), "+y": ("front", -1), "-x": ("back", -1), "-y": ("back", 1)}
POSES = {"walk-front": "pf", "walk-back": "pb", "work": "pw"}


def heading(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if abs(dx) >= abs(dy):
        return "+x" if dx > 0 else "-x"
    return "+y" if dy > 0 else "-y"


def timeline(agent):
    """Segments (t0, t1, p0, p1, pose, flip, activity) of one loop, back to the start."""
    segments, t = [], 0.0
    here, pos = "seat", seat(agent)

    def walk(path):
        nonlocal t, pos
        for point in simplify(pos, path):
            duration = math.dist(pos, point) / SPEED
            if duration < 1e-6:
                continue
            view, flip = FACING[heading(pos, point)]
            segments.append((t, t + duration, pos, point, "walk-" + view, flip, None))
            t, pos = t + duration, point

    for activity, seconds in agent["plan"]:
        station = STATION[activity]
        if station == "seat":
            facing = "-y"
            if here != "seat":
                walk(route(agent, pos, here, "seat", seat(agent)))
        else:
            points, facing = station_path(agent, station)
            walk(route(agent, pos, here, station, points[-1]))
        segments.append((t, t + seconds, pos, pos, "work", FACING[facing][1], activity))
        t += seconds
        here = station
    walk(route(agent, pos, here, "seat", seat(agent)))
    assert math.dist(pos, seat(agent)) < 1e-9
    return segments, t


def pct(t, total):
    return num(100 * t / total) + "%" if t < total else "100%"


def step_track(name, segments, total, value):
    """Keyframes holding value(segment) for each segment; used with steps(1, end)."""
    frames, last = [], None
    for segment in segments:
        current = value(segment)
        if current != last:
            frames.append(f"{pct(segment[0], total)}{{{current}}}")
            last = current
    frames.append(f"100%{{{last}}}")
    return f"@keyframes {name}{{{''.join(frames)}}}"


def move_track(name, segments, total):
    frames = []
    for t0, _, p0, *_ in segments:
        x, y = P(*p0)
        frames.append(f"{pct(t0, total)}{{transform:translate({num(x)}px,{num(y)}px)}}")
    x, y = P(*segments[0][2])
    frames.append(f"100%{{transform:translate({num(x)}px,{num(y)}px)}}")
    return f"@keyframes {name}{{{''.join(frames)}}}"


# --- Drawing ------------------------------------------------------------------------


def figure(runtime, view, mode, pal):
    """One pose of an agent facing screen-right, drawn around its feet."""
    # A dark office lifts the mascots a little, so a dark suit still reads against the floor.
    r = {part: mix(RUNTIMES[runtime][part], pal["ink_rgb"], 0.16 if pal["dark"] else 0)
         for part in ("suit", "shell", "skin")}
    suit, shell, skin = css(r["suit"]), css(r["shell"]), css(r["skin"])
    suit_dark, shell_dark = css(mix(r["suit"], (0, 0, 0), 0.3)), css(mix(r["shell"], (0, 0, 0), 0.25))
    boot = "#20262f"
    front, walking = view == "front", mode == "walk"
    claws = runtime != "hermes"
    stroke = f' stroke="{pal["outline"]}" stroke-width=".6"' if pal["dark"] else ""

    def arm(cls, x, near):
        color = suit if near else suit_dark
        length = 13 if walking else 9
        hand_y = -30 + length
        if claws:
            hand = (f'<circle cx="{num(x + 2.2)}" cy="{hand_y}" r="3.1" fill="{shell if near else shell_dark}"/>'
                    f'<path d="M{num(x + 0.4)} {hand_y + 1.5}l-1 3M{num(x + 4)} {hand_y + 1.5}l1 3" '
                    f'stroke="{shell if near else shell_dark}" stroke-width="1.4" stroke-linecap="round"/>')
        else:
            hand = f'<circle cx="{num(x + 2.2)}" cy="{hand_y}" r="2.5" fill="{skin}"/>'
        return (f'<g class="{cls}"><rect x="{num(x)}" y="-30" width="4.4" height="{length}" rx="2.2" '
                f'fill="{color}"/>{hand}</g>')

    def leg(cls, x, near):
        toe = 1.2 if front else -0.6
        return (f'<g class="{cls}"><rect x="{num(x)}" y="-15" width="5" height="13" rx="2" '
                f'fill="{suit if near else suit_dark}"/><ellipse cx="{num(x + 2.5 + toe)}" cy="-2" rx="3.6" '
                f'ry="2.1" fill="{boot}"/></g>')

    leg_far, leg_near = ("ls", "lt") if walking else ("", "")
    arm_far, arm_near = ("at", "as") if walking else ("ty", "ty2")
    parts = [arm(arm_far, -9.4, False), leg(leg_far, -5.2, False), leg(leg_near, 0.4, True)]
    parts.append(f'<g{stroke}><rect x="-2.4" y="-35" width="4.8" height="6" rx="1.5" fill="{skin}"/>'
                 f'<rect x="-7.5" y="-31" width="15" height="17" rx="5" fill="{suit}"/>'
                 f'<path d="M1.5 -31h1a5 5 0 0 1 5 5v7a5 5 0 0 1-5 5h-1z" fill="{suit_dark}" opacity=".55"/>')
    if claws:
        parts.append(f'<circle cx="-6.5" cy="-28.5" r="3.3" fill="{shell_dark}"/>'
                     f'<circle cx="6.5" cy="-28.5" r="3.3" fill="{shell}"/>')
    parts.append("</g>")
    parts.append(arm(arm_near, 5.0, True))

    head = [f'<circle cx="0" cy="-41" r="10" fill="{shell}"/>']
    if runtime == "hermes":
        head.insert(0, f'<rect x="-10" y="-42" width="{8 if front else 20}" height="11" rx="4" fill="{shell}"/>')
    if runtime == "zeroclaw":
        head.append(f'<path d="M-6.5 -47.5L-9 -58.5L-1.5 -50Z" fill="{shell}"/>'
                    f'<path d="M1.5 -50L4.5 -60L7 -47Z" fill="{shell_dark}"/>')
    if runtime == "openclaw":
        head.append(f'<path d="M-3 -50Q-5 -57 -9.5 -59M3 -50Q4 -57 8.5 -60.5" fill="none" stroke="{shell}" '
                    f'stroke-width="1.6" stroke-linecap="round"/><circle cx="-9.5" cy="-59" r="1.9" fill="{shell}"/>'
                    f'<circle cx="8.5" cy="-60.5" r="1.9" fill="{shell}"/>')
    if front:
        head.append(f'<ellipse cx="3.6" cy="-40" rx="6.2" ry="7" fill="{skin}"/>'
                    f'<circle cx="6.6" cy="-41" r="1.15" fill="{boot}"/><circle cx="2.6" cy="-41" r="1.15" fill="{boot}"/>')
        if runtime == "hermes":
            head.append(f'<path d="M-4 -49a10 10 0 0 1 14 7q-6 -3 -14 -2z" fill="{shell}"/>')
        if runtime == "zeroclaw":
            head.append(f'<circle cx="-4.5" cy="-40" r="2.6" fill="{shell_dark}"/>')
    elif runtime == "zeroclaw":
        head.append(f'<circle cx="-8" cy="-40" r="2.4" fill="{shell_dark}"/><circle cx="8" cy="-40" r="2.4" fill="{shell_dark}"/>')
    parts.append(f'<g{stroke}>{"".join(head)}</g>')
    return f'<g class="{"bob" if walking else "nod"}">{"".join(parts)}</g>'


ICONS = {
    "code": '<path d="M-4 -4L-8 0L-4 4M4 -4L8 0L4 4M1.5 -5L-1.5 5"/>',
    "deploy": '<path d="M0 5V-5M-4 -1L0 -5L4 -1"/>',
    "check": '<path d="M-5 0L-1.5 3.5L5 -4"/>',
    "task": '<rect x="-4.5" y="-5" width="9" height="10" rx="1.5"/><path d="M-2 -1.5H2M-2 1.5H1"/>',
}
ACTIVITY_ICON = {"code": "code", "deploy": "deploy", "check": "check", "pick": "task", "file": "task"}


def office(pal, mark):
    out, style = [], []
    floor_plane = plane("floor", 0, 0, 0)

    # Slab, floor zones and tile seams.
    out.append(box(0, 0, -SLAB, COLS, ROWS, SLAB, pal["slab"]))
    out.append(floor_plane + f'<rect width="{COLS}" height="{ROWS}" fill="{pal["floor"]}"/>'
               f'<rect x="1.3" y="3.9" width="12.3" height="2.7" rx=".2" fill="{pal["carpet"]}"/>'
               f'<rect x="10.6" width="{num(COLS - 10.6)}" height="2.5" fill="{pal["server_floor"]}"/>'
               f'<rect x="{num(HUB[0] - 1.7)}" y="{num(HUB[1] - 1.7)}" width="3.4" height="3.4" rx=".35" fill="{pal["rug"]}"/>'
               f'<path d="{"".join(f"M{i} 0V{ROWS}" for i in range(1, COLS))}{"".join(f"M0 {j}H{COLS}" for j in range(1, ROWS))}" '
               f'stroke="{pal["seam"]}" stroke-width=".7" vector-effect="non-scaling-stroke"/></g>')

    # Walls and what hangs on them.
    out.append(box(-THICK, -THICK, 0, COLS + THICK, THICK, WALL, pal["wall"]))
    out.append(box(-THICK, 0, 0, THICK, ROWS, WALL, pal["wall"]))
    thin = 'vector-effect="non-scaling-stroke" stroke-width=".8"'
    text = f'font-family="{FONT}" fill="{pal["muted"]}"'

    # Dashboard on the right wall: a line chart that redraws and breathing bars.
    out.append(plane("xz", 2.0, 0.01, 1.95)
               + f'<rect width="5.2" height="1.2" rx=".06" fill="{pal["panel"]}" stroke="{pal["frame"]}" {thin}/>'
               f'<text x=".14" y=".22" font-size=".14" {text}>dashboard · 3 agents · healthy</text>'
               f'<path d="M.15 1.02H2.6" stroke="{pal["line"]}" {thin}/>'
               f'<path class="chart" pathLength="1" d="M.18 .9L.5 .78L.8 .84L1.1 .6L1.4 .66L1.7 .48L2 .55L2.3 .38L2.55 .42" '
               f'fill="none" stroke="{pal["accent"]}" stroke-width="1.4" vector-effect="non-scaling-stroke" '
               f'stroke-linejoin="round"/>'
               + "".join(f'<rect class="bar" style="animation-delay:-{i * 0.37:.2f}s" x="{num(2.9 + i * 0.3)}" '
                         f'y="{num(1.02 - h)}" width=".19" height="{num(h)}" fill="{pal["accent"] if i % 3 else pal["done"]}" '
                         f'opacity=".8"/>' for i, h in enumerate((0.45, 0.62, 0.38, 0.7, 0.55, 0.66, 0.5)))
               + "".join(f'<circle cx="{num(4.95 - i * 0.14)}" cy=".17" r=".035" fill="{pal["done"]}"/>' for i in range(3))
               + "</g>")
    style.append(".chart{stroke-dasharray:1 1;animation:chart 6s ease-in-out infinite}"
                 "@keyframes chart{0%{stroke-dashoffset:1}55%,100%{stroke-dashoffset:0}}"
                 ".bar{transform-box:fill-box;transform-origin:50% 100%;animation:bar 2.6s ease-in-out infinite alternate}"
                 "@keyframes bar{from{transform:scaleY(.45)}to{transform:scaleY(1)}}")

    def window(kind, x, y, width):
        return (plane(kind, x, y, 1.95) + f'<rect width="{width}" height="1.1" fill="{pal["sky"]}"/>'
                f'<circle cx="{num(width * 0.72)}" cy=".32" r=".13" fill="{pal["orb"]}"/>'
                f'<path d="M{num(width / 2)} 0V1.1M0 .55H{width}" stroke="{pal["frame"]}" {thin}/>'
                f'<rect width="{width}" height="1.1" fill="none" stroke="{pal["frame"]}" stroke-width="1.6" '
                f'vector-effect="non-scaling-stroke"/></g>')

    out.append(window("xz", 8.3, 0.01, 1.8))
    out.append(window("yz", 0.01, 9.4, 2.6))
    out.append(plane("xz", 12.1, 0.01, 2.3) + f'<rect width="2.0" height=".3" rx=".06" fill="{pal["accent_soft"]}"/>'
               f'<text x="1" y=".21" font-size=".18" text-anchor="middle" font-family="{FONT}" '
               f'fill="{pal["accent"]}">nixos</text></g>')

    # Task board on the left wall; one card keeps travelling from todo to done.
    cards = []
    for column, (count, color) in enumerate(((3, pal["note"]), (1, pal["accent_soft"]), (2, pal["done"]))):
        u = 0.12 + column * 1.02
        cards.append(f'<text x="{num(u)}" y=".22" font-size=".14" {text}>{("todo", "doing", "done")[column]}</text>')
        cards += [f'<rect x="{num(u)}" y="{num(0.32 + k * 0.24)}" width=".82" height=".17" rx=".03" fill="{color}"/>'
                  for k in range(count)]
    out.append(plane("yz", 0.01, 4.4, 1.95)
               + f'<rect width="3.2" height="1.2" rx=".05" fill="{pal["board"]}" stroke="{pal["frame"]}" {thin}/>'
               + "".join(cards)
               + f'<rect class="card" x=".12" y=".8" width=".82" height=".17" rx=".03" fill="{pal["note"]}" '
               f'stroke="{pal["accent"]}" {thin}/></g>')
    style.append(".card{animation:card 12s ease-in-out infinite}"
                 "@keyframes card{0%,20%{transform:translate(0,0)}30%,60%{transform:translate(1.02px,-.24px)}"
                 "70%,92%{transform:translate(2.04px,-.24px)}96%{transform:translate(2.04px,-.24px);opacity:1}"
                 "98%{opacity:0;transform:translate(2.04px,-.24px)}99%{opacity:0;transform:translate(0,0)}100%{opacity:1}}")

    # Tentacles: ribbons on the floor from the hub to every station, with pulses going out.
    targets = [(x + 1.5, DESK_Y + DESK_D + 0.05) for x in DESKS] + [(0.08, 3.0), (4.6, 0.08), (12.6, 1.0)]
    for index, (tx, ty) in enumerate(targets):
        hx, hy = HUB
        length = math.dist((hx, hy), (tx, ty))
        nx, ny = (hy - ty) / length, (tx - hx) / length
        bend = (0.16 if index % 2 else -0.16) * length
        c1 = (hx + (tx - hx) * 0.3 + nx * bend, hy + (ty - hy) * 0.3 + ny * bend)
        c2 = (hx + (tx - hx) * 0.7 - nx * bend * 0.6, hy + (ty - hy) * 0.7 - ny * bend * 0.6)
        d = f"M{num(hx)} {num(hy)}C{num(c1[0])} {num(c1[1])} {num(c2[0])} {num(c2[1])} {num(tx)} {num(ty)}"
        body = pal["tentacle"]
        out.append(floor_plane + f'<path d="{d}" fill="none" stroke="{body["right"]}" stroke-width=".22" '
                   f'stroke-linecap="round"/></g>')
        out.append(f'<g transform="translate(0 -1)">{floor_plane}<path d="{d}" fill="none" stroke="{body["top"]}" '
                   f'stroke-width=".15" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{pal["highlight"]}" '
                   f'stroke-width=".04" stroke-linecap="round"/><path class="pulse" style="animation-delay:-{index * 0.29:.2f}s" '
                   f'd="{d}" pathLength="12" fill="none" stroke="{pal["core"]}" stroke-width=".1" stroke-linecap="round" '
                   f'stroke-dasharray=".01 2.99"/></g></g>')
    style.append(".pulse{animation:pulse 1.9s linear infinite}@keyframes pulse{from{stroke-dashoffset:0}to{stroke-dashoffset:-3}}")

    # Back corner plant and the server racks with blinking LEDs.
    out.append(plant(0.25, 0.3, pal))
    for i, x in enumerate(RACKS):
        out.append(box(x, 0.12, 0, 1.0, 0.85, 1.75, pal["rack"]))
        leds = []
        for k in range(6):
            w = 0.12 + k * 0.27
            leds.append(f'<rect x=".08" y="{num(w)}" width=".84" height=".2" rx=".02" fill="{pal["slot"]}"/>')
            for j in range(3):
                delay = ((i * 7 + k * 3 + j * 5) % 11) * 0.23
                leds.append(f'<rect class="led" style="animation-delay:-{delay:.2f}s" x="{num(0.16 + j * 0.1)}" '
                            f'y="{num(w + 0.075)}" width=".05" height=".05" fill="{pal["accent"]}"/>')
            leds.append(f'<rect x=".8" y="{num(w + 0.075)}" width=".05" height=".05" fill="{pal["done"]}"/>')
        out.append(plane("xz", x, 0.97, 1.75) + "".join(leds) + "</g>")
    style.append(".led{animation:led 1.3s steps(1,end) infinite}@keyframes led{0%{opacity:1}40%{opacity:.25}70%{opacity:1}85%{opacity:.4}}")

    # Desks with a monitor, stand and keyboard; screens keep typing code.
    for i, x in enumerate(DESKS):
        sx = x + DESK_W / 2
        out.append(box(x, DESK_Y, 0, 0.08, DESK_D, 0.56, pal["leg"]))
        out.append(box(x + DESK_W - 0.08, DESK_Y, 0, 0.08, DESK_D, 0.56, pal["leg"]))
        out.append(box(x, DESK_Y, 0.56, DESK_W, DESK_D, 0.06, pal["desk"]))
        out.append(box(sx - 0.06, DESK_Y + 0.15, 0.62, 0.12, 0.08, 0.16, pal["metal"]))
        out.append(box(sx - 0.5, DESK_Y + 0.1, 0.78, 1.0, 0.07, 0.56, pal["rack"]))
        out.append(box(sx - 0.3, DESK_Y + 0.55, 0.62, 0.6, 0.16, 0.025, pal["metal"]))
        lines = []
        for k, (indent, width) in enumerate(((0, 0.5), (0.1, 0.62), (0.1, 0.38), (0.2, 0.55), (0.1, 0.3))):
            delay = 4.0 - k * 0.55 - i * 0.9
            lines.append(f'<rect class="type" style="animation-delay:-{delay:.2f}s" x="{num(0.1 + indent)}" '
                         f'y="{num(0.1 + k * 0.08)}" width="{num(width)}" height=".04" '
                         f'fill="{css(CODE[(k + i) % len(CODE)])}"/>')
        out.append(plane("xz", sx - 0.5, DESK_Y + 0.17, 1.34)
                   + f'<rect x=".05" y=".05" width=".9" height=".46" fill="{pal["screen"]}"/>' + "".join(lines) + "</g>")
    style.append(".type{transform-box:fill-box;transform-origin:0 50%;animation:type 4s steps(6,end) infinite}"
                 "@keyframes type{0%{transform:scaleX(0)}40%,100%{transform:scaleX(1)}}")

    # The agents.
    agents, bubbles = [], []
    for n, agent in enumerate(AGENTS):
        segments, total = timeline(agent)
        timing = f"{total:.2f}s"
        delay = f"{agent['delay']}s"
        style.append(f".m{n}{{animation:m{n} {timing} linear {delay} infinite}}")
        style.append(move_track(f"m{n}", segments, total))
        style.append(f".f{n}{{animation:f{n} {timing} steps(1,end) {delay} infinite}}")
        style.append(step_track(f"f{n}", segments, total, lambda s: f"transform:scale({s[5]},1)"))
        for pose, short in POSES.items():
            name = f"{short}{n}"
            style.append(f".{name}{{animation:{name} {timing} steps(1,end) {delay} infinite}}")
            style.append(step_track(name, segments, total, lambda s, p=pose: f"opacity:{1 if s[4] == p else 0}"))
        for icon in ICONS:
            name = f"i{icon}{n}"
            style.append(f".{name}{{animation:{name} {timing} steps(1,end) {delay} infinite}}")
            style.append(step_track(name, segments, total,
                                    lambda s, i=icon: f"opacity:{1 if ACTIVITY_ICON.get(s[6]) == i else 0}"))
        name = f"b{n}"
        style.append(f".{name}{{animation:{name} {timing} steps(1,end) {delay} infinite}}")
        style.append(step_track(name, segments, total, lambda s: f"opacity:{1 if s[6] else 0}"))

        rt = agent["runtime"]
        x, y = P(*seat(agent))
        start = f'transform="translate({num(x)} {num(y)})"'
        agents.append(
            f'<g class="m{n}" {start}><ellipse rx="11" ry="5" fill="{pal["shadow"]}"/><g class="f{n}">'
            f'<g class="pf{n}" opacity="0">{figure(rt, "front", "walk", pal)}</g>'
            f'<g class="pb{n}" opacity="0">{figure(rt, "back", "walk", pal)}</g>'
            f'<g class="pw{n}">{figure(rt, "back", "work", pal)}</g></g>'
            f'<text y="15" font-size="8.5" text-anchor="middle" font-family="{FONT}" fill="{pal["hue"][rt]}" '
            f'stroke="{pal["paper"]}" stroke-width="3" paint-order="stroke" stroke-linejoin="round">{rt}</text></g>'
        )
        icons = "".join(f'<g class="i{icon}{n}" opacity="{1 if icon == "code" else 0}">{shape}</g>'
                        for icon, shape in ICONS.items())
        bubbles.append(
            f'<g class="m{n}" {start}><g class="b{n}" transform="translate(0 -76)">'
            f'<path d="M-13 -10h26a4 4 0 0 1 4 4v11a4 4 0 0 1-4 4h-10l-3 4-3-4h-10a4 4 0 0 1-4-4v-11a4 4 0 0 1 4-4z" '
            f'fill="{pal["surface"]}" stroke="{pal["line"]}" stroke-width=".8"/>'
            f'<g transform="translate(0 -.5)" fill="none" stroke="{pal["accent"]}" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round">{icons}</g></g></g>'
        )
    out += agents
    style.append(".bob{animation:bob .16s ease-in-out infinite alternate}@keyframes bob{to{transform:translateY(-1.2px)}}"
                 ".nod{animation:nod 2.4s ease-in-out infinite alternate}@keyframes nod{to{transform:translateY(.8px)}}"
                 ".ls,.lt,.as,.at,.ty,.ty2{transform-box:fill-box;transform-origin:50% 0}"
                 ".lt,.at{animation:swing .3s ease-in-out infinite alternate}"
                 ".ls,.as{animation:swing .3s ease-in-out -.3s infinite alternate}"
                 "@keyframes swing{from{transform:rotate(-20deg)}to{transform:rotate(20deg)}}"
                 ".ty{animation:typing .2s ease-in-out infinite alternate}.ty2{animation:typing .2s ease-in-out -.13s infinite alternate}"
                 "@keyframes typing{to{transform:translateY(-1.6px)}}")

    # In front of everyone: a lounge corner, the Tentaflake hub and a plant.
    out.append(box(0.1, 7.0, 0, 0.75, 2.2, 0.32, pal["sofa"]))
    out.append(box(0.1, 7.0, 0.32, 0.22, 2.2, 0.42, pal["sofa"]))
    out.append(box(1.35, 7.6, 0, 0.8, 1.1, 0.3, pal["table"]))
    hx, hy = HUB
    gx, gy = P(hx, hy, 0.36)
    out.append(f'<ellipse class="glow" cx="{num(gx)}" cy="{num(gy)}" rx="78" ry="39" fill="url(#glow)"/>')
    out.append(box(hx - 1.0, hy - 1.0, 0, 2.0, 2.0, 0.22, pal["metal"]))
    out.append(box(hx - 0.75, hy - 0.75, 0.22, 1.5, 1.5, 0.14, pal["rack"]))
    size = 88
    out.append(f'<g class="float"><image href="data:image/webp;base64,{mark}" x="{num(gx - size / 2)}" '
               f'y="{num(gy - size * 0.86)}" width="{size}" height="{size}"/></g>')
    style.append(".glow{transform-box:fill-box;transform-origin:center;animation:glow 3.2s ease-in-out infinite alternate}"
                 "@keyframes glow{from{opacity:.55;transform:scale(.85)}to{opacity:1;transform:scale(1.05)}}"
                 ".float{animation:float 3.2s ease-in-out infinite alternate}@keyframes float{to{transform:translateY(-4px)}}")
    out.append(plant(0.35, 10.2, pal))
    out.append(plant(15.2, 10.2, pal))
    out += bubbles
    return out, style


def plant(x, y, pal):
    cx, cy = P(x + 0.25, y + 0.25, 0.42)
    leaves = "".join(
        f'<ellipse cx="{num(cx + dx)}" cy="{num(cy + dy)}" rx="{r}" ry="{num(r * 0.8)}" fill="{pal["leaf"][face]}"/>'
        for dx, dy, r, face in ((-5, -6, 8, "right"), (5, -9, 8, "left"), (0, -16, 8, "top"), (-3, -22, 6, "left"), (3, -26, 5, "top"))
    )
    return box(x, y, 0, 0.5, 0.5, 0.42, pal["pot"]) + leaves


def render(theme, mark):
    pal = palette(theme)
    body, style = office(pal, mark)
    margin = 12
    left = P(-THICK, ROWS)[0] - margin
    right = P(COLS, -THICK)[0] + margin
    top = P(-THICK, -THICK, WALL)[1] - margin - 16
    bottom = P(COLS, ROWS, -SLAB)[1] + margin
    width, height = right - left, bottom - top
    label = f'font-family="{FONT}" font-size="11" letter-spacing="1.5"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(left)} {num(top)} {num(width)} {num(height)}" '
        f'width="{round(width)}" height="{round(height)}" role="img" aria-labelledby="title">'
        f'<title id="title">Three AI agents at work in a Tentaflake environment: they take tasks from a board, '
        f'code at their desks, deploy at the server rack and check the dashboard. An illustration, not a live view.</title>'
        f'<defs><radialGradient id="glow"><stop offset="0" stop-color="{pal["core"]}"/>'
        f'<stop offset="1" stop-color="{pal["core"]}" stop-opacity="0"/></radialGradient></defs>'
        f'<style>{"".join(style)}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>'
        + "".join(body)
        + f'<text x="{num(left + margin + 4)}" y="{num(top + margin + 22)}" {label} fill="{pal["accent"]}">TENTAFLAKE</text>'
        f'<text x="{num(left + margin + 4)}" y="{num(top + margin + 40)}" {label} fill="{pal["muted"]}">agents at work, 24/7</text>'
        f'<text x="{num(right - margin - 4)}" y="{num(bottom - margin - 2)}" font-family="{FONT}" font-size="10" '
        f'text-anchor="end" fill="{pal["muted"]}">illustration, not a live view</text>'
        "</svg>\n"
    )


def main():
    mark = base64.b64encode((ASSETS / "tentaflake-mark.webp").read_bytes()).decode()
    for name, theme in THEMES.items():
        (ASSETS / f"agent-office-{name}.svg").write_text(render(theme, mark))


if __name__ == "__main__":
    main()
