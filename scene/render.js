// Requires chromium and the libwebp CLI on PATH. Render an exact eight-second loop.
import { chromium } from "playwright-core";
import { mkdtemp, rm, rename } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { serve } from "./serve.js";

const server = serve();
const assets = fileURLToPath(new URL("../assets/", import.meta.url));
const dir = await mkdtemp(join(assets, ".tentaflake-frames-"));
let browser;
try {
  browser = await chromium.launch({
    executablePath:
      Bun.which("chromium", { PATH: process.env.PATH }) ?? "chromium",
    args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
  });
  const page = await browser.newPage({
    viewport: { width: 960, height: 720 },
    deviceScaleFactor: 1,
  });
  page.on("pageerror", (e) => console.error(e));
  await page.goto(server.url.href + "?capture");
  await page.waitForFunction(() => typeof window.renderFrame === "function");
  // Capture the fixed layout once. Read each WebGL frame synchronously
  // after rendering, before the browser clears its drawing buffer.
  await page.locator("canvas").evaluate((c) => (c.style.visibility = "hidden"));
  const backdrop = await page.screenshot();
  await page
    .locator("canvas")
    .evaluate((c) => (c.style.visibility = "visible"));
  const composite = await page.evaluateHandle(async (base64) => {
    const bg = new Image();
    bg.src = "data:image/png;base64," + base64;
    await bg.decode();
    const canvas = document.createElement("canvas");
    canvas.width = bg.width;
    canvas.height = bg.height;
    return {
      bg,
      ctx: canvas.getContext("2d"),
      scene: document.querySelector("canvas"),
    };
  }, backdrop.toString("base64"));
  const files = [];
  for (let frame = 0; frame < 160; frame++) {
    const png = await composite.evaluate(({ bg, ctx, scene }, seconds) => {
      window.renderFrame(seconds);
      ctx.drawImage(bg, 0, 0);
      ctx.drawImage(scene, 0, 0);
      return ctx.canvas.toDataURL("image/png").split(",")[1];
    }, frame / 20);
    const path = join(dir, `frame-${String(frame).padStart(3, "0")}.png`);
    await Bun.write(path, Buffer.from(png, "base64"));
    files.push(path);
  }
  const encode = async (args) => {
    const proc = Bun.spawn(
      [
        Bun.which(args[0], { PATH: process.env.PATH }) ?? args[0],
        ...args.slice(1),
      ],
      { stdout: "inherit", stderr: "inherit" },
    );
    if ((await proc.exited) !== 0)
      throw new Error(`Encoding failed: ${args[0]}`);
  };
  await encode([
    "cwebp",
    "-quiet",
    "-q",
    "92",
    files[0],
    "-o",
    join(dir, "poster.webp"),
  ]);
  await encode([
    "img2webp",
    "-loop",
    "0",
    "-lossy",
    "-q",
    "83",
    "-m",
    "4",
    "-d",
    "50",
    ...files,
    "-o",
    join(dir, "animation.webp"),
  ]);
  await rename(
    join(dir, "poster.webp"),
    join(assets, "tentaflake-poster.webp"),
  );
  await rename(
    join(dir, "animation.webp"),
    join(assets, "tentaflake-banner.webp"),
  );
} finally {
  await browser?.close();
  server.stop(true);
  await rm(dir, { recursive: true, force: true });
}
