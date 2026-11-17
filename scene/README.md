# Tentaflake profile scene

From this directory, run `bun install --frozen-lockfile` and `bun run preview`.
Open `http://127.0.0.1:5178` for the live WebGL scene. The crystal relief uses
the profile's Tentaflake mark and its precomputed outline. The controller
connects eight work bays with jacketed data cables. Each agent collects a
cartridge from its rack and walks to a terminal. The terminal traces a route
through the cartridge’s simulated network and displays the result.

With Chromium on PATH, run `bun test` to check rendering with canvas pixel
readback blocked and verify the loop seam.

With Chromium, `cwebp` and `img2webp` on PATH, run `bun run render` to rebuild
the profile artwork. The renderer samples the eight-second loop at 20 frames
per second and exports both the animated WebP and its reduced-motion poster.
