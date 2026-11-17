import * as T from "three";
import { markOutline } from "./mark-outline.js";

const tau = 2 * Math.PI;
const vec = (x, y, z) => new T.Vector3(x, y, z);
const renderer = new T.WebGLRenderer({
  canvas: document.querySelector("canvas"),
  antialias: true,
  alpha: true,
  powerPreference: "low-power",
});
renderer.setClearColor(0, 0);
renderer.toneMapping = T.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = T.PCFShadowMap;
const scene = new T.Scene();
const camera = new T.OrthographicCamera(-7.5, 7.5, 5.625, -5.625, 0.1, 80);
camera.position.set(0, 12.7, 21);
camera.lookAt(0, 1.65, 0);

function mesh(parent, geometry, material, x = 0, y = 0, z = 0) {
  const obj = new T.Mesh(geometry, material);
  obj.position.set(x, y, z);
  parent.add(obj);
  return obj;
}
function group(parent, x = 0, y = 0, z = 0) {
  const g = new T.Group();
  g.position.set(x, y, z);
  parent.add(g);
  return g;
}
function metal(color, metalness = 0.55, roughness = 0.3) {
  return new T.MeshStandardMaterial({ color, metalness, roughness });
}
const flat = (color) => new T.MeshBasicMaterial({ color });
const boxGeo = new T.BoxGeometry();
function box(parent, x, y, z, w, h, d, mat) {
  const o = mesh(parent, boxGeo, mat, x, y, z);
  o.scale.set(w, h, d);
  return o;
}
const ballGeo = new T.SphereGeometry(1, 28, 20);
function oval(parent, x, y, z, w, h, d, mat) {
  const o = mesh(parent, ballGeo, mat, x, y, z);
  o.scale.set(w, h, d);
  return o;
}
function disc(parent, x, y, z, r, h, mat) {
  return mesh(parent, new T.CylinderGeometry(r, r, h, 48), mat, x, y, z);
}
function hoop(parent, x, y, z, r, thickness, mat) {
  return mesh(parent, new T.TorusGeometry(r, thickness, 8, 80), mat, x, y, z);
}
function line(parent, points, color, opacity = 1) {
  const geo = new T.BufferGeometry().setFromPoints(
    points.map((p) => vec(...p)),
  );
  const l = new T.Line(
    geo,
    new T.LineBasicMaterial({ color, transparent: opacity < 1, opacity }),
  );
  parent.add(l);
  return l;
}

const armor = metal(0x44546e, 0.56, 0.37),
  graphite = metal(0x182435),
  steel = metal(0x8299b3);
const deck = metal(0x263851, 0.48, 0.48),
  bevel = metal(0x435776),
  night = metal(0x101b30);
const ice = metal(0x45aeef, 0.38, 0.25),
  cyan = flat(0x80e6ff);
const jobAmber = flat(0xffb75b),
  jobGreen = flat(0x61e9b2);
function light(color, intensity, position) {
  const l = new T.DirectionalLight(color, intensity);
  l.position.set(...position);
  scene.add(l);
}
scene.add(new T.HemisphereLight(0xdcf0ff, 0x253e77, 1.35));
const key = new T.DirectionalLight(0xe7f4ff, 2.85);
key.position.set(-5, 9, 6);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, {
  left: -7,
  right: 7,
  top: 7,
  bottom: -7,
  near: 0.1,
  far: 27,
});
key.shadow.normalBias = 0.025;
key.shadow.bias = -0.00025;
scene.add(key);
light(0x548aff, 2.3, [6, 3, -4]);
light(0x86e6ff, 2.2, [-4, 6, -5]);

// Studio reflections give the curved arms continuous ribbons of light.
function studioEnvironment() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 256;
  const g = c.getContext("2d");
  g.fillStyle = "#283046";
  g.fillRect(0, 0, 512, 256);
  for (const [x, y, w, h, color] of [
    [46, 46, 78, 15, "#f5fbff"],
    [150, 34, 14, 96, "#c0dfff"],
    [282, 58, 98, 18, "#568eff"],
    [412, 64, 13, 85, "#efffff"],
    [0, 136, 512, 15, "#47597c"],
  ]) {
    g.fillStyle = color;
    g.fillRect(x, y, w, h);
  }
  const t = new T.CanvasTexture(c);
  t.mapping = T.EquirectangularReflectionMapping;
  t.colorSpace = T.SRGBColorSpace;
  scene.environment = t;
}
studioEnvironment();

// The square host is machined in stacked layers. Its diamond silhouette comes from the camera.
const floor = group(scene);
floor.scale.set(1.16, 1, 1.16);
const slab = group(floor);
slab.rotation.y = Math.PI / 4;
box(slab, 0, -0.28, 0, 8.38, 0.47, 8.38, night);
box(slab, 0, -0.071, 0, 8.43, 0.035, 8.43, metal(0x3771aa));
box(slab, 0, -0.025, 0, 8.38, 0.065, 8.38, bevel);
box(slab, 0, 0.015, 0, 8.27, 0.035, 8.27, deck).receiveShadow = true;
for (let k = -3.6; k < 4; k += 0.6) {
  line(
    slab,
    [
      [k, 0.035, -4.12],
      [k, 0.035, 4.12],
    ],
    0x527295,
    0.23,
  );
  line(
    slab,
    [
      [-4.12, 0.035, k],
      [4.12, 0.035, k],
    ],
    0x527295,
    0.23,
  );
}
for (let n = -3.6; n < 4; n += 1.2)
  for (const s of [-1, 1]) {
    box(slab, n, -0.22, s * 4.197, 0.045, 0.018, 0.01, cyan);
    box(slab, s * 4.197, -0.22, n, 0.01, 0.018, 0.045, cyan);
  }
disc(scene, 0, 0.07, 0, 1.24, 0.1, graphite);
hoop(scene, 0, 0.125, 0, 1.06, 0.028, ice).rotation.x = Math.PI / 2;

function aura(parent, color, radius, position) {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const ctx = c.getContext("2d"),
    ramp = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  ramp.addColorStop(0, "rgba(255,255,255,.68)");
  ramp.addColorStop(0.42, "rgba(255,255,255,.26)");
  ramp.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = ramp;
  ctx.fillRect(0, 0, 128, 128);
  const sprite = new T.Sprite(
    new T.SpriteMaterial({
      map: new T.CanvasTexture(c),
      color,
      blending: T.AdditiveBlending,
      depthWrite: false,
      transparent: true,
    }),
  );
  sprite.position.set(...position);
  sprite.scale.setScalar(radius * 2);
  parent.add(sprite);
}
aura(scene, 0x245fcf, 3.6, [0, 3.65, -2.1]);

// The alpha outline is authored once. Rendering the mark never reads canvas
// pixels, which some browsers deliberately randomise for fingerprint protection.
const mark = await new T.TextureLoader().loadAsync("/mark.webp");
mark.colorSpace = T.SRGBColorSpace;
function contourPoints(coords) {
  const points = [];
  for (let i = 0; i < coords.length; i += 2)
    points.push(
      new T.Vector2(
        (coords[i] / 200 - 0.5) * 4.9,
        (0.5 - coords[i + 1] / 200) * 4.9,
      ),
    );
  return points;
}
const silhouettes = markOutline.map(([perimeter, ...holes]) => {
  const shape = new T.Shape(contourPoints(perimeter));
  shape.holes = holes.map((hole) => new T.Path(contourPoints(hole)));
  return shape;
});
const logoGeo = new T.ExtrudeGeometry(silhouettes, {
  depth: 0.18,
  bevelEnabled: true,
  bevelSize: 0.012,
  bevelThickness: 0.018,
  bevelSegments: 1,
});
const coords = logoGeo.attributes.position,
  logoUV = logoGeo.attributes.uv;
for (let i = 0; i < coords.count; i++)
  logoUV.setXY(i, coords.getX(i) / 4.9 + 0.5, coords.getY(i) / 4.9 + 0.5);
const face = new T.MeshStandardMaterial({
  map: mark,
  alphaTest: 0.3,
  emissiveMap: mark,
  emissive: 0xffffff,
  emissiveIntensity: 0.4,
  roughness: 0.42,
  metalness: 0.2,
});
const head = mesh(scene, logoGeo, [face, metal(0x153f82, 0.44, 0.33)]);
const headHeight = 4.17;
head.scale.setScalar(1.3);
head.position.set(0, headHeight, -0.12);
head.rotation.x = -0.19;
// Under the crystal plates the mantle comes to a dark beak. Each folded
// cheek catches a different light, keeping the face legible between the arms.
const maskGeo = new T.BufferGeometry();
maskGeo.setAttribute(
  "position",
  new T.Float32BufferAttribute(
    [
      -1.04, -0.78, -0.14, -0.34, -0.8, 0.22, 0, -1.42, 0.4, -1.04, -0.78,
      -0.14, 0, -1.42, 0.4, 0, -2.29, -0.02, 0, -2.29, -0.02, 0, -1.42, 0.4,
      1.04, -0.78, -0.14, 0, -1.42, 0.4, 0.34, -0.8, 0.22, 1.04, -0.78, -0.14,
      -0.34, -0.8, 0.22, 0.34, -0.8, 0.22, 0, -1.42, 0.4,
    ],
    3,
  ),
);
maskGeo.computeVertexNormals();
const shell = metal(0x102d61, 0.42, 0.35);
shell.side = T.DoubleSide;
mesh(head, maskGeo, shell, 0, 0, -0.3);
// Machined controller chassis with ports on both sides and stacked heat sinks.
const hub = group(scene, 0, 0.12, -0.04);
disc(hub, 0, 0.25, 0, 0.83, 0.46, graphite);
box(hub, 0, 1.04, 0, 1.18, 1.54, 0.94, night);
for (let i = 0; i < 6; i++)
  box(hub, 0, 0.52 + i * 0.19, 0, 1.29, 0.095, 1.03, armor);
box(hub, 0, 1.64, 0.46, 0.8, 0.17, 0.06, graphite);
box(hub, 0, 1.64, 0.5, 0.54, 0.035, 0.025, cyan);

const cobalt = new T.Color(0x184bc0),
  azure = new T.Color(0x328aef),
  frost = new T.Color(0x91dfff);
const jacket = metal(0xffffff, 0.39, 0.29);
jacket.vertexColors = true;
// Tile one small woven sleeve texture on every jacket, with no extra geometry.
const weaveSize = 32,
  weavePixels = new Uint8Array(weaveSize * weaveSize * 4);
for (let y = 0; y < weaveSize; y++)
  for (let x = 0; x < weaveSize; x++) {
    const over = (x + y) % 8 < 3,
      under = (x - y + weaveSize) % 8 < 3;
    const v = over ? 246 : under ? 218 : 185;
    weavePixels.set([v, v, v, 255], 4 * (y * weaveSize + x));
  }
const weave = new T.DataTexture(weavePixels, weaveSize, weaveSize);
weave.wrapS = weave.wrapT = T.RepeatWrapping;
weave.repeat.set(10, 2);
weave.magFilter = T.LinearFilter;
weave.minFilter = T.LinearMipmapLinearFilter;
weave.generateMipmaps = true;
weave.needsUpdate = true;
jacket.map = weave;
jacket.bumpMap = weave;
jacket.bumpScale = 0.006;

const socket = metal(0x495669, 0.72, 0.31),
  boot = metal(0x172333, 0.14, 0.61);
const collars = new T.CylinderGeometry(1, 1, 1, 12);
const up = vec(0, 1, 0),
  forward = vec(0, 0, 1);
function ferrule(parent, p, direction, radius, length, material) {
  const part = mesh(parent, collars, material, p.x, p.y, p.z);
  part.scale.set(radius, length, radius);
  part.quaternion.setFromUnitVectors(up, direction);
  return part;
}
// Like the office illustration, each lead has a full shoulder at the hub
// and tapers into its plug. The fibre highlight follows the round sleeve.
function cable(parent, points, rootRadius, tipRadius) {
  const curve = new T.CatmullRomCurve3(points.map((p) => vec(...p)));
  const radiusAt = (u) => tipRadius + (rootRadius - tipRadius) * (1 - u) ** 1.5;
  const rings = 48,
    sides = 16;
  const geo = new T.TubeGeometry(curve, rings, 1, sides, false);
  const centers = curve.getSpacedPoints(rings);
  const pos = geo.attributes.position,
    normals = geo.attributes.normal;
  const colors = [],
    color = new T.Color();
  for (let i = 0; i <= rings; i++) {
    const u = i / rings,
      center = centers[i],
      radius = radiusAt(u);
    for (let j = 0; j <= sides; j++) {
      const k = i * (sides + 1) + j;
      const nx = normals.getX(k),
        ny = normals.getY(k),
        nz = normals.getZ(k);
      pos.setXYZ(
        k,
        center.x + nx * radius,
        center.y + ny * radius,
        center.z + nz * radius,
      );
      const light = Math.max(0, -0.52 * nx + 0.79 * ny + 0.32 * nz);
      color
        .copy(cobalt)
        .lerp(azure, 0.62 * light)
        .lerp(frost, 0.7 * light ** 8);
      colors.push(color.r, color.g, color.b);
    }
  }
  geo.setAttribute("color", new T.Float32BufferAttribute(colors, 3));
  mesh(parent, geo, jacket).castShadow = true;
  for (const u of [0, 1]) {
    const tip = centers[u * rings],
      r = radiusAt(u);
    const direction = curve.getTangentAt(u).multiplyScalar(u ? -1 : 1);
    const at = (d) => tip.clone().addScaledVector(direction, d * r);
    ferrule(parent, at(0.18), direction, r * 1.17, r * 0.55, socket);
    ferrule(parent, at(0.69), direction, r * 1.06, r * 0.65, boot);
    ferrule(parent, at(0.94), direction, r * 1.1, r * 0.16, ice);
  }
  return { curve, radiusAt };
}
const spots = [
  [-2.18, -2.24],
  [2.18, -2.24],
  [-3.68, -0.38],
  [3.68, -0.38],
  [-2.75, 1.86],
  [2.75, 1.86],
  [-1.11, 3.68],
  [1.11, 3.68],
];
const cells = [];
const ease = T.MathUtils.smoothstep;

// Each cartridge contains a small synthetic network. Record the actual
// traversal so the console can replay its checks at any export timestamp.
function checkRoutes(index) {
  const links = [[1], [2], index === 5 ? [] : [3], []];
  const visited = new Set([0]),
    order = [0];
  for (const node of order)
    for (const peer of links[node]) {
      if (!visited.has(peer)) {
        visited.add(peer);
        order.push(peer);
      }
    }
  return { order, reachable: visited.has(3) };
}

// Each bay has its own controller uplink, pull-out cartridge tray and build terminal.
// The route curves around the cabinet to the keyboard, entirely inside that bay.
function workcell(station, sign, index) {
  const rack = group(station);
  rack.rotation.y = -sign * 0.72;
  box(rack, 0, 0.56, 0, 0.57, 1.08, 0.46, graphite);
  box(rack, 0, 0.065, 0, 0.66, 0.1, 0.55, steel);
  box(rack, 0, 1.1, 0, 0.62, 0.06, 0.51, armor);
  disc(rack, 0, 1.145, 0, 0.12, 0.06, steel);
  hoop(rack, 0, 1.17, 0, 0.08, 0.012, cyan).rotation.x = Math.PI / 2;
  for (let slot = 0; slot < 5; slot++) {
    const y = 0.24 + slot * 0.165;
    box(rack, 0, y, 0.246, 0.48, 0.119, 0.051, armor);
    box(rack, -0.056, y, 0.275, 0.27, 0.026, 0.012, night);
    box(rack, 0.177, y, 0.277, 0.043, 0.023, 0.014, slot % 2 ? cyan : jobGreen);
  }
  const drawer = group(rack, 0, 0.6, 0.25);
  box(drawer, 0, 0, 0, 0.48, 0.096, 0.16, steel);
  box(drawer, 0, 0, 0.088, 0.2, 0.035, 0.025, jobAmber);

  const console = group(station, sign * 1.11, 0, -0.16);
  console.rotation.y = -sign * 0.3;
  box(console, 0, 0.32, 0, 0.55, 0.59, 0.36, graphite);
  box(console, 0, 0.54, 0.15, 0.84, 0.081, 0.51, steel);
  box(console, -0.1, 0.588, 0.22, 0.42, 0.018, 0.21, night);
  for (let row = 0; row < 3; row++)
    box(console, -0.1, 0.601, 0.155 + row * 0.055, 0.34, 0.012, 0.018, armor);
  const reader = box(console, 0.25, 0.6, 0.22, 0.16, 0.04, 0.16, night);
  box(console, 0, 0.63, -0.09, 0.095, 0.18, 0.08, armor);
  const monitor = group(console, 0, 0.92, -0.09);
  box(monitor, 0, 0, 0, 0.94, 0.55, 0.065, armor);
  box(monitor, 0, 0, 0.043, 0.86, 0.47, 0.025, night);
  // Terminal header, task steps and progress are drawn on the physical screen.
  box(monitor, -0.13, 0.158, 0.065, 0.48, 0.032, 0.012, cyan);
  const trace = checkRoutes(index);
  const nodes = [
    [-0.3, 0],
    [-0.12, -0.05],
    [0.087, 0.05],
    [0.29, -0.025],
  ];
  const ports = nodes.map(([x, y], i) => {
    if (i > 0)
      line(
        monitor,
        [
          [...nodes[i - 1], 0.072],
          [x, y, 0.072],
        ],
        0x6986a7,
      );
    return oval(monitor, x, y, 0.083, 0.035, 0.035, 0.014, armor);
  });
  box(monitor, 0, -0.16, 0.065, 0.72, 0.049, 0.012, graphite);
  const progress = box(monitor, 0, -0.16, 0.078, 0.72, 0.042, 0.012, jobGreen);
  const lamp = oval(console, 0.37, 0.59, -0.02, 0.04, 0.024, 0.04, jobAmber);

  const route = new T.CatmullRomCurve3([
    vec(-sign * 0.55, 0, 0.24),
    vec(-sign * 0.44, 0, 0.65),
    vec(sign * 0.15, 0, 0.88),
    vec(sign * 0.76, 0, 0.82),
    vec(sign * 1.07, 0, 0.52),
  ]);
  const routePts = route.getPoints(20);
  line(
    station,
    routePts.map((v) => [v.x, 0.009, v.z]),
    0x537598,
    0.66,
  );
  for (let j = 1; j < routePts.length; j += 4) {
    const pt = routePts[j];
    box(station, pt.x, 0.012, pt.z, 0.075, 0.01, 0.04, ice);
  }
  box(station, sign * 0.53, 0.032, -0.18, 1.22, 0.048, 0.089, graphite);
  return { route, drawer, progress, lamp, reader, sign, index, trace, ports };
}

const ceramic = metal(0x8194ad, 0.43, 0.38);
const panelGeo = new T.OctahedronGeometry(1);
for (let i = 0; i < spots.length; i++) {
  const [x, z] = spots[i],
    s = Math.sign(x),
    row = Math.floor(i / 2);
  const station = group(scene, x, 0.04, z);
  const cell = workcell(station, s, i);
  const g = group(station);
  const limbs = [];
  let carried;
  for (const side of [-1, 1]) {
    const hip = group(g, side * 0.105, 0.39, 0);
    box(hip, 0, -0.33, 0.035, 0.138, 0.12, 0.195, graphite);
    box(hip, 0, -0.16, 0, 0.116, 0.31, 0.13, armor);
    const shin = mesh(hip, panelGeo, ceramic, 0, -0.17, 0.072);
    shin.scale.set(0.071, 0.13, 0.048);
    box(hip, 0, -0.295, 0.116, 0.116, 0.042, 0.042, steel);
    const shoulder = group(g, side * 0.222, 0.7, 0);
    oval(shoulder, 0, -0.12, 0, 0.08, 0.19, 0.085, armor);
    oval(shoulder, side * 0.028, -0.26, 0.02, 0.057, 0.082, 0.062, graphite);
    const pauldron = mesh(shoulder, panelGeo, ceramic, side * 0.015, -0.035, 0);
    pauldron.scale.set(0.135, 0.105, 0.126);
    box(shoulder, 0, -0.2, 0.06, 0.116, 0.071, 0.069, steel);
    shoulder.rotation.z = side * 0.16;
    if (side === 1)
      carried = box(shoulder, 0, -0.3, 0.045, 0.18, 0.084, 0.09, jobAmber);
    limbs.push({ shoulder, hip, side });
  }
  const torso = mesh(
    g,
    new T.CylinderGeometry(0.233, 0.148, 0.36, 6),
    armor,
    0,
    0.55,
    0,
  );
  torso.rotation.y = Math.PI / 6;
  for (const side of [-1, 1]) {
    const plate = mesh(g, panelGeo, ceramic, side * 0.09, 0.625, 0.148);
    plate.scale.set(0.12, 0.108, 0.058);
    plate.rotation.z = -side * 0.25;
    oval(g, side * 0.16, 0.855, 0.015, 0.046, 0.084, 0.078, steel);
  }
  box(g, 0, 0.46, 0.15, 0.21, 0.052, 0.054, graphite);
  box(g, 0, 0.465, 0.18, 0.068, 0.035, 0.018, steel);
  box(g, 0, 0.61, 0.164, 0.081, 0.029, 0.022, cyan);
  oval(g, 0, 0.85, 0, 0.188, 0.176, 0.15, graphite);
  box(g, 0, 0.863, 0.126, 0.24, 0.063, 0.05, night);
  box(g, 0, 0.87, 0.155, 0.183, 0.028, 0.012, cyan);
  // A ceramic brow overhangs the inset, illuminated visor.
  box(g, 0, 0.928, 0.105, 0.267, 0.044, 0.095, ceramic);
  box(g, 0, 0.798, 0.127, 0.116, 0.055, 0.055, armor);
  g.traverse((o) => {
    if (o.isMesh) o.castShadow = true;
  });
  const y = 1.21;
  const portY = row % 2 === 0 ? 1.76 : 1.11;
  const root = [s * 0.64, portY, row < 2 ? -0.36 : 0.34];
  const uplink = cable(
    scene,
    [
      root,
      [s * 1.14, portY - 0.04, root[2]],
      [s * (Math.abs(x) * 0.66 + 0.16), 1.03 + row * 0.08, z * 0.45],
      [x * 0.9, 1.62, z * 0.84],
      [x, 1.52, z],
      [x, y, z],
    ],
    0.255,
    0.118,
  );
  const dispatch = hoop(scene, 0, 0, 0, 1, 0.095, cyan);
  cells.push({ ...cell, worker: g, limbs, carried, uplink, dispatch });
}
// Rear partitions frame the room like the agent office. Its queue and
// completion boards use the same job clocks as the workers on the floor.
const boardCards = [];
for (const side of [-1, 1]) {
  const wall = group(scene, side * 3.15, 0.04, -3.46);
  wall.rotation.y = (-side * Math.PI) / 4;
  box(wall, 0, 0.99, 0, 3.35, 1.98, 0.113, armor);
  box(wall, 0, 0.96, 0.075, 3.16, 1.67, 0.06, deck);
  box(wall, 0, 2.0, 0, 3.4, 0.06, 0.18, steel);
  box(wall, 0, 1.08, 0.12, 2.66, 1.22, 0.07, night);
  for (let c = 0; c < 3; c++) {
    box(
      wall,
      (c - 1) * 0.8,
      1.48,
      0.167,
      0.62,
      0.042,
      0.025,
      c === 2 ? jobGreen : ice,
    );
    box(wall, (c - 1) * 0.8, 1.01, 0.165, 0.71, 0.76, 0.026, graphite);
  }
  for (let i = 0; i < 4; i++) {
    const card = box(
      wall,
      0,
      0.75 + i * 0.167,
      0.197,
      0.5,
      0.1,
      0.035,
      ceramic,
    );
    boardCards.push({ card, cell: cells[2 * i + (side > 0 ? 1 : 0)] });
  }
  // Underfloor trunk runs along the bevel with both ends on the chassis.
  cable(
    scene,
    [
      [side * 0.7, -0.3, 6.15],
      [side * 1.0, -0.58, 6.03],
      [side * 2.54, -0.68, 4.56],
      [side * 4.88, -0.58, 2.25],
      [side * 5.18, -0.31, 1.71],
    ],
    0.155,
    0.13,
  );
}

// Repeated fixed props share draw calls. Animated limbs and job indicators
// keep their own transforms and materials.
const moving = new Set([
  head,
  ...cells.flatMap((c) => [
    c.worker,
    c.drawer,
    c.progress,
    c.lamp,
    c.reader,
    c.dispatch,
    ...c.ports,
  ]),
  ...boardCards.map((b) => b.card),
]);
function batchFixedProps() {
  const batches = new Map();
  scene.updateMatrixWorld(true);
  function collect(object) {
    if (moving.has(object)) return;
    if (object.isMesh && !Array.isArray(object.material)) {
      const key = [
        object.geometry.uuid,
        object.material.uuid,
        object.castShadow,
        object.receiveShadow,
      ].join("/");
      if (!batches.has(key)) batches.set(key, []);
      batches.get(key).push(object);
    }
    object.children.forEach(collect);
  }
  collect(scene);
  for (const matches of batches.values()) {
    if (matches.length < 3) continue;
    const [first] = matches;
    const batch = new T.InstancedMesh(
      first.geometry,
      first.material,
      matches.length,
    );
    batch.castShadow = first.castShadow;
    batch.receiveShadow = first.receiveShadow;
    matches.forEach((obj, i) => {
      batch.setMatrixAt(i, obj.matrixWorld);
      obj.removeFromParent();
    });
    scene.add(batch);
  }
}
batchFixedProps();

// One complete job: dispatch, pick up a cartridge, walk to the terminal,
// load and run it, then return to the rack. Every pose is a function of time
// so live playback and the exported loop use the same simulation.
function updateCell(cell, seconds) {
  const {
    route,
    sign,
    index,
    worker,
    limbs,
    carried,
    progress,
    drawer,
    lamp,
    reader,
    dispatch,
    uplink,
  } = cell;
  const clock = (seconds + index * 0.97) % 8;
  const outward = ease(clock, 1.15, 3.25);
  const returning = ease(clock, 5.55, 7.7);
  const u = outward - returning;
  const p = route.getPointAt(u);
  const travel = Math.sin(Math.PI * outward) + Math.sin(Math.PI * returning);
  const stride = Math.sin(u * tau * 3) * (clock < 5.55 ? 1 : -1);
  worker.position.set(p.x, 0.016 + 0.044 * Math.abs(stride) * travel, p.z);
  const rackYaw = sign * 1.9,
    terminalYaw = sign * 3.07;
  const walkingYaw = sign * (clock < 5.55 ? 1.36 : -1.62);
  const idleYaw = T.MathUtils.lerp(rackYaw, terminalYaw, u);
  const turn = Math.atan2(
    Math.sin(walkingYaw - idleYaw),
    Math.cos(walkingYaw - idleYaw),
  );
  worker.rotation.y = idleYaw + turn * travel;
  const atRack = ease(clock, 0.05, 0.42) * (1 - ease(clock, 0.89, 1.14));
  const typing = ease(clock, 3.28, 3.68) * (1 - ease(clock, 5.14, 5.55));
  worker.rotation.x = 0.092 * typing;
  for (const { shoulder, hip, side } of limbs) {
    hip.rotation.x = side * stride * travel * 0.67;
    shoulder.rotation.x =
      -side * stride * travel * 0.55 -
      atRack * (side === 1 ? 1.28 : 0.4) -
      typing * (1.09 + 0.25 * Math.sin(clock * tau * 2 + side * 1.6));
    shoulder.rotation.z = side * (0.13 + 0.065 * typing);
  }
  carried.visible = clock >= 0.82 && clock < 3.55;
  drawer.position.z = 0.25 + 0.18 * atRack;
  reader.material = clock >= 3.55 && clock < 6.0 ? jobAmber : night;
  const done = ease(clock, 3.55, 5.14) * (1 - ease(clock, 7.38, 7.94));
  progress.scale.x = 0.72 * Math.max(0.001, done);
  progress.position.x = -0.36 + progress.scale.x * 0.5;
  const complete = clock >= 5.14 && clock < 7.38;
  const result = cell.trace.reachable ? jobGreen : jobAmber;
  progress.material = result;
  lamp.material = complete
    ? result
    : clock >= 3.55 && clock < 5.14
      ? cyan
      : armor;
  const checked = Math.floor(ease(clock, 3.55, 5.14) * cell.trace.order.length);
  for (const [i, port] of cell.ports.entries()) {
    const visit = cell.trace.order.indexOf(i);
    port.material =
      clock >= 3.55 && clock < 7.38 && visit >= 0 && visit < checked
        ? cyan
        : armor;
    if (i === 3 && complete) port.material = result;
  }
  dispatch.visible = clock < 0.76;
  if (dispatch.visible) {
    const u = clock / 0.76;
    dispatch.position.copy(uplink.curve.getPointAt(u));
    dispatch.quaternion.setFromUnitVectors(
      forward,
      uplink.curve.getTangentAt(u),
    );
    dispatch.scale.setScalar(uplink.radiusAt(u) * 1.035);
  }
}

function draw(seconds) {
  const t = (seconds * tau) / 8;
  head.position.y = headHeight + 0.063 * Math.sin(t);
  head.rotation.y = 0.067 * Math.sin(t);
  head.rotation.z = 0.025 * Math.cos(t);
  for (const cell of cells) updateCell(cell, seconds);
  for (const { card, cell } of boardCards) {
    const clock = (seconds + cell.index * 0.97) % 8;
    card.position.x =
      -0.8 +
      0.8 *
        (ease(clock, 1.0, 1.4) +
          ease(clock, 5.1, 5.45) -
          2 * ease(clock, 7.48, 7.97));
  }
  renderer.render(scene, camera);
}
function resize() {
  const c = renderer.domElement;
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(c.clientWidth, c.clientHeight, false);
}
resize();
new ResizeObserver(() => {
  resize();
  draw(0);
}).observe(renderer.domElement);
draw(0);
window.renderFrame = draw;
if (!new URLSearchParams(location.search).has("capture")) {
  const pref = matchMedia("(prefers-reduced-motion: reduce)");
  function play() {
    renderer.setAnimationLoop(
      pref.matches ? null : (ms) => draw((ms / 1000) % 8),
    );
    if (pref.matches) draw(0);
  }
  pref.addEventListener("change", play);
  play();
}
