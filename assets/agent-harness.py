#!/usr/bin/env python3
"""Render the README's benchmark arena as animated SVGs: wide and narrow, light and dark.

An isometric arena for one agent-harness benchmark task, "repair routing and firewall".
Several agents compete on the same task, each sealed in its own isolated Linux network
with a client, a router, a firewall and two services; they cannot reach each other.
An independent evaluator then probes every network: web must be reachable and admin
must stay blocked. Lamps on each network's roof show whether the two checks hold.

Everything is synthetic: no run, score, ranking or live data. Plain SVG with CSS
animation, so GitHub shows it without scripts. The base styles are the finished frame;
animations only dim, move and reveal, so viewers without animation support or with
reduced motion requested see a complete static scene.

    python3 assets/agent-harness.py
"""

from pathlib import Path

ASSETS = Path(__file__).resolve().parent
HW, HH, ZU = 32, 16, 32  # isometric half tile width, half tile height, unit height
LOOP = 16  # seconds
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
POD, POD_H = 3.0, 1.7  # glass network footprint (tiles) and height (units)
K = POD / 2.6  # scale of the network contents, laid out for a 2.6-tile box
AGENT_AT = (1.4, POD + 1.25)  # where each agent stands, relative to its network

THEMES = {
    "light": dict(
        bg="#f7f8fa",
        ink="#1c222b",
        muted="#56606d",
        accent="#2943d6",
        ok="#1d7f46",
        bad="#c0392b",
        panel="#ffffff",
        line="#aeb6c4",
        floor_top="#e4e7ed",
        floor_alt="#d8dce4",
        slab_l="#c9ced8",
        slab_r="#b9bfcb",
        stand_top="#d3d8e1",
        stand_l="#bfc6d2",
        stand_r="#aeb6c4",
        glass="rgba(41,67,214,.07)",
        glass_edge="rgba(41,67,214,.75)",
        node_top="#f4f5f8",
        node_l="#d6dae2",
        node_r="#c4cad5",
        brick_top="#e2c7a8",
        brick_l="#c99f77",
        brick_r="#b58a63",
        track="#cfd4dd",
        visor="#1c222b",
        screen="#1c222b",
        post="#9aa3b0",
    ),
    "dark": dict(
        bg="#15191f",
        ink="#edf0f5",
        muted="#b1bac8",
        accent="#a3b4ff",
        ok="#5cc98a",
        bad="#ff8a73",
        panel="#1d232c",
        line="#4a5462",
        floor_top="#252c36",
        floor_alt="#2c3440",
        slab_l="#1b2028",
        slab_r="#161a21",
        stand_top="#2d3540",
        stand_l="#232a33",
        stand_r="#1c222a",
        glass="rgba(163,180,255,.08)",
        glass_edge="rgba(163,180,255,.8)",
        node_top="#3a4350",
        node_l="#2c333d",
        node_r="#242a33",
        brick_top="#7a6150",
        brick_l="#5e4a3d",
        brick_r="#4d3d32",
        track="#323a46",
        visor="#0d1015",
        screen="#0d1015",
        post="#56606d",
    ),
}
AGENTS = (  # body, eyes
    ("#2f9e8f", "#b9f5ea"),
    ("#7b5cd6", "#e2d8ff"),
    ("#e07a4f", "#ffe1cf"),
    ("#3b82c4", "#d6ebff"),
    ("#c2508a", "#ffd9ec"),
    ("#8a9a2e", "#f0f7c8"),
)
EVALUATOR = ("#d9a23b", "#fff1cc")
CROWD = (
    "#2f9e8f",
    "#7b5cd6",
    "#e07a4f",
    "#3b82c4",
    "#c2508a",
    "#8a9a2e",
    "#d9a23b",
    "#8b95a5",
)
# Invented outcome per network for the picture: (web reachable, admin blocked).
OUTCOMES = (
    (True, True),
    (True, True),
    (False, True),
    (True, True),
    (True, False),
    (True, True),
)
# Loop percentage at which each agent submits its configuration.
FINISH = (38, 47, 52, 42, 56, 49)
PROBE_START, PROBE_STEP = 62, 4.5

LAYOUTS = {
    "wide": dict(cols=16, rows=11.6, evaluator=(15.3, 10.0), margin=(24, 24, 24, 24), labels="corners",
                 pods=((1.0, 1.0), (6.0, 1.0), (11.0, 1.0), (1.0, 6.4), (6.0, 6.4), (11.0, 6.4))),
    "narrow": dict(cols=11, rows=11.6, evaluator=(10.4, 9.6), margin=(24, 24, 24, 28), labels="stacked",
                   pods=((1.0, 1.0), (6.0, 1.0), (1.0, 6.4), (6.0, 6.4))),
}


def P(x, y, z=0.0):
    return (x - y) * HW, (x + y) * HH - z * ZU


def num(v):
    text = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def poly(points, fill):
    d = " ".join(f"{num(x)} {num(y)}" for x, y in points)
    return f'<path d="M{d}Z" fill="{fill}"/>'


def line(a, b):
    return f"M{num(a[0])} {num(a[1])}L{num(b[0])} {num(b[1])}"


def box(x, y, z, w, d, h, top, left, right):
    """Visible faces of an axis-aligned box: front-left (y+d), front-right (x+w), top."""
    return "".join(
        (
            poly(
                [
                    P(x, y + d, z),
                    P(x + w, y + d, z),
                    P(x + w, y + d, z + h),
                    P(x, y + d, z + h),
                ],
                left,
            ),
            poly(
                [
                    P(x + w, y, z),
                    P(x + w, y + d, z),
                    P(x + w, y + d, z + h),
                    P(x + w, y, z + h),
                ],
                right,
            ),
            poly(
                [
                    P(x, y, z + h),
                    P(x + w, y, z + h),
                    P(x + w, y + d, z + h),
                    P(x, y + d, z + h),
                ],
                top,
            ),
        )
    )


def text(x, y, body, size=16, fill="ink", weight=None, anchor=None):
    attrs = [f'x="{num(x)}" y="{num(y)}" font-size="{size}" fill="{{{fill}}}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    return f"<text {' '.join(attrs)}>{body}</text>"


def frange(start, stop, step):
    v = start
    while v <= stop:
        yield v
        v += step


def move_track(name, points, start, end):
    """Keyframes that move an element along screen points between two loop percentages."""
    x0, y0 = points[0]
    lengths = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(points, points[1:])]
    total, run = sum(lengths), 0
    frames = [
        f"0%,{start}%{{opacity:0;transform:translate(0,0)}}",
        f"{start + 0.5}%{{opacity:1;transform:translate(0,0)}}",
    ]
    for (x, y), length in zip(points[1:], lengths):
        run += length
        pct = start + (end - start) * run / total
        frames.append(
            f"{pct:.1f}%{{opacity:1;transform:translate({num(x - x0)}px,{num(y - y0)}px)}}"
        )
    lx, ly = points[-1]
    frames.append(
        f"{end + 3}%,100%{{opacity:0;transform:translate({num(lx - x0)}px,{num(ly - y0)}px)}}"
    )
    return f"@keyframes {name}{{{''.join(frames)}}}"


# --- arena -----------------------------------------------------------------------


def stands(cols, rows):
    """Three tiers of seats along both back edges, outermost first, with a crowd."""
    stand = ("{stand_top}", "{stand_l}", "{stand_r}")
    a, n = [], 0
    for tier in (1, 0):
        o, h = 0.7 * (tier + 1), 0.32 * (tier + 1)
        a.append(box(-o, -o, 0, cols + o, 0.7, h, *stand))
        a.append(box(-o, -o + 0.7, 0, 0.7, rows + o - 0.7, h, *stand))
        mid = -o + 0.35
        spots = [(x, mid) for x in frange(0.4, cols - 0.3, 0.95)]
        spots += [(mid, y) for y in frange(0.4, rows - 0.3, 0.95)]
        for x, y in spots:
            sx, sy = P(x, y, h)
            colour = CROWD[(n * 5 + tier) % len(CROWD)]
            a.append(
                f'<g class="cheer" style="animation-delay:{-(n * 0.37) % 2.2:.2f}s">'
                f'<rect x="{num(sx - 5)}" y="{num(sy - 12)}" width="10" height="11" rx="4" fill="{colour}" opacity=".7"/>'
                f'<circle cx="{num(sx)}" cy="{num(sy - 16)}" r="4.5" fill="{colour}"/></g>'
            )
            n += 1
    return "".join(a)


def floor(cols, rows):
    a = [box(0, 0, -0.3, cols, rows, 0.3, "{floor_top}", "{slab_l}", "{slab_r}")]
    marks = [line(P(i, 0), P(i, rows)) for i in range(2, int(cols), 2)]
    marks += [line(P(0, j), P(cols, j)) for j in range(2, int(rows), 2)]
    a.append(f'<path d="{"".join(marks)}" stroke="{{floor_alt}}" stroke-width="2"/>')
    return "".join(a)


def jumbotron(big):
    """The task on a screen above the back corner of the arena."""
    s = 1.12 if big else 1
    cx, back = 0, P(-1.4, -1.4, 0.64)[1]
    w, h = 330 * s, 100 * s
    x, y = cx - w / 2, back - h - 30
    a = [
        f'<rect x="{num(cx - 72)}" y="{num(y + h)}" width="6" height="44" fill="{{post}}"/>',
        f'<rect x="{num(cx + 66)}" y="{num(y + h)}" width="6" height="44" fill="{{post}}"/>',
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="10" fill="{{screen}}" '
        f'stroke="{{accent}}" stroke-width="2" class="loop task"/>',
        f'<text x="{cx}" y="{num(y + 26 * s)}" font-size="{num(14 * s)}" fill="#b1bac8" text-anchor="middle">① TASK · same for every agent</text>',
        f'<text x="{cx}" y="{num(y + 56 * s)}" font-size="{num(21 * s)}" fill="#edf0f5" font-weight="700" text-anchor="middle">repair routing</text>',
        f'<text x="{cx}" y="{num(y + 81 * s)}" font-size="{num(21 * s)}" fill="#edf0f5" font-weight="700" text-anchor="middle">and firewall</text>',
    ]
    return "".join(a), y


def lamp(x, y, held, r=8.0):
    colour = "{ok}" if held else "{bad}"
    k = r / 8
    mark = (
        f"M{num(x - 3.5 * k)} {num(y)} l{num(2.5 * k)} {num(2.5 * k)} l{num(4.5 * k)} {num(-5 * k)}"
        if held
        else f"M{num(x - 3 * k)} {num(y - 3 * k)} l{num(6 * k)} {num(6 * k)} "
        f"M{num(x + 3 * k)} {num(y - 3 * k)} l{num(-6 * k)} {num(6 * k)}"
    )
    return (
        f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{colour}"/>'
        f'<path d="{mark}" stroke="{{panel}}" stroke-width="{num(2 * k)}" fill="none" stroke-linecap="round"/>'
    )


def pod(i, px, py):
    """One sealed network: glass box with client, router, firewall, web and admin."""

    def g(u, v, z=0.0):
        return P(px + u, py + v, z)

    def gi(u, v, z=0.0):
        return P(px + u * K, py + v * K, z)

    def bi(u, v, z, w, d, h, faces):
        return box(px + u * K, py + v * K, z, w * K, d * K, h, *faces)

    node = ("{node_top}", "{node_l}", "{node_r}")
    brick = ("{brick_top}", "{brick_l}", "{brick_r}")
    a = [
        poly([g(0, 0), g(0, POD), g(0, POD, POD_H), g(0, 0, POD_H)], "{glass}"),
        poly([g(0, 0), g(POD, 0), g(POD, 0, POD_H), g(0, 0, POD_H)], "{glass}"),
        bi(1.0, 0.25, 0, 0.6, 0.4, 0.35, node),  # client
        bi(1.05, 0.95, 0, 0.5, 0.45, 0.28, node),  # router
    ]
    rx, ry = gi(1.3, 1.17, 0.28)
    a.append(f'<circle cx="{num(rx)}" cy="{num(ry)}" r="4" fill="{{accent}}"/>')
    # Firewall; the middle brick closes the web opening until the agent's fix lands.
    a.append(bi(0.15, 1.55, 0, 0.4, 0.15, 0.45, brick))
    a.append(
        f'<g class="loop shut s{i}">{bi(0.55, 1.55, 0, 0.4, 0.15, 0.45, brick)}</g>'
    )
    a.append(bi(0.95, 1.55, 0, 1.5, 0.15, 0.45, brick))
    for u in (0.3, 1.5):  # web, admin
        a.append(bi(u, 1.95, 0, 0.8, 0.5, 0.75, node))
        for k in range(3):
            lx, ly = gi(u + 0.8, 2.1 + k * 0.12, 0.6 - k * 0.18)
            a.append(f'<circle cx="{num(lx)}" cy="{num(ly)}" r="1.6" fill="{{ok}}"/>')
    start = gi(1.3, 1.17, 0.4)
    ok_path = (start, gi(0.75, 1.62, 0.4), gi(0.7, 2.2, 0.85))
    bad_path = (start, gi(1.9, 1.5, 0.4))
    for name, colour in ((f"pok{i}", "ok"), (f"pbad{i}", "bad")):
        a.append(
            f'<circle cx="{num(start[0])}" cy="{num(start[1])}" r="4.5" fill="{{{colour}}}" class="loop {name}"/>'
        )
    # Front glass faces and dashed edges.
    a.append(
        poly([g(POD, 0), g(POD, POD), g(POD, POD, POD_H), g(POD, 0, POD_H)], "{glass}")
    )
    a.append(
        poly([g(0, POD), g(POD, POD), g(POD, POD, POD_H), g(0, POD, POD_H)], "{glass}")
    )
    a.append(
        poly(
            [g(0, 0, POD_H), g(POD, 0, POD_H), g(POD, POD, POD_H), g(0, POD, POD_H)],
            "{glass}",
        )
    )
    corners = [(0, 0), (POD, 0), (POD, POD), (0, POD)]
    edges = [(g(u, v), g(u, v, POD_H)) for u, v in corners]
    edges += [
        (g(*corners[k], POD_H), g(*corners[(k + 1) % 4], POD_H)) for k in range(4)
    ]
    edges += [(g(POD, 0), g(POD, POD)), (g(0, POD), g(POD, POD))]
    d = "".join(line(s, e) for s, e in edges)
    a.append(
        f'<path d="{d}" stroke="{{glass_edge}}" stroke-width="1.4" stroke-dasharray="5 4" fill="none"/>'
    )
    # Check lamps on the roof, lit once the evaluator has probed this network.
    for k, held in enumerate(OUTCOMES[i]):
        lx, ly = gi(0.85 + k * 0.9, 1.3, POD_H)
        a.append(f'<g class="loop lamp l{i}">{lamp(lx, ly, held)}</g>')
    return "".join(a), (ok_path, bad_path)


def agent(i, x, y):
    body, eyes = AGENTS[i]
    sx, sy = P(x, y)
    delay = -0.7 * i
    a = [
        f'<ellipse cx="{num(sx)}" cy="{num(sy)}" rx="15" ry="6" fill="#000" opacity=".12"/>',
        f'<g class="bob" style="animation-delay:{delay:.1f}s">',
        f'<rect x="{num(sx - 9)}" y="{num(sy - 12)}" width="6" height="12" rx="3" fill="{body}"/>',
        f'<rect x="{num(sx + 3)}" y="{num(sy - 12)}" width="6" height="12" rx="3" fill="{body}"/>',
        f'<rect x="{num(sx - 14)}" y="{num(sy - 38)}" width="28" height="28" rx="9" fill="{body}" opacity=".9"/>',
        f'<line x1="{num(sx)}" y1="{num(sy - 62)}" x2="{num(sx)}" y2="{num(sy - 70)}" stroke="{body}" stroke-width="2.5"/>',
        f'<circle cx="{num(sx)}" cy="{num(sy - 72)}" r="3.5" fill="{body}"/>',
        f'<rect x="{num(sx - 17)}" y="{num(sy - 62)}" width="34" height="26" rx="9" fill="{body}"/>',
        f'<rect x="{num(sx - 12)}" y="{num(sy - 56)}" width="24" height="13" rx="5" fill="{{visor}}"/>',
        f'<g class="blink" style="animation-delay:{delay * 1.6:.1f}s">'
        f'<circle cx="{num(sx - 5)}" cy="{num(sy - 49.5)}" r="2.4" fill="{eyes}"/>'
        f'<circle cx="{num(sx + 5)}" cy="{num(sy - 49.5)}" r="2.4" fill="{eyes}"/></g>',
        f'<line x1="{num(sx - 12)}" y1="{num(sy - 28)}" x2="{num(sx - 24)}" y2="{num(sy - 36)}" '
        f'stroke="{body}" stroke-width="5" stroke-linecap="round"/>',
        "</g>",
        f'<g class="float" style="animation-delay:{delay:.1f}s">',
        f'<rect x="{num(sx - 64)}" y="{num(sy - 70)}" width="44" height="34" rx="4" fill="{{screen}}" '
        f'stroke="{body}" stroke-width="1.5"/>',
    ]
    # Progress toward a submitted fix, filling at a different pace for every agent.
    a.append(f'<rect x="{num(sx - 59)}" y="{num(sy - 44)}" width="34" height="4" rx="2" fill="{{track}}"/>')
    a.append(f'<rect x="{num(sx - 59)}" y="{num(sy - 44)}" width="34" height="4" rx="2" fill="{eyes}" '
             f'class="loop bar b{i}"/>')
    for k, width in enumerate((26, 16, 30)):
        a.append(
            f'<rect x="{num(sx - 59)}" y="{num(sy - 65 + k * 6)}" width="{width}" height="3" rx="1.5" '
            f'fill="{eyes}" class="type" style="animation-delay:{-(k * 0.3 + i * 0.2):.1f}s"/>'
        )
    a.append("</g>")
    return "".join(a)


def evaluator(x, y):
    body, eyes = EVALUATOR
    sx, sy = P(x, y, 0.35)
    a = [
        box(
            x - 0.55,
            y - 0.55,
            0,
            1.1,
            1.1,
            0.35,
            "{stand_top}",
            "{stand_l}",
            "{stand_r}",
        ),
        '<g class="bob" style="animation-delay:-1.1s">',
        f'<rect x="{num(sx - 16)}" y="{num(sy - 44)}" width="32" height="36" rx="10" fill="{body}" opacity=".9"/>',
        f'<rect x="{num(sx - 19)}" y="{num(sy - 74)}" width="38" height="30" rx="9" fill="{body}"/>',
        f'<rect x="{num(sx - 14)}" y="{num(sy - 67)}" width="28" height="15" rx="5" fill="{{visor}}"/>',
        f'<circle cx="{num(sx - 5)}" cy="{num(sy - 59.5)}" r="3.6" fill="none" stroke="{eyes}" stroke-width="2"/>',
        f'<circle cx="{num(sx + 6)}" cy="{num(sy - 59.5)}" r="2.4" fill="{eyes}"/>',
        f'<line x1="{num(sx - 14)}" y1="{num(sy - 30)}" x2="{num(sx - 30)}" y2="{num(sy - 44)}" '
        f'stroke="{body}" stroke-width="5" stroke-linecap="round"/>',
        f'<circle cx="{num(sx - 36)}" cy="{num(sy - 50)}" r="10" fill="{{panel}}" fill-opacity=".5" '
        f'stroke="{{ink}}" stroke-width="2.5"/>',
        "</g>",
    ]
    return "".join(a), (sx - 36, sy - 50)


# --- composition -----------------------------------------------------------------


def scene(layout):
    cols, rows, pods = layout["cols"], layout["rows"], layout["pods"]
    parts = [stands(cols, rows), floor(cols, rows)]
    screen, top = jumbotron(layout["labels"] == "stacked")

    items, packets = [], {}
    for i, (px, py) in enumerate(pods):
        svg, packets[i] = pod(i, px, py)
        items.append((px + py + POD, svg))
        ax, ay = px + AGENT_AT[0], py + AGENT_AT[1]
        items.append((ax + ay, agent(i, ax, ay)))
    ev_svg, lens = evaluator(*layout["evaluator"])
    items.append((sum(layout["evaluator"]), ev_svg))
    parts.extend(svg for _, svg in sorted(items, key=lambda item: item[0]))

    # Evaluator probes: one beam per network, in turn.
    for i, (px, py) in enumerate(pods):
        target = P(px + POD / 2, py + POD / 2, POD_H)
        parts.append(
            f'<path d="{line(lens, target)}" stroke="{{accent}}" stroke-width="2.5" '
            f'stroke-dasharray="6 5" class="loop beam e{i}"/>'
        )
    parts.append(screen)

    bounds = (P(-1.4, rows)[0], top, P(cols, -1.4)[0], P(cols, rows)[1] + 0.3 * ZU)
    labels, (minx, top, maxx, bottom) = place_labels(layout, bounds)
    parts.extend(labels)
    ml, mt, mr, mb = layout["margin"]
    view = (minx - ml, top - mt, maxx - minx + ml + mr, bottom - top + mt + mb)
    return "".join(parts), view, packets


def legend(x, y, size, gap):
    rows = ((True, "web reachable"), (True, "admin blocked"), (False, "check fails"))
    return [
        lamp(x + size / 2, y + gap * (k + 1) - size * 0.35, held, size / 2)
        + text(x + size * 1.5, y + gap * (k + 1), label, size=size)
        for k, (held, label) in enumerate(rows)
    ]


def place_labels(layout, bounds):
    minx, top, maxx, bottom = bounds
    a = []
    if layout["labels"] == "corners":
        px, py = layout["pods"][2]
        tx, ty = P(px + POD, py + 0.6, POD_H * 0.6)
        lx, ly = maxx - 236, top + 34
        a.append(
            f'<path d="{line((lx + 110, ly + 52), (tx, ty))}" stroke="{{line}}" stroke-width="1.5"/>'
        )
        a.append(f'<circle cx="{num(tx)}" cy="{num(ty)}" r="3" fill="{{line}}"/>')
        a.append(text(lx, ly, "② one agent per", fill="muted"))
        a.append(text(lx, ly + 22, "isolated Linux network,", fill="muted"))
        a.append(text(lx, ly + 44, "same task, separate runs", fill="muted"))
        ex, ey = P(*layout["evaluator"])
        a.append(text(ex + 46, ey - 52, "③ independent", fill="muted"))
        a.append(text(ex + 46, ey - 30, "evaluator probes", fill="muted"))
        a.append(text(ex + 46, ey - 8, "every network", fill="muted"))
        maxx = max(maxx, ex + 46 + 17 * 9.7)
        bx, by = minx, bottom - 128
        a.append(text(bx, by, "④ lamps on each roof", fill="muted"))
        a.extend(legend(bx, by, 16, 26))
        bottom += 30
        a.append(
            text(
                maxx,
                bottom,
                "illustration · synthetic runs and outcomes · no scores",
                size=14,
                fill="muted",
                anchor="end",
            )
        )
    else:
        size, y = 26, bottom + 60
        lines = (
            "② one agent per isolated",
            "   Linux network, same task",
            None,
            "③ an independent evaluator",
            "   probes every network",
            None,
            "④ lamps on each roof",
        )
        for body in lines:
            if body:
                a.append(text(minx, y, body, size=size, fill="muted"))
            y += 36 if body else 14
        a.extend(legend(minx, y - 36, size, 40))
        y += 3 * 40 + 24
        a.append(text(minx, y, "illustration · synthetic runs", size=22, fill="muted"))
        a.append(text(minx, y + 30, "and outcomes · no scores", size=22, fill="muted"))
        bottom = y + 30
    return a, (minx, top, maxx, bottom)


def style(layout, packets):
    rules = [
        f"text{{font-family:{FONT}}}",
        f".loop{{animation-duration:{LOOP}s;animation-iteration-count:infinite;animation-timing-function:ease-in-out}}",
        ".task{animation-name:task}",
        "@keyframes task{0%,10%{stroke-width:5}16%,100%{stroke-width:2}}",
        ".bob{animation:bob 2.4s ease-in-out infinite alternate}",
        "@keyframes bob{from{transform:translateY(0)}to{transform:translateY(2px)}}",
        ".float{animation:float 3.2s ease-in-out infinite alternate}",
        "@keyframes float{from{transform:translateY(0)}to{transform:translateY(-3px)}}",
        ".cheer{animation:cheer 2.2s ease-in-out infinite}",
        "@keyframes cheer{0%,70%,100%{transform:translateY(0)}80%{transform:translateY(-4px)}}",
        ".blink{transform-box:fill-box;transform-origin:center;animation:blink 4.6s infinite}",
        "@keyframes blink{0%,94%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}",
        ".type{transform-box:fill-box;transform-origin:left;animation:type .9s steps(3) infinite}",
        "@keyframes type{0%{transform:scaleX(.3)}100%{transform:scaleX(1)}}",
        ".bar{transform-box:fill-box;transform-origin:left}.shut,.beam{opacity:0}",
    ]
    for i in range(len(layout["pods"])):
        done = FINISH[i]
        probe = PROBE_START + PROBE_STEP * i
        rules += [
            f".b{i}{{animation-name:b{i}}}",
            f"@keyframes b{i}{{0%,6%{{transform:scaleX(.05)}}{done}%,96%{{transform:scaleX(1)}}100%{{transform:scaleX(.05)}}}}",
            f".s{i}{{animation-name:s{i}}}",
            f"@keyframes s{i}{{0%,{done}%{{opacity:1}}{done + 2}%,97%{{opacity:0}}100%{{opacity:1}}}}",
            f".pok{i}{{animation-name:pok{i}}}.pbad{i}{{animation-name:pbad{i}}}",
            move_track(f"pok{i}", packets[i][0], done + 2, done + 9),
            move_track(f"pbad{i}", packets[i][1], done + 3, done + 8),
            f".e{i}{{animation-name:e{i}}}",
            f"@keyframes e{i}{{0%,{probe}%{{opacity:0}}{probe + 0.5}%,{probe + PROBE_STEP}%{{opacity:1}}"
            f"{probe + PROBE_STEP + 0.5}%,100%{{opacity:0}}}}",
            f".l{i}{{animation-name:l{i}}}",
            f"@keyframes l{i}{{0%,{probe + 2}%{{opacity:0}}{probe + 3}%,97%{{opacity:1}}100%{{opacity:0}}}}",
        ]
    rules.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return "".join(rules)


TITLE = "Agent harness benchmark arena (illustration)"
DESC = (
    "Illustration with synthetic data. An isometric arena with a crowd in the stands. "
    "A screen shows the task 'repair routing and firewall', the same for every agent. "
    "Each agent works in front of its own sealed glass box, an isolated Linux network with a client, "
    "a router, a firewall and two services, web and admin; progress bars fill at different speeds. "
    "An independent evaluator on a podium probes each network in turn, and lamps on each roof show "
    "whether web is reachable and admin is blocked. The outcomes are invented for the picture."
)


def render(theme, layout):
    pal = THEMES[theme]
    body, (x, y, w, h), packets = scene(layout)
    for key, value in pal.items():
        body = body.replace("{" + key + "}", value)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" '
        f'width="{num(w)}" height="{num(h)}" role="img" aria-labelledby="t d">'
        f'<title id="t">{TITLE}</title><desc id="d">{DESC}</desc>'
        f"<style>{style(layout, packets)}</style>"
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" fill="{pal["bg"]}"/>'
        f"{body}</svg>\n"
    )


def main():
    for name, layout in LAYOUTS.items():
        prefix = "agent-harness-" if name == "wide" else f"agent-harness-{name}-"
        for theme in THEMES:
            (ASSETS / f"{prefix}{theme}.svg").write_text(
                render(theme, layout), encoding="utf-8"
            )


if __name__ == "__main__":
    main()
