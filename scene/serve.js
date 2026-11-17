import { fileURLToPath } from "node:url";

export function serve() {
  const routes = {
    "/": "index.html",
    "/scene.js": "scene.js",
    "/mark.webp": "../assets/tentaflake-mark.webp",
    "/three.module.js": "node_modules/three/build/three.module.js",
    "/three.core.js": "node_modules/three/build/three.core.js",
  };
  return Bun.serve({
    hostname: "127.0.0.1",
    port: 5178,
    routes: Object.fromEntries(
      Object.entries(routes).map(([url, path]) => {
        const file = Bun.file(fileURLToPath(new URL(path, import.meta.url)));
        return [url, () => new Response(file)];
      }),
    ),
    fetch: () => new Response("Not found", { status: 404 }),
  });
}
if (import.meta.main) console.log(serve().url.href);
