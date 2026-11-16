#!/usr/bin/env python3
"""Render the README's benchmark scene as animated SVGs: wide and narrow, light and dark.

An illustration of one agent-harness benchmark task, "repair routing and firewall":
a task board, agents working with tools, an isolated Linux network, an independent
evaluator and its result. The scene is synthetic: no run, score or live data.

The narrow layout stacks the network and evaluator below the table so the labels
stay legible on phones. Plain SVG with CSS animation, so GitHub shows it without scripts. The base styles
are the finished frame; animations only dim, move and reveal. Viewers without
animation support, or with reduced motion requested, see that static frame.

    python3 assets/agent-harness.py
"""

from pathlib import Path

ASSETS = Path(__file__).resolve().parent
# Each layout places the task-and-agents zone and the network-and-evaluator zone
# (drawn in wide coordinates) by an offset. The submitted configuration rests at a
# fraction of its path. The narrow layout omits the dotted path, which would cross
# labels, and starts the file on the table beside the third laptop.
LAYOUTS = {
    "wide": dict(size=(880, 468), table=(0, 0), network=(0, 0), floors=((352, 116),),
                 config_rest=0.3, config_line=True),
    "narrow": dict(size=(492, 880), table=(50, 0), network=(-376, 426),
                   floors=((352, 88), (778, 102)), config_from=(360, 312), config_rest=0,
                   config_line=False),
}
LOOP = 14  # seconds
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "light": dict(
        bg="#f7f8fa",
        ink="#1c222b",
        muted="#56606d",
        accent="#2943d6",
        ok="#1d7f46",
        bad="#c0392b",
        board="#ebe6dc",
        panel="#ffffff",
        line="#c3c9d3",
        lab="rgba(41,67,214,.05)",
        brick="#d9cbbb",
        brick_line="#b9a690",
        node="#e8ebf0",
        visor="#1c222b",
        wood="#c9a77c",
        floor="#eceef2",
        lid="#9aa3b0",
    ),
    "dark": dict(
        bg="#15191f",
        ink="#edf0f5",
        muted="#b1bac8",
        accent="#a3b4ff",
        ok="#5cc98a",
        bad="#ff8a73",
        board="#232a35",
        panel="#1d232c",
        line="#3d4653",
        lab="rgba(163,180,255,.07)",
        brick="#4a3f37",
        brick_line="#6b5b4e",
        node="#2a313c",
        visor="#0d1015",
        wood="#7a6247",
        floor="#1a1f26",
        lid="#56606d",
    ),
}
AGENTS = (  # x centre, body colour, eye colour, tool chip
    (80, "#2f9e8f", "#b9f5ea", "shell"),
    (190, "#7b5cd6", "#e2d8ff", "ip route"),
    (300, "#e07a4f", "#ffe1cf", "nft"),
)
EVALUATOR = ("#d9a23b", "#fff1cc")

# Network inside the isolated lab.
CLIENT, ROUTER = (516, 93), (516, 166)
WEB, ADMIN = (450, 312), (584, 312)
WALL_Y = (214, 238)
ALLOWED = (CLIENT, ROUTER, (WEB[0], 200), (WEB[0], 282))
BLOCKED = (CLIENT, ROUTER, (ADMIN[0], 200), (ADMIN[0], 212))
CONFIG_FROM, CONFIG_TO = (334, 290), (500, 176)


def text(x, y, body, size=16, fill="ink", weight=None, anchor=None, cls=None):
    attrs = [f'x="{x}" y="{y}" font-size="{size}" fill="{{{fill}}}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if cls:
        attrs.append(f'class="{cls}"')
    return f"<text {' '.join(attrs)}>{body}</text>"


def path(points):
    return "M" + " L".join(f"{x} {y}" for x, y in points)


def move_track(name, points, start, end, hold_from=None):
    """Keyframes that move an element along points between two loop percentages."""
    lengths = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(points, points[1:])]
    total, run, frames = sum(lengths), 0, []
    x0, y0 = points[0]
    frames.append(f"0%,{start}%{{opacity:0;transform:translate(0,0)}}")
    frames.append(f"{start + 0.5}%{{opacity:1;transform:translate(0,0)}}")
    for (x, y), length in zip(points[1:], lengths):
        run += length
        pct = start + (end - start) * run / total
        frames.append(
            f"{pct:.2f}%{{opacity:1;transform:translate({x - x0}px,{y - y0}px)}}"
        )
    last = points[-1]
    hold = hold_from or end + 2
    frames.append(
        f"{hold}%,100%{{opacity:0;transform:translate({last[0] - x0}px,{last[1] - y0}px)}}"
    )
    return f"@keyframes {name}{{{''.join(frames)}}}"


def config_path(layout):
    (tx, ty), (nx, ny) = layout["table"], layout["network"]
    fx, fy = layout.get("config_from", CONFIG_FROM)
    return (fx + tx, fy + ty), (CONFIG_TO[0] + nx, CONFIG_TO[1] + ny)


def style(layout):
    (fx, fy), (tx, ty) = config_path(layout)
    ax, ay = tx - fx, ty - fy
    sx, sy = -ax * layout["config_rest"], -ay * layout["config_rest"]
    ex, ey = ax + sx, ay + sy
    return "".join(
        (
            f"text{{font-family:{FONT}}}",
            f".loop{{animation-duration:{LOOP}s;animation-iteration-count:infinite;animation-timing-function:ease-in-out}}",
            # 1 task: the card lights up at the start of each loop.
            ".task{animation-name:task}",
            "@keyframes task{0%,14%{stroke-opacity:1}22%,100%{stroke-opacity:0}}",
            # 2 agents: each tool is in use for a while, otherwise dimmed.
            ".chip{animation-name:chip;opacity:1}",
            "@keyframes chip{0%,100%{opacity:.45}}",
            ".c0{animation-name:c0}.c1{animation-name:c1}.c2{animation-name:c2}",
            "@keyframes c0{0%,8%{opacity:.45}12%,24%{opacity:1}28%,100%{opacity:.45}}",
            "@keyframes c1{0%,20%{opacity:.45}24%,34%{opacity:1}38%,100%{opacity:.45}}",
            "@keyframes c2{0%,30%{opacity:.45}34%,44%{opacity:1}48%,100%{opacity:.45}}",
            ".bob{animation:bob 2.6s ease-in-out infinite alternate}",
            "@keyframes bob{from{transform:translateY(0)}to{transform:translateY(2.5px)}}",
            ".blink{transform-box:fill-box;transform-origin:center;animation:blink 5s infinite}",
            "@keyframes blink{0%,94%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}",
            ".type{animation:type .45s ease-in-out infinite alternate}",
            "@keyframes type{from{transform:translateY(0)}to{transform:translateY(-3px)}}",
            # Submit: the corrected configuration travels from the table into the lab.
            # Its static position is just inside the lab wall.
            ".config{animation-name:config}",
            f"@keyframes config{{0%,46%{{opacity:0;transform:translate({sx:.0f}px,{sy:.0f}px)}}"
            f"48%{{opacity:1;transform:translate({sx:.0f}px,{sy:.0f}px)}}"
            f"56%{{opacity:1;transform:translate({ex:.0f}px,{ey:.0f}px)}}"
            f"59%,100%{{opacity:0;transform:translate({ex:.0f}px,{ey:.0f}px)}}}}",
            # The firewall opening for web traffic exists only after the change.
            ".gap{animation-name:gap}",
            "@keyframes gap{0%,57%{opacity:0}60%,94%{opacity:1}100%{opacity:0}}",
            ".applied{animation-name:applied;opacity:0}",
            "@keyframes applied{0%,56%{opacity:0}59%{opacity:.9}66%,100%{opacity:0}}",
            # 3 network: allowed and blocked routes appear after the change.
            ".route{stroke-dasharray:1;stroke-dashoffset:0;animation-name:route}",
            "@keyframes route{0%,58%{stroke-dashoffset:1}70%,94%{stroke-dashoffset:0}100%{stroke-dashoffset:1}}",
            ".deny{animation-name:deny}",
            "@keyframes deny{0%,70%{opacity:0}73%,94%{opacity:1}100%{opacity:0}}",
            move_track("ok", ALLOWED, 60, 70),
            ".pok{animation-name:ok;opacity:0}",
            move_track("bad", BLOCKED, 61, 70),
            ".pbad{animation-name:bad;opacity:0}",
            # 4 evaluator: probes run from outside, then each check is marked.
            ".probe{stroke-dasharray:5 6;animation:probe 1.2s linear infinite}",
            "@keyframes probe{to{stroke-dashoffset:-11}}",
            ".probes{animation-name:probes;opacity:.9}",
            "@keyframes probes{0%,72%{opacity:.25}76%,92%{opacity:.9}100%{opacity:.25}}",
            ".m0{animation-name:m0}.m1{animation-name:m1}",
            "@keyframes m0{0%,78%{opacity:0}81%,96%{opacity:1}100%{opacity:0}}",
            "@keyframes m1{0%,83%{opacity:0}86%,96%{opacity:1}100%{opacity:0}}",
            # 5 result.
            ".result{animation-name:result}",
            "@keyframes result{0%,87%{opacity:.3}90%,96%{opacity:1}100%{opacity:.3}}",
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}}",
        )
    )


def agent(cx, body, eyes, delay):
    return "".join(
        (
            f'<g class="bob" style="animation-delay:{delay}s">',
            f'<line x1="{cx}" y1="222" x2="{cx}" y2="211" stroke="{body}" stroke-width="3"/>',
            f'<circle cx="{cx}" cy="209" r="4.5" fill="{body}"/>',
            f'<rect x="{cx - 28}" y="222" width="56" height="42" rx="14" fill="{body}"/>',
            f'<rect x="{cx - 20}" y="231" width="40" height="21" rx="8" fill="{{visor}}"/>',
            f'<g class="blink" style="animation-delay:{delay * 1.7}s">',
            f'<circle cx="{cx - 8}" cy="241.5" r="3.6" fill="{eyes}"/>',
            f'<circle cx="{cx + 8}" cy="241.5" r="3.6" fill="{eyes}"/></g>',
            f'<rect x="{cx - 30}" y="266" width="60" height="60" rx="16" fill="{body}" opacity=".85"/>',
            "</g>",
            # Laptop lid seen from behind, hands typing on either side.
            f'<rect x="{cx - 34}" y="290" width="68" height="40" rx="4" fill="{{lid}}"/>',
            f'<circle cx="{cx}" cy="309" r="4" fill="{eyes}" opacity=".8"/>',
            f'<circle class="type" cx="{cx - 40}" cy="324" r="6" fill="{body}"/>',
            f'<circle class="type" style="animation-delay:.22s" cx="{cx + 40}" cy="324" r="6" fill="{body}"/>',
        )
    )


def server(cx, cy, name):
    x, y = cx - 38, cy - 30
    rows = "".join(
        f'<rect x="{x + 10}" y="{y + 10 + 14 * i}" width="56" height="9" rx="2" fill="{{bg}}"/>'
        f'<circle cx="{x + 58}" cy="{y + 14.5 + 14 * i}" r="2.2" fill="{{ok}}"/>'
        for i in range(3)
    )
    return (
        f'<rect x="{x}" y="{y}" width="76" height="60" rx="6" fill="{{node}}" stroke="{{line}}"/>'
        + rows
        + text(cx, y - 10, name, anchor="middle")
    )


def firewall():
    y0, y1 = WALL_Y
    parts = [
        f'<rect x="400" y="{y0}" width="232" height="{y1 - y0}" rx="3" fill="{{brick}}"/>'
    ]
    for row, y in enumerate((y0, (y0 + y1) / 2)):
        offset = 0 if row == 0 else 14
        for x in range(400 + offset, 632, 28):
            parts.append(
                f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 12}" stroke="{{brick_line}}"/>'
            )
    parts.append(
        f'<line x1="400" y1="{(y0 + y1) / 2}" x2="632" y2="{(y0 + y1) / 2}" stroke="{{brick_line}}"/>'
    )
    # The opening the corrected rules leave for web traffic.
    parts.append(
        f'<g class="loop gap"><rect x="{WEB[0] - 11}" y="{y0 - 1}" width="22" height="{y1 - y0 + 2}" fill="{{bg}}"/>'
        f'<rect x="{WEB[0] - 11}" y="{y0 - 1}" width="22" height="{y1 - y0 + 2}" fill="{{lab}}"/></g>'
    )
    parts.append(
        f'<rect x="478" y="{y0 + 2}" width="76" height="20" rx="4" fill="{{panel}}"/>'
    )
    parts.append(text(516, y0 + 17, "firewall", size=14, fill="muted", anchor="middle"))
    return "".join(parts)


def check(y, label, cls):
    return (
        f'<circle cx="686" cy="{y - 5}" r="9" fill="{{ok}}" class="loop {cls}"/>'
        f'<path d="M681.5 {y - 5} l3 3 l5.5 -6" stroke="{{panel}}" stroke-width="2" fill="none" class="loop {cls}"/>'
        + text(704, y, label)
    )


def scene(layout):
    width, height = layout["size"]
    start, end = config_path(layout)
    a = ['<rect width="100%" height="100%" fill="{bg}"/>']
    for y, h in layout["floors"]:
        a.append(f'<rect x="0" y="{y}" width="{width}" height="{h}" fill="{{floor}}"/>')
    if layout["config_line"]:
        a.append(
            f'<path d="{path((start, end))}" stroke="{{line}}" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round" fill="none"/>'
        )
    a.append('<g transform="translate({},{})">'.format(*layout["table"]))
    a.extend(table_zone())
    a.append('</g><g transform="translate({},{})">'.format(*layout["network"]))
    a.extend(network_zone())
    a.append("</g>")
    # The corrected configuration, submitted from the table into the lab.
    rest = layout["config_rest"]
    mx = round(start[0] + (end[0] - start[0]) * rest)
    my = round(start[1] + (end[1] - start[1]) * rest)
    a.append(
        f'<g class="loop config"><path d="M{mx - 13} {my - 16} h17 l9 9 v23 h-26z" fill="{{panel}}" stroke="{{accent}}" stroke-width="2" stroke-linejoin="round"/>'
        f'<path d="M{mx - 7} {my - 2} h14 M{mx - 7} {my + 4} h14 M{mx - 7} {my + 10} h9" stroke="{{accent}}" stroke-width="2" stroke-linecap="round"/></g>'
    )
    a.append(
        text(
            width - 20,
            height - 12,
            "illustration · synthetic scene, not a live run",
            size=14,
            fill="muted",
            anchor="end",
        )
    )
    return "".join(a)


def table_zone():
    a = []
    # 1 task board.
    a.append('<rect x="24" y="24" width="230" height="140" rx="10" fill="{board}"/>')
    a.append(text(40, 50, "① task", fill="muted"))
    a.append('<rect x="40" y="62" width="198" height="88" rx="6" fill="{panel}"/>')
    a.append(
        '<rect x="40" y="62" width="198" height="88" rx="6" fill="none" stroke="{accent}" stroke-width="2.5" class="loop task"/>'
    )
    a.append('<rect x="40" y="62" width="5" height="88" rx="2" fill="{accent}"/>')
    a.append(text(56, 88, "repair routing", size=18, weight="600"))
    a.append(text(56, 110, "and firewall", size=18, weight="600"))
    a.append(
        text(
            56,
            137,
            'web <tspan fill="{ok}">✓</tspan>  admin <tspan fill="{bad}">✗</tspan>',
            fill="muted",
        )
    )

    # 2 agents with tools around one table.
    for i, (cx, _, _, chip) in enumerate(AGENTS):
        width = len(chip) * 9.6 + 20
        a.append(
            f'<g class="loop chip c{i}">'
            f'<rect x="{cx - width / 2:.1f}" y="178" width="{width:.1f}" height="26" rx="13" '
            f'fill="{{panel}}" stroke="{{line}}"/>'
            + text(cx, 196, chip, anchor="middle")
            + "</g>"
        )
    for i, (cx, body, eyes, _) in enumerate(AGENTS):
        a.append(agent(cx, body, eyes, -0.9 * i))
    a.append('<rect x="16" y="330" width="360" height="18" rx="6" fill="{wood}"/>')
    a.append(
        '<rect x="38" y="348" width="10" height="52" fill="{wood}"/><rect x="344" y="348" width="10" height="52" fill="{wood}"/>'
    )
    a.append(text(196, 430, "② agents with tools", fill="muted", anchor="middle"))
    return a


def network_zone():
    a = []
    # 3 isolated Linux network.
    a.append(
        '<rect x="384" y="24" width="264" height="384" rx="14" fill="{lab}" stroke="{accent}" stroke-width="1.5" stroke-dasharray="7 6"/>'
    )
    a.append(text(400, 52, "③ isolated Linux network", fill="muted"))
    a.append(firewall())
    a.append(
        f'<path d="{path(BLOCKED)}" pathLength="1" stroke="{{bad}}" stroke-width="3" fill="none" stroke-linejoin="round" class="loop route"/>'
    )
    a.append(
        f'<path d="{path(ALLOWED)}" pathLength="1" stroke="{{ok}}" stroke-width="3" fill="none" stroke-linejoin="round" class="loop route"/>'
    )
    a.append(
        f'<g class="loop deny"><circle cx="{ADMIN[0]}" cy="226" r="11" fill="{{bad}}"/>'
        f'<path d="M{ADMIN[0] - 4.5} 221.5 l9 9 M{ADMIN[0] + 4.5} 221.5 l-9 9" stroke="{{panel}}" stroke-width="2.2"/></g>'
    )
    cx, cy = CLIENT
    a.append(
        f'<rect x="{cx - 38}" y="{cy - 17}" width="76" height="34" rx="6" fill="{{node}}" stroke="{{line}}"/>'
    )
    a.append(text(cx, cy + 5, "client", anchor="middle"))
    rx, ry = ROUTER
    a.append(
        f'<circle cx="{rx}" cy="{ry}" r="30" fill="none" stroke="{{accent}}" stroke-width="3" class="loop applied"/>'
    )
    a.append(f'<circle cx="{rx}" cy="{ry}" r="22" fill="{{node}}" stroke="{{line}}"/>')
    a.append(
        f'<path d="M{rx - 10} {ry - 4} h18 l-5 -5 M{rx + 10} {ry + 4} h-18 l5 5" stroke="{{ink}}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    a.append(text(rx + 32, ry + 5, "router"))
    a.append(server(*WEB, "web"))
    a.append(server(*ADMIN, "admin"))
    for name, colour, (x, y) in (
        ("pok", "ok", ALLOWED[0]),
        ("pbad", "bad", BLOCKED[0]),
    ):
        a.append(
            f'<circle cx="{x}" cy="{y}" r="6" fill="{{{colour}}}" class="loop {name}"/>'
        )

    # 4 independent evaluator, probing from outside the lab.
    a.append(
        f'<g class="loop probes"><path d="M664 388 H{WEB[0]} V342 M{ADMIN[0]} 388 V342" stroke="{{ink}}" stroke-width="2" fill="none" class="probe"/></g>'
    )
    body, eyes = EVALUATOR
    a.append('<g class="bob" style="animation-delay:-1.3s">')
    a.append(f'<rect x="732" y="170" width="60" height="46" rx="10" fill="{body}"/>')
    a.append('<rect x="740" y="180" width="44" height="22" rx="7" fill="{visor}"/>')
    a.append(
        f'<circle cx="754" cy="191" r="5" fill="none" stroke="{eyes}" stroke-width="2.4"/>'
    )
    a.append(f'<circle cx="772" cy="191" r="3.4" fill="{eyes}"/>')
    a.append(
        f'<rect x="730" y="220" width="64" height="84" rx="16" fill="{body}" opacity=".85"/>'
    )
    a.append(
        f'<line x1="734" y1="252" x2="712" y2="266" stroke="{body}" stroke-width="7" stroke-linecap="round"/>'
    )
    a.append(
        '<circle cx="700" cy="258" r="14" fill="{bg}" fill-opacity=".6" stroke="{ink}" stroke-width="3"/>'
    )
    a.append("</g>")
    a.append(
        '<rect x="664" y="300" width="196" height="108" rx="10" fill="{panel}" stroke="{line}"/>'
    )
    a.append(text(676, 324, "④ independent check", size=15, fill="muted"))
    a.append(check(356, "web reachable", "m0"))
    a.append(check(388, "admin blocked", "m1"))

    # 5 result.
    a.append(
        '<path d="M762 162 V140 m-6 7 l6 -7 l6 7" stroke="{line}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    a.append('<g class="loop result">')
    a.append(
        '<rect x="664" y="24" width="196" height="108" rx="10" fill="{panel}" stroke="{ok}" stroke-width="2"/>'
    )
    a.append(text(680, 50, "⑤ result", fill="muted"))
    a.append('<circle cx="694" cy="83" r="13" fill="{ok}"/>')
    a.append(
        '<path d="M687.5 83 l4.5 4.5 l8 -9" stroke="{panel}" stroke-width="2.6" fill="none"/>'
    )
    a.append(text(716, 93, "pass", size=28, fill="ok", weight="700"))
    a.append(text(680, 120, "both checks hold", size=15, fill="muted"))
    a.append("</g>")
    return a


TITLE = "Agent harness benchmark scene (illustration)"
DESC = (
    "Illustration with synthetic data. Agents at a shared table take the task "
    "'repair routing and firewall' from a board and work with shell, ip route and nft. "
    "A corrected configuration goes into an isolated Linux network with a client, a router, "
    "a firewall and two services. Afterwards web traffic reaches the web service and traffic "
    "to the admin service stops at the firewall. An independent evaluator outside the network "
    "checks that web is reachable and admin is blocked, and the result reads pass."
)


def render(theme, layout):
    pal = THEMES[theme]
    width, height = layout["size"]
    body = scene(layout)
    for key, value in pal.items():
        body = body.replace("{" + key + "}", value)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-labelledby="t d">'
        f'<title id="t">{TITLE}</title><desc id="d">{DESC}</desc>'
        f"<style>{style(layout)}</style>{body}</svg>\n"
    )


def main():
    for name, layout in LAYOUTS.items():
        prefix = "agent-harness-" if name == "wide" else f"agent-harness-{name}-"
        for theme in THEMES:
            (ASSETS / f"{prefix}{theme}.svg").write_text(render(theme, layout), encoding="utf-8")


if __name__ == "__main__":
    main()
