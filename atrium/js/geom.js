// ATRIUM — procedural geometry. Everything in the house is built from these.
// Vertex layout (14 floats): pos(3) nrm(3) uv(2) obj(1) mat(1) pivot(3) ao(1)
// AO starts at 1.0 and is baked in a CPU pass once the house is assembled.

export const STRIDE = 14;

export class Builder {
  constructor() {
    this.v = [];        // interleaved vertex data
    this.i = [];        // indices
    this.objects = [];  // { id, name, room, pivot, bbox } — one per animated unit
    this._obj = 0;
    this._mat = 0;
    this._pivot = [0, 0, 0];
    this._bbox = null;
  }

  /** Open a new animated object. Everything pushed until endObject() shares its reveal slot. */
  beginObject(name, room, pivot, mat, structural = false) {
    this._obj = this.objects.length;
    this._mat = mat | 0;
    this._pivot = pivot.slice();
    this._bbox = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
    this.objects.push({ id: this._obj, name, room, pivot: pivot.slice(), bbox: this._bbox, structural });
    return this._obj;
  }
  endObject() { return this._obj; }

  mat(m) { this._mat = m | 0; return this; }

  /** Append a Geo, transformed by a 4x4 matrix (or null for identity). */
  add(geo, m, matOverride) {
    const mat = matOverride === undefined ? this._mat : matOverride;
    const base = this.v.length / STRIDE;
    const p = geo.pos, n = geo.nrm, u = geo.uv;
    const bb = this._bbox;
    for (let k = 0; k < p.length; k += 3) {
      let x = p[k], y = p[k + 1], z = p[k + 2];
      let nx = n[k], ny = n[k + 1], nz = n[k + 2];
      if (m) {
        const tx = m[0] * x + m[4] * y + m[8] * z + m[12];
        const ty = m[1] * x + m[5] * y + m[9] * z + m[13];
        const tz = m[2] * x + m[6] * y + m[10] * z + m[14];
        x = tx; y = ty; z = tz;
        const ax = m[0] * nx + m[4] * ny + m[8] * nz;
        const ay = m[1] * nx + m[5] * ny + m[9] * nz;
        const az = m[2] * nx + m[6] * ny + m[10] * nz;
        const l = Math.hypot(ax, ay, az) || 1;
        nx = ax / l; ny = ay / l; nz = az / l;
      }
      if (bb) {
        if (x < bb[0]) bb[0] = x; if (y < bb[1]) bb[1] = y; if (z < bb[2]) bb[2] = z;
        if (x > bb[3]) bb[3] = x; if (y > bb[4]) bb[4] = y; if (z > bb[5]) bb[5] = z;
      }
      const j = (k / 3) * 2;
      this.v.push(x, y, z, nx, ny, nz, u[j], u[j + 1], this._obj, mat,
        this._pivot[0], this._pivot[1], this._pivot[2], 1.0);
    }
    for (let k = 0; k < geo.idx.length; k++) this.i.push(base + geo.idx[k]);
    return this;
  }

  build() {
    return {
      vertices: new Float32Array(this.v),
      indices: (this.v.length / STRIDE > 65535) ? new Uint32Array(this.i) : new Uint32Array(this.i),
      objects: this.objects,
      count: this.i.length,
    };
  }
}

const G = (pos, nrm, uv, idx) => ({ pos, nrm, uv, idx });

/* ------------------------------------------------------------------ box */
export function box(w, h, d, uvScale = 1) {
  const x = w / 2, y = h / 2, z = d / 2;
  const pos = [], nrm = [], uv = [], idx = [];
  const faces = [
    { n: [0, 0, 1],  c: [[-x,-y, z],[ x,-y, z],[ x, y, z],[-x, y, z]], s: [w, h] },
    { n: [0, 0,-1],  c: [[ x,-y,-z],[-x,-y,-z],[-x, y,-z],[ x, y,-z]], s: [w, h] },
    { n: [1, 0, 0],  c: [[ x,-y, z],[ x,-y,-z],[ x, y,-z],[ x, y, z]], s: [d, h] },
    { n: [-1,0, 0],  c: [[-x,-y,-z],[-x,-y, z],[-x, y, z],[-x, y,-z]], s: [d, h] },
    { n: [0, 1, 0],  c: [[-x, y, z],[ x, y, z],[ x, y,-z],[-x, y,-z]], s: [w, d] },
    { n: [0,-1, 0],  c: [[-x,-y,-z],[ x,-y,-z],[ x,-y, z],[-x,-y, z]], s: [w, d] },
  ];
  for (const f of faces) {
    const b = pos.length / 3;
    const uvs = [[0, 0], [f.s[0], 0], [f.s[0], f.s[1]], [0, f.s[1]]];
    for (let k = 0; k < 4; k++) {
      pos.push(...f.c[k]); nrm.push(...f.n);
      uv.push(uvs[k][0] * uvScale, uvs[k][1] * uvScale);
    }
    idx.push(b, b + 1, b + 2, b, b + 2, b + 3);
  }
  return G(pos, nrm, uv, idx);
}

/* --------------------------------------------------- rounded (chamfered) box */
export function roundedBox(w, h, d, r, seg = 3, uvScale = 1) {
  r = Math.min(r, w / 2 - 1e-3, h / 2 - 1e-3, d / 2 - 1e-3);
  if (r <= 0.001) return box(w, h, d, uvScale);
  const ix = w / 2 - r, iy = h / 2 - r, iz = d / 2 - r;
  const n = seg + 1;
  const pos = [], nrm = [], uv = [], idx = [];
  const dirs = [
    { u: [1,0,0], v: [0,1,0], w: [0,0,1] }, { u: [-1,0,0], v: [0,1,0], w: [0,0,-1] },
    { u: [0,0,-1], v: [0,1,0], w: [1,0,0] }, { u: [0,0,1], v: [0,1,0], w: [-1,0,0] },
    { u: [1,0,0], v: [0,0,-1], w: [0,1,0] }, { u: [1,0,0], v: [0,0,1], w: [0,-1,0] },
  ];
  for (const f of dirs) {
    const base = pos.length / 3;
    for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) {
      const s = (a / seg) * 2 - 1, t = (b / seg) * 2 - 1;
      // point on the surface of the outer box
      const px = f.u[0] * s + f.v[0] * t + f.w[0];
      const py = f.u[1] * s + f.v[1] * t + f.w[1];
      const pz = f.u[2] * s + f.v[2] * t + f.w[2];
      const qx = px * (w / 2), qy = py * (h / 2), qz = pz * (d / 2);
      // clamp to the inner box, then push out by r → exact rounded-box surface
      const cx = Math.max(-ix, Math.min(ix, qx));
      const cy = Math.max(-iy, Math.min(iy, qy));
      const cz = Math.max(-iz, Math.min(iz, qz));
      let dx = qx - cx, dy = qy - cy, dz = qz - cz;
      const l = Math.hypot(dx, dy, dz) || 1;
      dx /= l; dy /= l; dz /= l;
      pos.push(cx + dx * r, cy + dy * r, cz + dz * r);
      nrm.push(dx, dy, dz);
      uv.push((a / seg) * uvScale * w, (b / seg) * uvScale * h);
    }
    for (let a = 0; a < seg; a++) for (let b = 0; b < seg; b++) {
      const i0 = base + a * n + b, i1 = i0 + 1, i2 = i0 + n, i3 = i2 + 1;
      idx.push(i0, i2, i1, i1, i2, i3);
    }
  }
  return G(pos, nrm, uv, idx);
}

/* ------------------------------------------------------------- cylinder */
export function cylinder(rTop, rBot, h, seg = 20, caps = true, uvScale = 1) {
  const pos = [], nrm = [], uv = [], idx = [];
  const slope = Math.atan2(rBot - rTop, h);
  const cs = Math.cos(slope), sn = Math.sin(slope);
  for (let s = 0; s <= seg; s++) {
    const a = (s / seg) * Math.PI * 2, c = Math.cos(a), si = Math.sin(a);
    for (let y = 0; y < 2; y++) {
      const r = y ? rTop : rBot;
      pos.push(c * r, y ? h / 2 : -h / 2, si * r);
      nrm.push(c * cs, sn, si * cs);
      uv.push((s / seg) * uvScale * Math.PI * 2 * Math.max(rTop, rBot), y * h * uvScale);
    }
  }
  for (let s = 0; s < seg; s++) {
    const i0 = s * 2, i1 = i0 + 1, i2 = i0 + 2, i3 = i0 + 3;
    idx.push(i0, i2, i1, i1, i2, i3);
  }
  if (caps) {
    for (let y = 0; y < 2; y++) {
      const r = y ? rTop : rBot;
      if (r <= 1e-5) continue;
      const cy = y ? h / 2 : -h / 2, ny = y ? 1 : -1, base = pos.length / 3;
      pos.push(0, cy, 0); nrm.push(0, ny, 0); uv.push(0, 0);
      for (let s = 0; s <= seg; s++) {
        const a = (s / seg) * Math.PI * 2;
        pos.push(Math.cos(a) * r, cy, Math.sin(a) * r);
        nrm.push(0, ny, 0);
        uv.push(Math.cos(a) * r * uvScale, Math.sin(a) * r * uvScale);
      }
      for (let s = 0; s < seg; s++) {
        if (y) idx.push(base, base + 1 + s, base + 2 + s);
        else   idx.push(base, base + 2 + s, base + 1 + s);
      }
    }
  }
  return G(pos, nrm, uv, idx);
}

/* --------------------------------------------------------------- sphere */
export function sphere(r, seg = 18, rings = 12, squashY = 1) {
  const pos = [], nrm = [], uv = [], idx = [];
  for (let y = 0; y <= rings; y++) {
    const phi = (y / rings) * Math.PI;
    for (let s = 0; s <= seg; s++) {
      const th = (s / seg) * Math.PI * 2;
      const nx = Math.sin(phi) * Math.cos(th), ny = Math.cos(phi), nz = Math.sin(phi) * Math.sin(th);
      pos.push(nx * r, ny * r * squashY, nz * r);
      const l = Math.hypot(nx, ny / squashY, nz) || 1;
      nrm.push(nx / l, (ny / squashY) / l, nz / l);
      uv.push((s / seg) * r * 6, (y / rings) * r * 3);
    }
  }
  for (let y = 0; y < rings; y++) for (let s = 0; s < seg; s++) {
    const i0 = y * (seg + 1) + s, i1 = i0 + 1, i2 = i0 + seg + 1, i3 = i2 + 1;
    idx.push(i0, i2, i1, i1, i2, i3);
  }
  return G(pos, nrm, uv, idx);
}

/* ----------------------------------------------------------------- torus */
export function torus(R, r, segMaj = 24, segMin = 10, arc = Math.PI * 2) {
  const pos = [], nrm = [], uv = [], idx = [];
  for (let i = 0; i <= segMaj; i++) {
    const u = (i / segMaj) * arc, cu = Math.cos(u), su = Math.sin(u);
    for (let j = 0; j <= segMin; j++) {
      const v = (j / segMin) * Math.PI * 2, cv = Math.cos(v), sv = Math.sin(v);
      pos.push((R + r * cv) * cu, r * sv, (R + r * cv) * su);
      nrm.push(cv * cu, sv, cv * su);
      uv.push(u * R, v * r);
    }
  }
  for (let i = 0; i < segMaj; i++) for (let j = 0; j < segMin; j++) {
    const a = i * (segMin + 1) + j, b = a + segMin + 1;
    idx.push(a, b, a + 1, a + 1, b, b + 1);
  }
  return G(pos, nrm, uv, idx);
}

/* ------------------------------------------------------------------ lathe
   profile: [[radius, y], ...] bottom → top. Normals from the profile tangent. */
export function lathe(profile, seg = 24, uvScale = 1) {
  const pos = [], nrm = [], uv = [], idx = [];
  const P = profile.length;
  const pn = [];
  for (let k = 0; k < P; k++) {
    const a = profile[Math.max(0, k - 1)], b = profile[Math.min(P - 1, k + 1)];
    const dr = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dr, dy) || 1;
    pn.push([dy / l, -dr / l]);
  }
  for (let s = 0; s <= seg; s++) {
    const a = (s / seg) * Math.PI * 2, c = Math.cos(a), si = Math.sin(a);
    for (let k = 0; k < P; k++) {
      pos.push(c * profile[k][0], profile[k][1], si * profile[k][0]);
      nrm.push(c * pn[k][0], pn[k][1], si * pn[k][0]);
      uv.push((s / seg) * 6 * uvScale, profile[k][1] * uvScale);
    }
  }
  for (let s = 0; s < seg; s++) for (let k = 0; k < P - 1; k++) {
    const i0 = s * P + k, i1 = i0 + 1, i2 = i0 + P, i3 = i2 + 1;
    idx.push(i0, i2, i1, i1, i2, i3);
  }
  return G(pos, nrm, uv, idx);
}

/* ------------------------------------------------------------------ plane */
export function plane(w, d, sw = 1, sd = 1, uvScale = 1) {
  const pos = [], nrm = [], uv = [], idx = [];
  for (let z = 0; z <= sd; z++) for (let x = 0; x <= sw; x++) {
    pos.push((x / sw - 0.5) * w, 0, (z / sd - 0.5) * d);
    nrm.push(0, 1, 0);
    uv.push((x / sw) * w * uvScale, (z / sd) * d * uvScale);
  }
  for (let z = 0; z < sd; z++) for (let x = 0; x < sw; x++) {
    const i0 = z * (sw + 1) + x, i1 = i0 + 1, i2 = i0 + sw + 1, i3 = i2 + 1;
    idx.push(i0, i2, i1, i1, i2, i3);
  }
  return G(pos, nrm, uv, idx);
}

/* ------------------------------------------------------------------ AO bake
   Cheap but convincing ambient occlusion, computed once on the CPU and stored
   per vertex. Two contributions:
     1. the room box  — darkens where a surface approaches a wall/floor/ceiling
     2. object spheres — darkens under and behind furniture (contact shadows)
   No rays, no extra render passes, deterministic. */
export function bakeAO(vertices, objects, rooms, opts = {}) {
  const wallR = opts.wallRadius || 3.0;
  const objR = opts.objRadius || 6.0;
  const floorBoost = opts.floorBoost || 1.25;
  const minAO = opts.minAO !== undefined ? opts.minAO : 0.22;

  // sphere proxies for non-structural objects
  const sp = [];
  for (const o of objects) {
    if (o.structural) continue;
    const b = o.bbox;
    if (!b || !isFinite(b[0])) continue;
    const cx = (b[0] + b[3]) / 2, cy = (b[1] + b[4]) / 2, cz = (b[2] + b[5]) / 2;
    const rx = (b[3] - b[0]) / 2, ry = (b[4] - b[1]) / 2, rz = (b[5] - b[2]) / 2;
    const r = Math.cbrt(Math.max(rx, 0.05) * Math.max(ry, 0.05) * Math.max(rz, 0.05)) * 1.15;
    sp.push({ id: o.id, cx, cy, cz, r });
  }

  const n = vertices.length / STRIDE;
  for (let i = 0; i < n; i++) {
    const k = i * STRIDE;
    const px = vertices[k], py = vertices[k + 1], pz = vertices[k + 2];
    const nx = vertices[k + 3], ny = vertices[k + 4], nz = vertices[k + 5];
    const myObj = vertices[k + 8];
    let occ = 0;

    // --- room box term
    let room = null;
    for (const r of rooms) {
      if (px >= r.x0 - 0.6 && px <= r.x1 + 0.6 && pz >= r.z0 - 0.6 && pz <= r.z1 + 0.6) { room = r; break; }
    }
    if (room) {
      const planes = [
        [px - room.x0, 1, 0, 0], [room.x1 - px, -1, 0, 0],
        [pz - room.z0, 0, 0, 1], [room.z1 - pz, 0, 0, -1],
        [py - room.y0, 0, 1, 0], [room.y1 - py, 0, -1, 0],
      ];
      for (let q = 0; q < planes.length; q++) {
        const pl = planes[q];
        const d = pl[0];
        if (d < -0.2 || d > wallR) continue;
        const align = nx * pl[1] + ny * pl[2] + nz * pl[3];   // 1 = facing away from plane
        const t = 1 - Math.min(1, Math.max(0, d) / wallR);
        const f = 0.5 * (1 - align) * t * t;
        occ += f * (q === 4 ? floorBoost : 1.0) * 0.55;
      }
    }

    // --- object proxies
    for (let s = 0; s < sp.length; s++) {
      const o = sp[s];
      if (o.id === myObj) continue;
      const vx = o.cx - px, vy = o.cy - py, vz = o.cz - pz;
      const d2 = vx * vx + vy * vy + vz * vz;
      if (d2 > objR * objR) continue;
      const d = Math.sqrt(d2) || 1e-4;
      const cosw = (nx * vx + ny * vy + nz * vz) / d;
      if (cosw <= 0.02) continue;
      const rr = o.r / Math.max(d, o.r * 0.9);
      occ += cosw * rr * rr * 0.42;
    }

    vertices[k + 13] = Math.max(minAO, 1 - Math.min(1, occ));
  }
  return vertices;
}

/* Merge several Geos into one (already in local space). */
export function mergeGeo(list) {
  const pos = [], nrm = [], uv = [], idx = [];
  for (const g of list) {
    const b = pos.length / 3;
    pos.push(...g.pos); nrm.push(...g.nrm); uv.push(...g.uv);
    for (const k of g.idx) idx.push(b + k);
  }
  return G(pos, nrm, uv, idx);
}

/* Translate/rotate a Geo in place (cheap local transform without a matrix). */
export function xform(g, tx, ty, tz, ry = 0, sx = 1, sy = 1, sz = 1) {
  const c = Math.cos(ry), s = Math.sin(ry);
  for (let k = 0; k < g.pos.length; k += 3) {
    let x = g.pos[k] * sx, y = g.pos[k + 1] * sy, z = g.pos[k + 2] * sz;
    const rx = c * x + s * z, rz = -s * x + c * z;
    g.pos[k] = rx + tx; g.pos[k + 1] = y + ty; g.pos[k + 2] = rz + tz;
    let nx = g.nrm[k] / sx, ny = g.nrm[k + 1] / sy, nz = g.nrm[k + 2] / sz;
    const ax = c * nx + s * nz, az = -s * nx + c * nz;
    const l = Math.hypot(ax, ny, az) || 1;
    g.nrm[k] = ax / l; g.nrm[k + 1] = ny / l; g.nrm[k + 2] = az / l;
  }
  return g;
}
