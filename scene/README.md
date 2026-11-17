# Tentaflake profile scene

From this directory, run `bun install --frozen-lockfile` and `bun run preview`.
Open `http://127.0.0.1:5178` for the live WebGL scene. The crystal relief uses
the profile's Tentaflake mark. The tentacles, host, agents and network displays
are animated Three.js geometry.

With Chromium, `cwebp` and `img2webp` on PATH, run `bun run render` to rebuild
the profile artwork. The renderer samples the eight-second loop at 20 frames
per second and exports both the animated WebP and its reduced-motion poster.
