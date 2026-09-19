// ATRIUM — builds The Ocotillo from engine/plan.json.
// Every wall length, every opening and every room area here is the same number
// the estimate is computed from. There is no second set of dimensions.

import { Builder, box, roundedBox, cylinder, sphere, torus, lathe, plane, bakeAO } from './geom.js';
import { MAT } from './shaders.js';
import { m4, m4trs, m4trs2 } from './math.js';

const T = m4();
const P = (b, geo, x, y, z, ry = 0, sx = 1, sy = 1, sz = 1) => {
  m4trs(T, x, y, z, ry, sx, sy, sz);
  b.add(geo, T);
};
// same, but with a tilt about X first — for anything mounted flat to a wall
const PX = (b, geo, x, y, z, rx, ry = 0, sx = 1, sy = 1, sz = 1) => {
  m4trs2(T, x, y, z, rx, ry, sx, sy, sz);
  b.add(geo, T);
};

const HALF_PI = Math.PI / 2;
// lay a Y-axis primitive down so it points along +X / +Z
const ALONG_Z = [HALF_PI, 0];
const ALONG_X = [HALF_PI, HALF_PI];
const FACE_X = [HALF_PI, HALF_PI];

export function buildHouse(plan) {
  const H = plan.meta.ceiling_height;
  const WT = plan.meta.wall_thickness;
  const FX = plan.meta.footprint.width_x;
  const FZ = plan.meta.footprint.depth_z;
  const b = new Builder();
  const lights = [];
  const rooms = {};
  for (const r of plan.rooms) rooms[r.id] = r;

  /* =============================================== openings, resolved to world */
  // Each plan opening is written relative to its room + wall. Resolve to absolute
  // spans so the wall builder can cut them.
  const cuts = { x: {}, z: {} };   // cuts.x[coord] = [{a,b,sill,h,type}], a/b along z
  const addCut = (axis, coord, a, b2, sill, h, type) => {
    const key = coord.toFixed(3);
    const m = cuts[axis];
    (m[key] || (m[key] = [])).push({ a, b: b2, sill, h, type });
  };

  const windows = [];
  for (const op of plan.openings) {
    const r = rooms[op.room];
    if (!r) continue;
    let axis, coord, a, b2;
    if (op.wall === 'south')      { axis = 'z'; coord = r.z0; a = r.x0 + op.offset; b2 = a + op.width; }
    else if (op.wall === 'north') { axis = 'z'; coord = r.z1; a = r.x0 + op.offset; b2 = a + op.width; }
    else if (op.wall === 'west')  { axis = 'x'; coord = r.x0; a = r.z0 + op.offset; b2 = a + op.width; }
    else                          { axis = 'x'; coord = r.x1; a = r.z0 + op.offset; b2 = a + op.width; }
    addCut(axis, coord, a, b2, op.sill, op.height, op.type);
    if (op.type === 'window') windows.push({ axis, coord, a, b: b2, sill: op.sill, h: op.height, room: op.room });
    if (op.type === 'door_front') windows.push({ axis, coord, a, b: b2, sill: op.sill, h: op.height, room: op.room, glass: true });
  }

  const cutsFor = (axis, coord, from, to) => {
    const list = cuts[axis][coord.toFixed(3)] || [];
    return list.filter(c => c.b > from + 0.01 && c.a < to - 0.01)
      .map(c => ({ ...c, a: Math.max(c.a, from), b: Math.min(c.b, to) }))
      .sort((p, q) => p.a - q.a);
  };

  /* ==================================================================== WALLS */
  // axis 'x' → wall runs along z at constant x. axis 'z' → runs along x at constant z.
  function wall(name, axis, coord, from, to, matSlot = MAT.WALL, structural = true) {
    if (to - from < 0.02) return;
    const mid = (from + to) / 2;
    const pivot = axis === 'x' ? [coord, 0, mid] : [mid, 0, coord];
    b.beginObject(name, null, pivot, matSlot, structural);

    const segs = cutsFor(axis, coord, from, to);
    const emit = (a, b2, y0, y1) => {
      if (b2 - a < 0.01 || y1 - y0 < 0.01) return;
      const len = b2 - a, hh = y1 - y0, c = (a + b2) / 2, cy = (y0 + y1) / 2;
      const g = axis === 'x' ? box(WT, hh, len, 1) : box(len, hh, WT, 1);
      if (axis === 'x') P(b, g, coord, cy, c);
      else P(b, g, c, cy, coord);
    };

    let cursor = from;
    for (const s of segs) {
      emit(cursor, s.a, 0, H);                       // pier
      if (s.sill > 0.01) emit(s.a, s.b, 0, s.sill);  // under the sill
      const top = s.sill + s.h;
      if (top < H - 0.01) emit(s.a, s.b, top, H);    // header
      cursor = s.b;
    }
    emit(cursor, to, 0, H);

    // baseboard, both faces
    const bh = 0.55, bd = WT / 2 + 0.06;
    const runBase = (a, b2) => {
      if (b2 - a < 0.05) return;
      const len = b2 - a, c = (a + b2) / 2;
      b.mat(MAT.TRIM);
      if (axis === 'x') P(b, box(bd * 2, bh, len), coord, bh / 2, c);
      else P(b, box(len, bh, bd * 2), c, bh / 2, coord);
      b.mat(matSlot);
    };
    let bc = from;
    for (const s of segs) {
      runBase(bc, s.a);
      if (s.sill > 0.55) runBase(s.a, s.b);
      bc = s.b;
    }
    runBase(bc, to);

    b.endObject();
  }

  // exterior shell
  wall('wall.south', 'z', 0, 0, FX);
  wall('wall.north', 'z', FZ, 0, FX);
  wall('wall.west', 'x', 0, 0, FZ);
  wall('wall.east', 'x', FX, 0, FZ);
  // interior partitions
  wall('wall.living_entry', 'x', 18, 0, 20);
  wall('wall.entry_kitchen', 'x', 28, 0, 20);
  wall('wall.mid', 'z', 20, 0, FX);
  wall('wall.bath_closet', 'x', 10, 20, FZ);
  wall('wall.closet_bed', 'x', 20, 20, FZ);

  /* ============================================================ FLOOR + CEILING */
  b.beginObject('floor', null, [FX / 2, 0, FZ / 2], MAT.FLOOR, true);
  P(b, plane(FX + 1.2, FZ + 1.2, 8, 8, 1), FX / 2, 0, FZ / 2);
  b.endObject();

  b.beginObject('ceiling', null, [FX / 2, H, FZ / 2], MAT.CEILING, true);
  const ceil = plane(FX, FZ, 4, 4, 1);
  for (let i = 0; i < ceil.nrm.length; i += 3) ceil.nrm[i + 1] = -1;
  for (let i = 0; i < ceil.idx.length; i += 3) {
    const t = ceil.idx[i]; ceil.idx[i] = ceil.idx[i + 2]; ceil.idx[i + 2] = t;
  }
  P(b, ceil, FX / 2, H, FZ / 2);
  // a shallow beam grid so the ceiling is not a dead plane
  b.mat(MAT.TRIM);
  for (let x = 6; x < FX; x += 6) P(b, box(0.55, 0.45, FZ - 0.4), x, H - 0.22, FZ / 2);
  b.endObject();

  /* ============================================================= WINDOW GLASS */
  b.beginObject('glazing', null, [FX / 2, 4, FZ / 2], MAT.GLASS, true);
  for (const w of windows) {
    const cy = w.sill + w.h / 2, c = (w.a + w.b) / 2, len = w.b - w.a;
    // frame
    b.mat(MAT.TRIM);
    const fr = 0.22;
    if (w.axis === 'x') {
      P(b, box(WT + 0.12, fr, len + fr * 2), w.coord, w.sill - fr / 2, c);
      P(b, box(WT + 0.12, fr, len + fr * 2), w.coord, w.sill + w.h + fr / 2, c);
      P(b, box(WT + 0.12, w.h, fr), w.coord, cy, w.a - fr / 2);
      P(b, box(WT + 0.12, w.h, fr), w.coord, cy, w.b + fr / 2);
      const mull = Math.max(1, Math.round(len / 4));
      for (let i = 1; i < mull; i++) P(b, box(WT + 0.02, w.h, 0.12), w.coord, cy, w.a + (len * i) / mull);
      // no pane: an open reveal reads as glass and lets the sky actually come in
    } else {
      P(b, box(len + fr * 2, fr, WT + 0.12), c, w.sill - fr / 2, w.coord);
      P(b, box(len + fr * 2, fr, WT + 0.12), c, w.sill + w.h + fr / 2, w.coord);
      P(b, box(fr, w.h, WT + 0.12), w.a - fr / 2, cy, w.coord);
      P(b, box(fr, w.h, WT + 0.12), w.b + fr / 2, cy, w.coord);
      const mull = Math.max(1, Math.round(len / 4));
      for (let i = 1; i < mull; i++) P(b, box(0.12, w.h, WT + 0.02), w.a + (len * i) / mull, cy, w.coord);
    }
  }
  b.endObject();

  /* =============================================================== FURNITURE */
  const obj = (name, room, pivot, mat) => b.beginObject(name, room, pivot, mat, false);

  /* ---------- LIVING ---------- */
  // rug
  obj('rug.living', 'living', [8.5, 0, 11], MAT.TEXTILE_B);
  P(b, box(12, 0.07, 9, 1), 8.5, 0.035, 11);
  b.endObject();

  // sofa, against the north partition facing the south window
  obj('sofa', 'living', [8.5, 0, 17.4], MAT.TEXTILE_A);
  sofa(b, 8.5, 17.4, Math.PI, 8.4);
  b.endObject();

  // two lounge chairs facing back
  obj('chair.a', 'living', [4.6, 0, 6.6], MAT.TEXTILE_A);
  loungeChair(b, 4.6, 6.6, -0.35);
  b.endObject();
  obj('chair.b', 'living', [12.4, 0, 6.6], MAT.TEXTILE_A);
  loungeChair(b, 12.4, 6.6, 0.35);
  b.endObject();

  // coffee table
  obj('table.coffee', 'living', [8.5, 0, 12.0], MAT.STONE);
  P(b, roundedBox(4.6, 0.34, 2.4, 0.12, 3), 8.5, 1.28, 12.0);
  b.mat(MAT.WOOD);
  for (const [dx, dz] of [[-1.9, -0.85], [1.9, -0.85], [-1.9, 0.85], [1.9, 0.85]])
    P(b, cylinder(0.09, 0.11, 1.11, 10), 8.5 + dx, 0.555, 12.0 + dz);
  b.mat(MAT.STONE);
  P(b, lathe([[0, 0], [0.36, 0.05], [0.30, 0.5], [0.42, 0.95], [0.30, 1.15], [0.28, 1.2], [0, 1.2]], 20), 7.6, 1.45, 12.0);
  b.mat(MAT.PLANT);
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2 + 0.3;
    const h = 1.1 + (i % 3) * 0.28;
    P(b, cylinder(0.018, 0.028, h, 5), 7.6 + Math.cos(a) * 0.14, 1.95 + h / 2, 12.0 + Math.sin(a) * 0.14);
    for (let k = 0; k < 3; k++) {
      const t = 0.55 + k * 0.2;
      P(b, sphere(0.16, 8, 5, 0.10), 7.6 + Math.cos(a) * (0.14 + t * 0.34), 1.95 + h * t,
        12.0 + Math.sin(a) * (0.14 + t * 0.34), a + k * 0.9, 1, 1, 2.4);
    }
  }
  b.endObject();

  // media console + art, east wall
  obj('console.media', 'living', [17.3, 0, 16.0], MAT.CABINET);
  P(b, roundedBox(1.5, 1.75, 6.5, 0.05, 2), 17.0, 1.28, 16.0);
  b.mat(MAT.DARK);
  P(b, box(1.2, 0.4, 6.1), 17.0, 0.2, 16.0);        // recessed plinth — it floats
  P(b, box(0.12, 3.0, 5.2), 17.4, 4.4, 16.0);       // screen
  b.mat(MAT.METAL);
  for (const dz of [-1.6, 1.6]) PX(b, cylinder(0.04, 0.04, 1.1, 8), 16.24, 1.6, 16.0 + dz, ...ALONG_Z);
  b.endObject();

  obj('art.living', 'living', [17.6, 0, 6.0], MAT.ART);
  artPiece(b, 17.55, 5.4, 6.0, 'x', 4.4, 3.2);
  b.endObject();

  // shelving on the west wall, north end
  obj('shelf.living', 'living', [0.9, 0, 17.6], MAT.WOOD);
  shelfUnit(b, 0.85, 17.6, HALF_PI, 5.0, 8.2);
  b.endObject();

  // floor lamp + plant
  obj('lamp.living', 'living', [2.4, 0, 13.6], MAT.METAL);
  floorLamp(b, 2.4, 13.6);
  b.endObject();
  lights.push({ pos: [2.4, 5.3, 13.6], color: [1, 0.8, 0.55], intensity: 1.0, range: 16, obj: 'lamp.living' });

  obj('plant.living', 'living', [15.6, 0, 18.4], MAT.PLANT);
  bigPlant(b, 15.6, 18.4, 1.0);
  b.endObject();

  /* ---------- ENTRY + HALL ---------- */
  obj('bench.entry', 'entry', [27.2, 0, 2.0], MAT.WOOD);
  P(b, roundedBox(1.3, 0.22, 3.4, 0.06, 2), 27.2, 1.45, 2.0);
  for (const dz of [-1.4, 1.4]) {
    P(b, box(0.16, 1.45, 0.16), 26.75, 0.72, 2.0 + dz);
    P(b, box(0.16, 1.45, 0.16), 27.65, 0.72, 2.0 + dz);
  }
  b.mat(MAT.TEXTILE_A);
  P(b, roundedBox(1.15, 0.2, 3.1, 0.09, 2), 27.2, 1.66, 2.0);
  b.endObject();

  obj('console.entry', 'entry', [18.8, 0, 2.2], MAT.CABINET);
  P(b, roundedBox(1.2, 0.18, 3.6, 0.04, 2), 18.85, 2.5, 2.2);
  b.mat(MAT.METAL);
  for (const dz of [-1.5, 1.5]) {
    P(b, cylinder(0.045, 0.045, 2.42, 8), 18.5, 1.21, 2.2 + dz);
    P(b, cylinder(0.045, 0.045, 2.42, 8), 19.2, 1.21, 2.2 + dz);
  }
  b.mat(MAT.STONE);
  P(b, lathe([[0, 0], [0.22, 0.03], [0.30, 0.35], [0.16, 0.72], [0.19, 0.8], [0, 0.8]], 18), 18.85, 2.59, 1.4);
  b.endObject();

  obj('art.entry', 'entry', [18.35, 0, 3.4], MAT.ART);
  artPiece(b, 18.32, 5.2, 3.4, 'x', 2.2, 2.8);
  b.endObject();

  pendant(b, obj, lights, 'pendant.entry', 'entry', 23.0, 5.0, H, 0.55, 2.6);

  obj('rug.hall', 'hall', [23, 0, 14.5], MAT.TEXTILE_B);
  P(b, box(3.2, 0.05, 9.0, 1), 23, 0.025, 14.5);
  b.endObject();

  for (const [sx, sz, ry] of [[18.42, 12.0, 0], [27.58, 16.0, Math.PI]]) {
    obj(`sconce.hall.${sz}`, 'hall', [sx, 0, sz], MAT.METAL);
    sconce(b, sx, 5.6, sz, ry);
    b.endObject();
    lights.push({ pos: [sx + (ry ? -0.5 : 0.5), 5.7, sz], color: [1, 0.78, 0.5], intensity: 0.55, range: 10 });
  }

  obj('art.hall', 'hall', [27.6, 0, 11.0], MAT.ART);
  artPiece(b, 27.63, 5.3, 11.0, 'x', 2.0, 2.6, true);
  b.endObject();

  /* ---------- KITCHEN ---------- */
  // base run + counter along the south window wall
  obj('kitchen.base_south', 'kitchen', [37, 0, 1.4], MAT.CABINET);
  cabinetRun(b, 29, 45, 1.4, 2.0, 3.0, 0);
  b.mat(MAT.COUNTER);
  P(b, box(16.4, 0.22, 2.2), 37, 3.11, 1.4);
  b.endObject();

  obj('kitchen.sink', 'kitchen', [37, 0, 1.4], MAT.TRIM);
  P(b, roundedBox(2.9, 0.95, 1.85, 0.08, 3), 37, 2.66, 1.35);
  b.mat(MAT.DARK);
  P(b, box(2.5, 0.06, 1.5), 37, 3.05, 1.35);
  b.mat(MAT.METAL);
  P(b, cylinder(0.055, 0.055, 1.5, 10), 37, 3.95, 2.15);
  PX(b, torus(0.42, 0.055, 18, 8, Math.PI), 37, 4.7, 2.15, ...ALONG_X);   // gooseneck
  P(b, cylinder(0.05, 0.05, 0.3, 8), 37, 4.55, 1.73);
  PX(b, cylinder(0.05, 0.05, 0.55, 8), 36.35, 4.05, 2.2, ...ALONG_X);     // cross handles
  PX(b, cylinder(0.05, 0.05, 0.55, 8), 37.65, 4.05, 2.2, ...ALONG_X);
  b.endObject();

  // range + hood on the north wall
  obj('kitchen.range', 'kitchen', [37, 0, 18.9], MAT.METAL);
  P(b, roundedBox(4.0, 3.0, 2.1, 0.05, 2), 37, 1.5, 18.85);
  b.mat(MAT.DARK);
  P(b, box(3.85, 0.1, 2.0), 37, 3.05, 18.85);
  for (const dx of [-1.35, -0.45, 0.45, 1.35]) P(b, cylinder(0.32, 0.32, 0.07, 12), 37 + dx, 3.12, 18.6);
  b.mat(MAT.METAL);
  for (const dx of [-1.5, -0.9, 0.9, 1.5]) PX(b, cylinder(0.13, 0.13, 0.2, 10), 37 + dx, 2.55, 17.72, ...ALONG_Z);
  PX(b, cylinder(0.06, 0.06, 3.6, 10), 37, 2.0, 17.68, ...ALONG_X);
  b.endObject();

  obj('kitchen.hood', 'kitchen', [37, H, 19.2], MAT.WALL);
  P(b, box(5.0, 1.1, 1.9), 37, 8.6, 19.0);
  const hood = lathe([[2.5, 0], [2.5, 0.15], [1.6, 1.5], [1.6, 1.7]], 4);
  P(b, hood, 37, 6.4, 19.0, Math.PI / 4, 1.0, 1.0, 0.62);
  b.endObject();
  lights.push({ pos: [37, 5.6, 18.3], color: [1, 0.92, 0.8], intensity: 0.5, range: 8 });

  // tall cabinets + fridge, east end of the north wall
  obj('kitchen.tall', 'kitchen', [44.2, 0, 18.6], MAT.CABINET);
  P(b, roundedBox(3.2, 8.2, 2.4, 0.04, 2), 44.2, 4.1, 18.55);
  b.mat(MAT.METAL);
  for (const dy of [3.0, 5.6]) P(b, cylinder(0.05, 0.05, 1.5, 8), 42.75, dy, 17.3);
  b.endObject();

  // open shelves on the north wall
  obj('kitchen.shelves', 'kitchen', [32, 0, 19.7], MAT.WOOD);
  for (const y of [5.0, 6.3]) {
    P(b, box(5.6, 0.14, 0.95), 32, y, 19.25);
    b.mat(MAT.METAL);
    for (const dx of [-2.4, 0, 2.4]) P(b, box(0.08, 0.5, 0.7), 32 + dx, y - 0.3, 19.3);
    b.mat(MAT.WOOD);
  }
  b.mat(MAT.TRIM);
  for (let i = 0; i < 6; i++) P(b, lathe([[0, 0], [0.16, 0.02], [0.2, 0.28], [0.14, 0.42], [0.16, 0.46], [0.13, 0.5]], 12), 30.1 + i * 0.72, 5.14, 19.2);
  b.mat(MAT.STONE);
  for (let i = 0; i < 4; i++) P(b, cylinder(0.19, 0.17, 0.62, 12), 30.6 + i * 0.9, 6.75, 19.2);
  b.endObject();

  // island
  obj('kitchen.island', 'kitchen', [38, 0, 10], MAT.CABINET);
  P(b, roundedBox(10.0, 2.95, 4.0, 0.05, 2), 38, 1.475, 10);
  b.mat(MAT.METAL);
  for (const dx of [-3.4, -1.1, 1.1, 3.4]) PX(b, cylinder(0.05, 0.05, 1.1, 8), 38 + dx, 2.2, 7.94, ...ALONG_X);
  b.mat(MAT.COUNTER);
  P(b, roundedBox(10.9, 0.28, 4.9, 0.03, 2), 38, 3.09, 10.15);
  b.endObject();

  for (const [i, x] of [34.9, 38, 41.1].entries()) {
    obj(`stool.${i}`, 'kitchen', [x, 0, 7.2], MAT.WOOD);
    barStool(b, x, 7.15);
    b.endObject();
  }

  pendant(b, obj, lights, 'pendant.island.a', 'kitchen', 35.6, 10.15, H, 0.95, 3.6);
  pendant(b, obj, lights, 'pendant.island.b', 'kitchen', 40.4, 10.15, H, 0.95, 3.6);

  obj('plant.kitchen', 'kitchen', [44.4, 0, 3.0], MAT.PLANT);
  bigPlant(b, 44.4, 3.0, 0.8);
  b.endObject();

  /* ---------- BATH ---------- */
  obj('bath.tub', 'bath', [5.0, 0, 31.0], MAT.TRIM);
  const tubOuter = lathe([[0, 0], [1.05, 0.12], [1.42, 0.55], [1.55, 1.55], [1.58, 1.95], [1.5, 2.0], [1.34, 1.9], [1.3, 0.9], [1.1, 0.4], [0, 0.32]], 28);
  P(b, tubOuter, 5.0, 0, 31.0, 0, 1.55, 1.0, 1.0);
  b.mat(MAT.STONE);
  P(b, cylinder(1.9, 1.9, 0.04, 28), 5.0, 0.34, 31.0, 0, 1.55, 1, 1);
  b.endObject();

  obj('bath.filler', 'bath', [3.0, 0, 31.0], MAT.METAL);
  P(b, cylinder(0.075, 0.09, 4.2, 12), 2.9, 2.1, 32.6);
  P(b, box(0.13, 0.13, 1.5), 2.9, 4.15, 31.9);
  P(b, cylinder(0.06, 0.06, 0.3, 10), 2.9, 3.98, 31.2);
  P(b, cylinder(0.24, 0.24, 0.09, 12), 2.9, 0.05, 32.6);
  b.endObject();

  obj('bath.vanity', 'bath', [0.9, 0, 25.5], MAT.CABINET);
  P(b, roundedBox(1.9, 2.6, 7.0, 0.05, 2), 0.95, 1.55, 25.5);
  b.mat(MAT.METAL);
  for (const dz of [-1.6, 1.6]) P(b, cylinder(0.05, 0.05, 1.3, 8), 1.85, 2.2, 25.5 + dz, HALF_PI);
  b.mat(MAT.COUNTER);
  P(b, roundedBox(2.1, 0.22, 7.2, 0.03, 2), 0.95, 2.96, 25.5);
  b.mat(MAT.TRIM);
  for (const dz of [-1.7, 1.7]) P(b, lathe([[0.62, 0], [0.66, 0.1], [0.5, 0.42], [0.46, 0.46], [0, 0.42]], 20), 1.05, 3.07, 25.5 + dz);
  b.mat(MAT.METAL);
  for (const dz of [-1.7, 1.7]) {
    P(b, cylinder(0.05, 0.05, 0.85, 10), 0.35, 3.5, 25.5 + dz);
    P(b, box(0.09, 0.09, 0.55), 0.35, 3.9, 25.5 + dz, HALF_PI, 1, 1, 1);
  }
  b.endObject();

  for (const [i, dz] of [-1.7, 1.7].entries()) {
    obj(`bath.mirror.${i}`, 'bath', [0.3, 0, 25.5 + dz], MAT.METAL);
    PX(b, torus(1.05, 0.085, 28, 8), 0.36, 5.5, 25.5 + dz, ...FACE_X);
    PX(b, cylinder(1.02, 1.02, 0.06, 28), 0.34, 5.5, 25.5 + dz, ...FACE_X);   // mirror = polished metal
    b.endObject();
  }
  for (const [i, dz] of [-1.7, 1.7].entries()) {
    obj(`bath.sconce.${i}`, 'bath', [0.35, 0, 25.5 + dz], MAT.METAL);
    sconce(b, 0.42, 6.4, 25.5 + dz, 0);
    b.endObject();
    lights.push({ pos: [1.1, 6.4, 25.5 + dz], color: [1, 0.85, 0.66], intensity: 0.5, range: 9 });
  }

  obj('bath.toilet', 'bath', [1.5, 0, 21.4], MAT.TRIM);
  P(b, roundedBox(1.5, 1.2, 1.35, 0.28, 3), 1.35, 1.35, 21.4);
  P(b, roundedBox(1.25, 0.35, 2.0, 0.16, 3), 1.5, 1.35, 22.1);
  P(b, box(0.5, 2.4, 1.6), 0.62, 1.2, 21.4);
  b.endObject();

  obj('bath.shower', 'bath', [8.2, 0, 22.4], MAT.GLASS);
  P(b, box(0.06, 7.2, 4.4), 6.6, 3.6, 22.4);
  P(b, box(3.3, 7.2, 0.06), 8.25, 3.6, 24.6);
  b.mat(MAT.METAL);
  P(b, box(0.1, 0.1, 4.4), 6.6, 7.25, 22.4);
  P(b, box(3.3, 0.1, 0.1), 8.25, 7.25, 24.6);
  P(b, cylinder(0.07, 0.07, 1.4, 10), 8.2, 7.2, 21.0, 0, 1, 1, 1);
  P(b, cylinder(0.42, 0.42, 0.07, 16), 8.2, 6.55, 21.0);
  b.mat(MAT.STONE);
  P(b, box(3.3, 0.14, 4.4), 8.25, 0.07, 22.4);
  b.endObject();

  /* ---------- DRESSING ---------- */
  obj('closet.wardrobe', 'closet', [15, 0, 33.2], MAT.CABINET);
  cabinetRun(b, 10.6, 19.4, 33.2, 2.2, 8.4, 0);
  b.endObject();
  obj('closet.wardrobe.w', 'closet', [10.9, 0, 27], MAT.CABINET);
  cabinetRun(b, 22.5, 32.4, 10.9, 2.2, 8.4, HALF_PI);
  b.endObject();

  obj('closet.island', 'closet', [15.4, 0, 27.5], MAT.WOOD);
  P(b, roundedBox(3.4, 2.6, 6.0, 0.06, 2), 15.4, 1.3, 27.5);
  b.mat(MAT.COUNTER);
  P(b, roundedBox(3.7, 0.2, 6.3, 0.03, 2), 15.4, 2.7, 27.5);
  b.mat(MAT.METAL);
  for (const dz of [-1.9, 0, 1.9]) P(b, cylinder(0.045, 0.045, 0.9, 8), 13.75, 1.9, 27.5 + dz, HALF_PI);
  b.endObject();

  obj('closet.mirror', 'closet', [19.5, 0, 23.0], MAT.TRIM);
  P(b, box(0.12, 6.4, 2.6), 19.62, 3.4, 23.0);
  b.mat(MAT.METAL);
  P(b, box(0.06, 6.0, 2.25), 19.52, 3.4, 23.0);
  b.endObject();

  pendant(b, obj, lights, 'pendant.closet', 'closet', 15.4, 27.5, H, 0.5, 3.4);

  /* ---------- BEDROOM ---------- */
  obj('rug.bed', 'bedroom', [33, 0, 25.5], MAT.TEXTILE_B);
  P(b, box(14, 0.07, 11, 1), 33, 0.035, 25.5);
  b.endObject();

  obj('bed', 'bedroom', [33, 0, 24.2], MAT.TEXTILE_A);
  bedKing(b, 33, 24.2);
  b.endObject();

  for (const [i, x] of [28.6, 37.4].entries()) {
    obj(`nightstand.${i}`, 'bedroom', [x, 0, 21.4], MAT.WOOD);
    P(b, roundedBox(2.2, 1.9, 1.7, 0.06, 2), x, 1.15, 21.4);
    b.mat(MAT.METAL);
    P(b, cylinder(0.05, 0.05, 0.7, 8), x, 1.55, 20.5, HALF_PI);
    for (const dx of [-0.9, 0.9]) P(b, box(0.13, 0.2, 0.13), x + dx, 0.12, 21.4);
    b.mat(MAT.WOOD);
    b.endObject();
    pendant(b, obj, lights, `pendant.bed.${i}`, 'bedroom', x, 21.4, H, 0.36, 5.0);
  }

  obj('bench.bed', 'bedroom', [33, 0, 28.4], MAT.TEXTILE_A);
  P(b, roundedBox(6.2, 0.55, 1.7, 0.2, 3), 33, 1.5, 28.4);
  b.mat(MAT.WOOD);
  for (const dx of [-2.7, 2.7]) {
    P(b, box(0.16, 1.25, 1.5), 33 + dx, 0.62, 28.4);
  }
  b.endObject();

  obj('chair.read', 'bedroom', [43, 0, 27.5], MAT.TEXTILE_A);
  loungeChair(b, 43, 27.5, -HALF_PI - 0.4);
  b.endObject();

  obj('art.bed', 'bedroom', [39.5, 0, 20.4], MAT.ART);
  artPiece(b, 39.5, 5.6, 20.42, 'z', 5.0, 3.4);
  b.endObject();

  obj('plant.bed', 'bedroom', [44.3, 0, 21.6], MAT.PLANT);
  bigPlant(b, 44.3, 21.6, 1.05);
  b.endObject();

  /* ================================================================= FINISH */
  const mesh = b.build();
  const aoRooms = plan.rooms.map(r => ({ x0: r.x0, x1: r.x1, z0: r.z0, z1: r.z1, y0: 0, y1: H }));
  bakeAO(mesh.vertices, mesh.objects, aoRooms);
  return { mesh, objects: mesh.objects, lights, plan };
}

/* ====================================================== furniture builders */

function sofa(b, x, z, ry, w) {
  const d = 3.4;
  P(b, roundedBox(w, 1.0, d, 0.22, 3), x, 0.95, z, ry);
  P(b, roundedBox(w - 0.1, 0.55, d - 0.9, 0.24, 3), x, 1.62, z + Math.cos(ry) * 0.18, ry);
  // back
  const bx = Math.sin(ry) * 0, bz = 0;
  P(b, roundedBox(w, 2.0, 0.85, 0.3, 3), x - Math.sin(ry) * (d / 2 - 0.42), 1.95, z - Math.cos(ry) * (d / 2 - 0.42), ry);
  // arms
  for (const s of [-1, 1]) {
    P(b, roundedBox(0.85, 1.55, d - 0.2, 0.3, 3),
      x + Math.cos(ry) * s * (w / 2 - 0.42), 1.55, z - Math.sin(ry) * s * (w / 2 - 0.42), ry);
  }
  // cushions
  const n = Math.max(2, Math.round(w / 2.8));
  for (let i = 0; i < n; i++) {
    const t = (i + 0.5) / n - 0.5;
    P(b, roundedBox(w / n - 0.22, 0.42, d - 1.3, 0.18, 3),
      x + Math.cos(ry) * t * w, 2.15, z - Math.sin(ry) * t * w, ry);
  }
  b.mat(MAT.TEXTILE_B);
  for (const s of [-0.62, 0.62]) {
    P(b, roundedBox(1.3, 1.3, 0.42, 0.2, 3),
      x + Math.cos(ry) * s * (w / 2), 2.6, z - Math.sin(ry) * s * (w / 2) - Math.cos(ry) * 0.9, ry + 0.2);
  }
  b.mat(MAT.WOOD);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    P(b, cylinder(0.075, 0.09, 0.45, 8),
      x + Math.cos(ry) * sx * (w / 2 - 0.5) - Math.sin(ry) * sz * (d / 2 - 0.5), 0.22,
      z - Math.sin(ry) * sx * (w / 2 - 0.5) - Math.cos(ry) * sz * (d / 2 - 0.5));
  }
  b.mat(MAT.TEXTILE_A);
}

function loungeChair(b, x, z, ry) {
  P(b, roundedBox(2.9, 0.85, 2.9, 0.26, 3), x, 1.15, z, ry);
  P(b, roundedBox(2.7, 2.1, 0.7, 0.3, 3), x - Math.sin(ry) * 1.1, 2.1, z - Math.cos(ry) * 1.1, ry);
  for (const s of [-1, 1]) {
    P(b, roundedBox(0.6, 1.15, 2.5, 0.26, 3), x + Math.cos(ry) * s * 1.15, 1.75, z - Math.sin(ry) * s * 1.15, ry);
  }
  b.mat(MAT.WOOD);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    P(b, cylinder(0.07, 0.085, 0.75, 8),
      x + Math.cos(ry) * sx * 1.05 - Math.sin(ry) * sz * 1.05, 0.37,
      z - Math.sin(ry) * sx * 1.05 - Math.cos(ry) * sz * 1.05);
  }
  b.mat(MAT.TEXTILE_A);
}

function bedKing(b, x, z) {
  // headboard
  P(b, roundedBox(7.4, 4.6, 0.75, 0.3, 3), x, 2.3, z - 3.55);
  // mattress + base
  b.mat(MAT.WOOD);
  P(b, roundedBox(6.9, 1.0, 7.0, 0.08, 2), x, 0.72, z + 0.1);
  b.mat(MAT.TEXTILE_A);
  P(b, roundedBox(6.7, 1.15, 6.85, 0.26, 3), x, 1.78, z + 0.1);
  b.mat(MAT.TRIM);
  P(b, roundedBox(6.75, 0.42, 6.5, 0.2, 3), x, 2.45, z + 0.25);
  // duvet fold
  P(b, roundedBox(6.8, 0.5, 2.4, 0.24, 3), x, 2.62, z + 2.3);
  // pillows
  for (const dx of [-1.55, 1.55]) {
    P(b, roundedBox(2.7, 0.62, 1.5, 0.3, 3), x + dx, 2.85, z - 2.55, 0.04);
    P(b, roundedBox(2.3, 0.5, 1.25, 0.26, 3), x + dx, 3.3, z - 2.2, -0.05);
  }
  b.mat(MAT.TEXTILE_B);
  P(b, roundedBox(2.0, 0.45, 1.05, 0.22, 3), x, 3.25, z - 2.0, 0.1);
  b.mat(MAT.TEXTILE_A);
}

function barStool(b, x, z) {
  P(b, roundedBox(1.35, 0.28, 1.25, 0.12, 3), x, 2.3, z);
  P(b, roundedBox(1.2, 1.35, 0.28, 0.12, 3), x, 3.05, z - 0.5);
  b.mat(MAT.METAL);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    P(b, cylinder(0.045, 0.055, 2.2, 8), x + sx * 0.5, 1.1, z + sz * 0.45);
  }
  P(b, box(1.0, 0.06, 0.06), x, 0.75, z + 0.45);
  P(b, box(1.0, 0.06, 0.06), x, 0.75, z - 0.45);
  b.mat(MAT.WOOD);
}

function shelfUnit(b, x, z, ry, w, h) {
  const d = 1.15;
  P(b, box(0.14, h, d), x - Math.cos(ry) * (w / 2), h / 2, z + Math.sin(ry) * (w / 2), ry);
  P(b, box(0.14, h, d), x + Math.cos(ry) * (w / 2), h / 2, z - Math.sin(ry) * (w / 2), ry);
  const n = 5;
  for (let i = 0; i <= n; i++) {
    const y = 0.35 + (i / n) * (h - 0.6);
    P(b, box(w, 0.12, d), x, y, z, ry);
  }
  // objects on the shelves — deterministic, not random
  const cols = [MAT.STONE, MAT.WOOD, MAT.ART, MAT.PLANT, MAT.TRIM];
  for (let i = 1; i <= n; i++) {
    const y = 0.35 + (i / n) * (h - 0.6);
    for (let k = 0; k < 3; k++) {
      const t = (k + 0.5) / 3 - 0.5;
      const s = 0.22 + ((i * 7 + k * 13) % 5) * 0.055;
      b.mat(cols[(i + k) % cols.length]);
      const px = x + Math.cos(ry) * t * (w - 0.8), pz = z - Math.sin(ry) * t * (w - 0.8);
      if ((i + k) % 3 === 0) P(b, cylinder(s * 0.8, s * 0.7, s * 2.6, 12), px, y + s * 1.35, pz);
      else if ((i + k) % 3 === 1) P(b, box(s * 1.4, s * 2.2, s * 1.1), px, y + s * 1.1, pz, 0.2);
      else P(b, sphere(s, 12, 8, 1.15), px, y + s * 1.15, pz);
    }
  }
  b.mat(MAT.WOOD);
}

function floorLamp(b, x, z) {
  P(b, cylinder(0.62, 0.68, 0.11, 20), x, 0.055, z);
  P(b, cylinder(0.055, 0.055, 5.1, 10), x, 2.6, z);
  P(b, box(0.055, 0.055, 1.5), x, 5.12, z + 0.72);
  b.mat(MAT.TRIM);
  P(b, lathe([[0, 0], [0.72, 0], [0.86, 1.05], [0, 1.05]], 20), x, 4.1, z + 1.42);
  b.mat(MAT.EMISSIVE);
  P(b, sphere(0.3, 12, 8), x, 4.5, z + 1.42);
  b.mat(MAT.METAL);
}

function sconce(b, x, y, z, ry) {
  PX(b, cylinder(0.34, 0.34, 0.12, 18), x, y, z, ...FACE_X);
  P(b, box(0.55, 0.09, 0.09), x + (ry ? -0.3 : 0.3), y, z);
  b.mat(MAT.TRIM);
  P(b, lathe([[0, 0], [0.36, 0.02], [0.42, 0.62], [0, 0.62]], 16), x + (ry ? -0.62 : 0.62), y - 0.31, z);
  b.mat(MAT.EMISSIVE);
  P(b, sphere(0.17, 10, 6), x + (ry ? -0.62 : 0.62), y, z);
  b.mat(MAT.METAL);
}

function pendant(b, obj, lights, name, room, x, z, H, r, drop) {
  obj(name, room, [x, H, z], MAT.METAL);
  P(b, cylinder(0.05, 0.05, drop, 8), x, H - drop / 2, z);
  P(b, cylinder(0.26, 0.26, 0.09, 14), x, H - 0.05, z);
  b.mat(MAT.TRIM);
  P(b, lathe([[0, 0], [r * 0.35, 0.02], [r, r * 0.85], [r * 0.96, r * 0.95], [r * 0.3, r * 0.2]], 22), x, H - drop, z);
  b.mat(MAT.EMISSIVE);
  P(b, sphere(r * 0.42, 12, 8), x, H - drop + r * 0.28, z);
  b.endObject();
  lights.push({ pos: [x, H - drop + r * 0.2, z], color: [1, 0.8, 0.55], intensity: 0.85, range: 15, obj: name });
}

function artPiece(b, x, y, z, axis, w, h, portrait) {
  const fr = 0.14;
  if (axis === 'x') {
    P(b, box(0.09, h + fr * 2, w + fr * 2), x, y, z);
    b.mat(MAT.ART);
    P(b, box(0.02, h, w), x + 0.04, y, z);
  } else {
    P(b, box(w + fr * 2, h + fr * 2, 0.09), x, y, z);
    b.mat(MAT.ART);
    P(b, box(w, h, 0.02), x, y, z + 0.04);
  }
  b.mat(MAT.ART);
}

function bigPlant(b, x, z, scale) {
  b.mat(MAT.STONE);
  P(b, lathe([[0, 0], [0.72, 0.04], [0.82, 0.7], [0.62, 1.75], [0.66, 1.85], [0.5, 1.8]], 20), x, 0, z, 0, scale, scale, scale);
  b.mat(MAT.DARK);
  P(b, cylinder(0.55 * scale, 0.55 * scale, 0.08, 16), x, 1.78 * scale, z);
  b.mat(MAT.PLANT);
  const stems = 11;
  for (let i = 0; i < stems; i++) {
    const a = (i / stems) * Math.PI * 2 + 0.4;
    const lean = 0.20 + (i % 4) * 0.085;
    const hgt = (2.5 + (i % 3) * 0.85) * scale;
    const tipx = x + Math.cos(a) * lean * hgt, tipz = z + Math.sin(a) * lean * hgt;
    P(b, cylinder(0.028, 0.05, hgt, 6), (x + tipx) / 2, 1.8 * scale + hgt / 2, (z + tipz) / 2);
    for (let k = 0; k < 5; k++) {
      const t = 0.38 + k * 0.155;
      const lx = x + (tipx - x) * t, lz = z + (tipz - z) * t;
      const ly = 1.8 * scale + hgt * t;
      // long narrow leaves, splayed — not pebbles
      P(b, sphere(0.26 * scale, 9, 5, 0.085), lx, ly, lz, a + k * 1.25, 1, 1, 2.9);
    }
  }
  b.mat(MAT.PLANT);
}

function cabinetRun(b, from, to, coord, depth, height, ry) {
  const len = to - from, c = (from + to) / 2;
  const along = ry === 0;
  if (along) {
    P(b, roundedBox(len, height - 0.3, depth, 0.04, 2), c, (height - 0.3) / 2 + 0.3, coord);
    P(b, box(len - 0.2, 0.3, depth - 0.35), c, 0.15, coord);
  } else {
    P(b, roundedBox(depth, height - 0.3, len, 0.04, 2), coord, (height - 0.3) / 2 + 0.3, c);
    P(b, box(depth - 0.35, 0.3, len - 0.2), coord, 0.15, c);
  }
  // door reveals
  b.mat(MAT.METAL);
  const n = Math.max(2, Math.round(len / 2.0));
  for (let i = 0; i < n; i++) {
    const t = from + (i + 0.5) * (len / n);
    if (along) P(b, cylinder(0.04, 0.04, Math.min(1.1, height * 0.35), 8), t, height * 0.62, coord - depth / 2 - 0.05, HALF_PI);
    else P(b, cylinder(0.04, 0.04, Math.min(1.1, height * 0.35), 8), coord + depth / 2 + 0.05, height * 0.62, t);
  }
  b.mat(MAT.CABINET);
}
