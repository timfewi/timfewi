import * as T from "three";

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
const blue = new T.MeshPhysicalMaterial({
  color: 0x1752cc,
  metalness: 0.5,
  roughness: 0.24,
  clearcoat: 0.78,
  clearcoatRoughness: 0.22,
});
const ice = metal(0x45aeef, 0.38, 0.25),
  cyan = flat(0x80e6ff),
  gold = metal(0xca8430, 0.66, 0.26);
const lightGold = flat(0xffcf78),
  darkGlass = metal(0x172039, 0.65, 0.19);
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
const slab = group(scene);
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
const halo = group(scene, 0, 4.02, -1.25);
halo.quaternion.copy(camera.quaternion);
const haloMat = new T.MeshBasicMaterial({
  color: 0x527bbe,
  transparent: true,
  opacity: 0.38,
});
for (const r of [2.04, 2.32]) hoop(halo, 0, 0, 0, r, 0.008, haloMat);
for (let i = 0; i < 60; i++) {
  const a = (tau * i) / 60,
    r = i % 5 === 0 ? 2.13 : 2.22;
  line(
    halo,
    [
      [r * Math.cos(a), r * Math.sin(a), 0],
      [2.29 * Math.cos(a), 2.29 * Math.sin(a), 0],
    ],
    0x4673ae,
    0.58,
  );
}

// Build a solid relief from the actual transparent brand mark. The sampled silhouette
// defines both faces and the edge walls, including the gaps between the crystal forks.
const mark = await new T.TextureLoader().loadAsync("/mark.webp");
mark.colorSpace = T.SRGBColorSpace;
function crystalRelief(tex) {
  const size = 130,
    stride = size + 1;
  const c = document.createElement("canvas");
  c.width = c.height = stride;
  const ctx = c.getContext("2d");
  ctx.drawImage(tex.image, 0, 0, stride, stride);
  const pixels = ctx.getImageData(0, 0, stride, stride).data;
  const positions = [],
    uv = [],
    faces = [],
    sides = [],
    boundary = [];
  const alpha = (i) => pixels[4 * i + 3],
    threshold = 125;
  const vertices = new Map();
  function vertex(a, b = a) {
    const key = Math.min(a, b) * stride * stride + Math.max(a, b);
    if (vertices.has(key)) return vertices.get(key);
    const t = a === b ? 0 : (threshold - alpha(a)) / (alpha(b) - alpha(a));
    const u = ((a % stride) * (1 - t) + (b % stride) * t) / size;
    const v =
      (Math.floor(a / stride) * (1 - t) + Math.floor(b / stride) * t) / size;
    const dome = Math.max(
      0,
      1 - ((u - 0.5) * 1.8) ** 2 - ((v - 0.62) * 1.5) ** 2,
    );
    const i = positions.length / 3;
    positions.push((u - 0.5) * 4.9, (0.5 - v) * 4.9, 0.04 + 0.3 * dome);
    uv.push(u, 1 - v);
    vertices.set(key, i);
    return i;
  }
  function triangle(a, b, c) {
    const clipped = [],
      crossings = [];
    for (const [i, j] of [
      [a, b],
      [b, c],
      [c, a],
    ]) {
      if (alpha(i) >= threshold) clipped.push(vertex(i));
      if (alpha(i) >= threshold !== alpha(j) >= threshold) {
        const cut = vertex(i, j);
        clipped.push(cut);
        crossings.push(cut);
      }
    }
    for (let k = 1; k + 1 < clipped.length; k++)
      faces.push(clipped[0], clipped[k], clipped[k + 1]);
    if (crossings.length === 2) boundary.push(crossings);
  }
  for (let y = 0; y < size; y++)
    for (let x = 0; x < size; x++) {
      const a = y * stride + x,
        b = a + 1,
        c = a + stride,
        d = c + 1;
      triangle(a, c, b);
      triangle(b, c, d);
    }
  const backOffset = positions.length / 3;
  for (let i = 0; i < backOffset; i++) {
    positions.push(
      positions[3 * i],
      positions[3 * i + 1],
      positions[3 * i + 2] - 0.15,
    );
    uv.push(uv[2 * i], uv[2 * i + 1]);
  }
  for (let i = 0; i < faces.length; i += 3) {
    sides.push(
      backOffset + faces[i],
      backOffset + faces[i + 2],
      backOffset + faces[i + 1],
    );
  }
  // Separate wall normals keep the crystal face smooth right out to its silhouette.
  for (const [i, j] of boundary) {
    const start = positions.length / 3;
    for (const [idx, dz] of [
      [i, 0],
      [j, 0],
      [j, -0.15],
      [i, -0.15],
    ]) {
      positions.push(
        positions[idx * 3],
        positions[idx * 3 + 1],
        positions[idx * 3 + 2] + dz,
      );
      uv.push(uv[2 * idx], uv[2 * idx + 1]);
    }
    sides.push(start, start + 1, start + 2, start, start + 2, start + 3);
  }
  const geo = new T.BufferGeometry();
  geo.setAttribute("position", new T.Float32BufferAttribute(positions, 3));
  geo.setAttribute("uv", new T.Float32BufferAttribute(uv, 2));
  geo.setIndex([...faces, ...sides]);
  geo.addGroup(0, faces.length, 0);
  geo.addGroup(faces.length, sides.length, 1);
  geo.computeVertexNormals();
  const facet = new T.MeshStandardMaterial({
    map: tex,
    emissiveMap: tex,
    emissive: 0xffffff,
    emissiveIntensity: 0.46,
    metalness: 0.2,
    roughness: 0.48,
  });
  const edge = metal(0x10458e, 0.4, 0.36);
  edge.side = T.DoubleSide;
  return mesh(scene, geo, [facet, edge]);
}
const head = crystalRelief(mark);
head.position.set(0, 3.61, -0.12);
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
mesh(head, maskGeo, shell);
const mantleGeo = new T.LatheGeometry(
  [
    [0.1, 0],
    [0.33, 0.2],
    [0.5, 0.62],
    [0.73, 1.2],
    [0.83, 1.8],
    [0.66, 2.18],
    [0.1, 2.35],
  ].map(([r, y]) => new T.Vector2(r, y)),
  48,
);
const mantle = mesh(scene, mantleGeo, blue, 0, 0.13, -0.2);
mantle.scale.z = 0.78;

// Closed, tapered tubes follow a spatial spline. Every ring moves as a unit,
// with zero deflection at the root and dock so the attachment points stay seated.
const arms = [];
const skin = blue.clone();
skin.vertexColors = true;
skin.roughness = 0.3;
skin.clearcoat = 0.62;
function arm(points, start, end, phase, swing, suckers = false) {
  const curve = new T.CatmullRomCurve3(points.map((p) => vec(...p)));
  const rings = swing > 0.2 ? 140 : 72,
    sides = 18,
    frames = curve.computeFrenetFrames(rings, false);
  const positions = [],
    indices = [],
    colors = [],
    weights = [],
    cups = [];
  for (let i = 0; i <= rings; i++) {
    const u = i / rings,
      p = curve.getPointAt(u),
      radius = end + (start - end) * (1 - u) ** 0.77;
    for (let j = 0; j < sides; j++) {
      const a = (tau * j) / sides;
      const flute =
        1 +
        0.084 * Math.cos(a * 3 + u * 9 + phase) +
        0.037 * Math.sin(a * 5 - u * 6);
      const normal = frames.normals[i]
        .clone()
        .multiplyScalar(Math.cos(a))
        .addScaledVector(frames.binormals[i], Math.sin(a));
      const shade = 0.6 + 0.37 * (0.5 + 0.5 * normal.y);
      colors.push(shade * 0.9, shade, 0.82 + 0.18 * shade);
      const q = p
        .clone()
        .addScaledVector(frames.normals[i], radius * flute * Math.cos(a))
        .addScaledVector(
          frames.binormals[i],
          radius * flute * 0.88 * Math.sin(a),
        );
      positions.push(q.x, q.y, q.z);
      if (i < rings) {
        const a = i * sides + j,
          b = i * sides + ((j + 1) % sides);
        indices.push(a, b, a + sides, b, b + sides, a + sides);
      }
    }
    weights.push(swing * Math.sin(Math.PI * u) ** 1.5);
    if (suckers && i % 3 === 0 && u > 0.42 && u < 0.84) {
      // Two rows on the forward-facing skin, kept on their own moving ring.
      const tangent = curve.getTangentAt(u);
      const front = vec(0, 0.15, 1);
      front.addScaledVector(tangent, -front.dot(tangent)).normalize();
      const side = tangent.clone().cross(front);
      for (const offset of [-0.35, 0.35]) {
        const n = front.clone().addScaledVector(side, offset).normalize();
        const at = p.clone().addScaledVector(n, radius * 0.9);
        const cup = hoop(
          scene,
          at.x,
          at.y,
          at.z,
          radius * 0.2,
          radius * 0.049,
          ice,
        );
        cup.quaternion.setFromUnitVectors(vec(0, 0, 1), n);
        cups.push({ mesh: cup, i, at });
      }
    }
  }
  const geo = new T.BufferGeometry();
  geo.setIndex(indices);
  const attr = new T.Float32BufferAttribute(positions, 3);
  attr.setUsage(T.DynamicDrawUsage);
  geo.setAttribute("position", attr);
  geo.setAttribute("color", new T.Float32BufferAttribute(colors, 3));
  geo.computeVertexNormals();
  mesh(scene, geo, skin).castShadow = true;
  arms.push({
    attr,
    base: Float32Array.from(positions),
    weights,
    phase,
    sides,
    cups,
  });
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
const routeDots = [],
  packets = [],
  wrists = [];
function networkPanel(parent, sign) {
  const panel = group(parent, sign * 0.68, 0.83, -0.16);
  panel.rotation.y = sign * -0.33;
  box(panel, 0, 0, 0, 0.76, 0.47, 0.034, metal(0x112945, 0.42, 0.22));
  line(
    panel,
    [
      [-0.38, -0.235, 0.023],
      [0.38, -0.235, 0.023],
      [0.38, 0.235, 0.023],
      [-0.38, 0.235, 0.023],
      [-0.38, -0.235, 0.023],
    ],
    0x649ddd,
  );
  box(panel, 0, -0.42, 0, 0.026, 0.34, 0.027, steel);
  const pts = [
    [-0.27, 0.04],
    [-0.12, 0],
    [0.015, 0.065],
    [0.14, 0.15],
    [0.23, -0.04],
  ];
  for (const [a, b] of [
    [0, 1],
    [1, 2],
    [2, 3],
    [2, 4],
  ])
    line(
      panel,
      [
        [...pts[a], 0.032],
        [...pts[b], 0.032],
      ],
      0x72acd6,
    );
  pts.forEach(([x, y], i) =>
    oval(
      panel,
      x,
      y,
      0.038,
      0.029,
      0.029,
      0.016,
      flat([0xcfd9ed, 0x5ba6ff, 0xffad54, 0x65ddab, 0x65ddab][i]),
    ),
  );
  packets.push(oval(panel, 0, 0, 0.064, 0.027, 0.027, 0.014, cyan));
  routeDots.push(
    oval(panel, 0.23, -0.04, 0.052, 0.034, 0.034, 0.014, lightGold),
  );
}
for (let i = 0; i < spots.length; i++) {
  const [x, z] = spots[i],
    s = Math.sign(x),
    row = Math.floor(i / 2);
  const station = group(scene, x, 0.04, z);
  disc(station, 0, 0.029, 0, 0.61, 0.056, night).receiveShadow = true;
  hoop(station, 0, 0.061, 0, 0.55, 0.012, steel).rotation.x = Math.PI / 2;
  const g = group(station, 0, 0.08, 0);
  g.rotation.y = s * -0.18;
  for (const side of [-1, 1]) {
    box(g, side * 0.105, 0.06, 0.035, 0.138, 0.12, 0.195, graphite);
    box(g, side * 0.105, 0.23, 0, 0.116, 0.31, 0.13, armor);
    const shoulder = group(g, side * 0.222, 0.7, 0);
    oval(shoulder, 0, -0.12, 0, 0.08, 0.19, 0.085, armor);
    oval(shoulder, side * 0.028, -0.26, 0.02, 0.057, 0.082, 0.062, graphite);
    shoulder.rotation.z = side * 0.16;
    wrists.push({ shoulder, side, i });
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
  box(g, 0, 0.61, 0.164, 0.081, 0.029, 0.022, cyan);
  oval(g, 0, 0.85, 0, 0.188, 0.176, 0.15, graphite);
  box(g, 0, 0.863, 0.126, 0.24, 0.063, 0.05, night);
  box(g, 0, 0.87, 0.155, 0.183, 0.028, 0.012, cyan);
  disc(g, 0, 1.055, 0, 0.111, 0.048, steel);
  hoop(g, 0, 1.084, 0, 0.076, 0.013, cyan).rotation.x = Math.PI / 2;
  g.traverse((o) => {
    if (o.isMesh) o.castShadow = true;
  });
  networkPanel(station, s);
  const y = 1.205;
  const paths = [
    [
      [s * 0.48, 2.35, -0.62],
      [s * 1.12, 1.95, -1.32],
      [x * 0.89, 2.15, z - 0.22],
      [x, y, z],
    ],
    [
      [s * 0.51, 2.4, -0.19],
      [s * 1.64, 1.65, -0.1],
      [s * 2.85, 2.16, -0.55],
      [s * 3.48, 1.96, -0.47],
      [x, y, z],
    ],
    [
      [s * 0.46, 2.18, 0.07],
      [s * 1.14, 1.28, 0.56],
      [s * 2.21, 1.61, 1.12],
      [s * 2.67, 1.65, 1.43],
      [x, y, z],
    ],
    [
      [s * 0.34, 2.02, 0.25],
      [s * 0.72, 1.07, 1.19],
      [s * 1.58, 1.47, 2.1],
      [s * 1.55, 1.36, 2.67],
      [s * 1.14, 1.42, 3.32],
      [x, y, z],
    ],
  ];
  arm(paths[row], 0.38, 0.041, i * 0.84, 0.135, row >= 2);
}
for (const s of [-1, 1]) {
  arm(
    [
      [s * 0.33, -0.84, 0.13],
      [s * 2.15, -1.26, 2.72],
      [s * 4.4, -0.88, 3.2],
      [s * 5.72, -0.05, 2.12],
      [s * 6.05, 1.12, 0.54],
      [s * 5.62, 1.88, -0.26],
      [s * 5.47, 2.31, -0.36],
      [s * 5.76, 2.54, -0.42],
      [s * 6.06, 2.42, -0.4],
      [s * 6.04, 2.19, -0.38],
      [s * 5.91, 2.2, -0.36],
    ],
    0.69,
    0.008,
    s * 0.8,
    0.25,
  );
}
arm(
  [
    [0, -0.39, 0.1],
    [-0.58, -1.05, 1.8],
    [-0.22, -1.44, 3.15],
    [0.53, -1.66, 3.84],
    [0.27, -1.94, 4.72],
    [-0.29, -1.85, 4.94],
  ],
  0.57,
  0.012,
  0.8,
  0.14,
);
// A pair of fine curled feelers frames the face above the load-bearing arms.
for (const s of [-1, 1]) {
  arm(
    [
      [s * 0.43, 2.38, -0.1],
      [s * 1.05, 2.12, 0.08],
      [s * 1.62, 2.48, 0.05],
      [s * 1.82, 2.96, -0.04],
      [s * 1.62, 3.22, -0.06],
      [s * 1.37, 3.14, -0.03],
      [s * 1.37, 2.94, 0.03],
      [s * 1.5, 2.94, 0.04],
      [s * 1.49, 3.02, 0.06],
    ],
    0.205,
    0.009,
    s * 0.93,
    0.095,
  );
}
const eyePos = [4.18, 4.3, -0.48];
arm(
  [
    [0.55, 2.48, -0.29],
    [1.48, 3.02, -0.81],
    [2.54, 3.62, -0.83],
    [3.62, 3.36, -0.68],
    [4.11, 3.68, -0.52],
    eyePos,
  ],
  0.213,
  0.055,
  4,
  0.1,
);
aura(scene, 0xb07e30, 0.95, [eyePos[0], eyePos[1], eyePos[2] - 0.38]);
const eye = group(scene, ...eyePos);
eye.quaternion.copy(camera.quaternion);
oval(eye, 0, 0, 0, 0.42, 0.42, 0.4, darkGlass);
const gaze = group(eye);
oval(gaze, 0, 0, 0.35, 0.19, 0.203, 0.076, gold);
oval(gaze, 0, 0, 0.415, 0.128, 0.151, 0.045, lightGold);
oval(gaze, 0, 0, 0.456, 0.034, 0.11, 0.012, flat(0x211933));
oval(gaze, -0.057, 0.066, 0.461, 0.023, 0.023, 0.012, flat(0xfff2cd));
const orbit = hoop(eye, 0, 0, 0, 0.58, 0.012, gold);
orbit.rotation.x = 1.19;
orbit.rotation.z = 0.34;
const beam = line(scene, [eyePos, [0, 0, 0]], 0xffca70, 0.2);

function draw(seconds) {
  const t = (seconds * tau) / 8;
  head.position.y = 3.61 + 0.063 * Math.sin(t);
  head.rotation.y = 0.067 * Math.sin(t);
  head.rotation.z = 0.025 * Math.cos(t);
  mantle.scale.x = 1 + 0.028 * Math.sin(t);
  halo.rotation.z = 0.032 * Math.sin(t);
  orbit.rotation.y = 0.45 * Math.sin(t);
  orbit.rotation.x = 1.18 + 0.12 * Math.cos(t);
  for (const { attr, base, weights, phase, sides, cups } of arms) {
    const shifts = weights.map((w, i) => [
      w * Math.sin(t + phase + i * 0.077),
      w * 0.8 * Math.cos(t + phase + i * 0.105),
    ]);
    for (let i = 0; i < weights.length; i++) {
      const [dx, dy] = shifts[i];
      for (let j = 0; j < sides; j++) {
        const k = (i * sides + j) * 3;
        attr.array[k] = base[k] + dx;
        attr.array[k + 1] = base[k + 1] + dy;
      }
    }
    for (const { mesh, i, at } of cups)
      mesh.position.set(at.x + shifts[i][0], at.y + shifts[i][1], at.z);
    attr.needsUpdate = true;
  }
  const index = Math.floor(seconds) % spots.length,
    pulse = Math.sin(Math.PI * (seconds % 1)) ** 2;
  const [x, z] = spots[index],
    target = x + Math.sign(x) * 0.68;
  // Slew to the next monitor while the old beam is dimming.
  const [nextX, nextZ] = spots[(index + 1) % spots.length];
  const slew = T.MathUtils.smoothstep(seconds % 1, 0.72, 1);
  const lookX = T.MathUtils.lerp(x, nextX, slew),
    lookZ = T.MathUtils.lerp(z, nextZ, slew);
  gaze.rotation.y = (lookX - eyePos[0]) * 0.075;
  gaze.rotation.x = 0.3 - lookZ * 0.035;
  for (const { shoulder, side, i } of wrists) {
    shoulder.rotation.z = side * (0.18 + 0.065 * Math.sin(2 * t + i));
    shoulder.rotation.x = -0.12 - 0.19 * (1 + Math.sin(2 * t + i + side));
  }
  packets.forEach((dot, i) => {
    const u = (seconds / 2 + i * 0.17) % 1;
    const route = [
      [-0.27, 0.04],
      [-0.12, 0],
      [0.015, 0.065],
      i % 2 ? [0.14, 0.15] : [0.23, -0.04],
    ];
    const k = Math.floor(u * 3),
      f = u * 3 - k;
    dot.position.x = T.MathUtils.lerp(route[k][0], route[k + 1][0], f);
    dot.position.y = T.MathUtils.lerp(route[k][1], route[k + 1][1], f);
  });
  beam.geometry.attributes.position.setXYZ(1, target, 0.9, z - 0.16);
  beam.geometry.attributes.position.needsUpdate = true;
  beam.frustumCulled = false;
  beam.material.opacity = pulse * 0.42;
  routeDots.forEach((o, i) => {
    o.visible = i === index && pulse > 0.15;
  });
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
