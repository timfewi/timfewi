import { expect, test } from "bun:test";
import { chromium } from "playwright-core";
import { serve } from "./serve.js";

test("renders a looping scene when canvas pixel readback is blocked", async () => {
  const server = serve();
  let browser;
  try {
    browser = await chromium.launch({
      executablePath:
        Bun.which("chromium", { PATH: process.env.PATH }) ?? "chromium",
      args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
    });
    const page = await browser.newPage({
      viewport: { width: 480, height: 360 },
    });
    await page.addInitScript(() => {
      CanvasRenderingContext2D.prototype.getImageData = () => {
        throw new Error("Canvas pixel readback is unavailable");
      };
    });
    await page.goto(server.url.href + "?capture");
    await page.waitForFunction(() => typeof window.renderFrame === "function");
    const canvas = page.locator("canvas");
    async function pose(time) {
      await page.evaluate((t) => window.renderFrame(t), time);
      return canvas.screenshot();
    }
    const start = await pose(0);
    expect(start.equals(await pose(2))).toBe(false);
    expect(start.equals(await pose(8))).toBe(true);
  } finally {
    await browser?.close();
    server.stop(true);
  }
}, 60000);
