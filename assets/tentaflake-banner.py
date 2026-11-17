"""Rebuild the self-contained profile SVG from the supplied Tentaflake artwork."""

import base64
import struct
import zlib
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
WIDTH, HEIGHT = 2172, 724

# Local displacements in artwork coordinates. The compact falloff keeps the
# lettering, box edges, panel and cable sockets fixed while the creature moves.
# Each tuple gives centre, horizontal/vertical radius and travel in pixels.
FLEX = (
    (1521, 158, 213, 242, 2.0, -7.5),    # crown and head
    (1518, 294, 168, 102, 1.5, -4.0),    # shoulders
    (1277, 285, 148, 61, 1.0, 8.0),      # upper left arm
    (1744, 282, 127, 60, -2.0, -7.5),    # upper right arm
    (983, 408, 94, 153, -9.0, -3.5),     # outside bends
    (1956, 457, 85, 134, 7.5, -3.0),
    (1114, 552, 118, 53, 1.5, 6.0),
    (1804, 547, 125, 54, -1.0, 5.5),
)

# Follow the visible centre lines. The third cable passes behind the front box.
LINKS = (
    ("M1474 292 C1444 326 1412 331 1354 340 S1261 353 1233 385 S1219 426 1194 446", 1192, 447, 0),
    ("M1503 313 C1495 353 1464 370 1455 406 S1453 479 1428 507 Q1408 527 1366 538", 1366, 538, 2.5),
    ("M1539 312 C1546 341 1574 360 1588 389 Q1600 412 1597 434", 1557, 547, 5),
    ("M1567 299 C1601 323 1636 335 1668 352 S1728 393 1738 451", 1738, 451, 7.5),
)


def uri(kind, data):
    return f"data:image/{kind};base64," + base64.b64encode(data).decode("ascii")


def flex_map():
    """Encode a smooth two-axis displacement field at 1/4 resolution as RGB PNG."""
    w, h = WIDTH // 4, HEIGHT // 4
    rows = bytearray()
    for y in range(h):
        rows.append(0)  # PNG scanline without a predictor
        for x in range(w):
            red = green = 127.5
            for cx, cy, rx, ry, dx, dy in FLEX:
                distance = (((x + 0.5) * 4 - cx) / rx) ** 2 + (((y + 0.5) * 4 - cy) / ry) ** 2
                if distance < 1:
                    weight = (1 - distance) ** 2 * 255 / 24
                    red += dx * weight
                    green += dy * weight
            rows.extend((round(red), round(green), 0))

    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload)))

    header = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


def signal(curve, x, y, delay):
    return f'''<g style="--delay:-{delay}s">
      <path class="signal" d="{curve}" pathLength="100"/>
      <ellipse class="socket" cx="{x}" cy="{y}" rx="12" ry="5"/>
    </g>'''


def render():
    artwork = uri("webp", (ASSETS / "tentaflake-banner.webp").read_bytes())
    motion = uri("png", flex_map())
    signals = "\n    ".join(signal(*link) for link in LINKS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Tentaflake — isolated AI agents</title>
  <desc id="desc">A blue crystal kraken flexes its arms above four glass agent enclosures. Signals travel from the kraken to the agents beside a tentaflake.toml panel.</desc>
  <style>
    .signal, .socket {{ fill:none; stroke:#a4faff; opacity:0; animation-delay:var(--delay); }}
    .signal {{ stroke-width:3.4; stroke-linecap:round; stroke-dasharray:6 110;
      animation-name:transmit; animation-duration:10s; animation-iteration-count:infinite; }}
    .socket {{ stroke-width:2; transform-box:fill-box; transform-origin:center;
      animation-name:receive; animation-duration:10s; animation-iteration-count:infinite; }}
    @keyframes transmit {{
      0% {{ stroke-dashoffset:6; opacity:0; }} 4% {{ opacity:.86; }}
      20% {{ opacity:.86; }} 25%, 100% {{ stroke-dashoffset:-100; opacity:0; }}
    }}
    @keyframes receive {{
      0%, 21% {{ opacity:0; transform:scale(.8); }} 25% {{ opacity:.95; }}
      35%, 100% {{ opacity:0; transform:scale(1.9); }}
    }}
    @media (prefers-reduced-motion:reduce) {{ .moving {{ display:none; }} }}
  </style>
  <defs>
    <image id="art" href="{artwork}" width="{WIDTH}" height="{HEIGHT}"/>
    <filter id="flex" filterUnits="userSpaceOnUse" x="880" y="0" width="1180" height="660" color-interpolation-filters="sRGB">
      <feImage href="{motion}" x="0" y="0" width="{WIDTH}" height="{HEIGHT}" preserveAspectRatio="none" result="field"/>
      <feDisplacementMap in="SourceGraphic" in2="field" xChannelSelector="R" yChannelSelector="G" scale="0">
        <animate attributeName="scale" values="0;24;0;-24;0" dur="7s" repeatCount="indefinite"
          calcMode="spline" keySplines=".37 0 .63 1;.37 0 .63 1;.37 0 .63 1;.37 0 .63 1"/>
      </feDisplacementMap>
    </filter>
  </defs>
  <use href="#art"/>
  <g class="moving" filter="url(#flex)">
    <use href="#art"/>
    {signals}
  </g>
</svg>
'''


if __name__ == "__main__":
    (ASSETS / "tentaflake-banner.svg").write_text(render(), encoding="utf-8")
