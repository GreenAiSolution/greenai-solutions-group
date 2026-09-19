// ATRIUM — catalog entries → the 16 shader material slots.
// Change a palette and the same object that re-prices also re-renders. One source.

import { MAT, NMAT } from './shaders.js';
import { lerp } from './math.js';

// which procedural detail routine each catalog material wants
const FAMILY = {
  oak_wide: 1, walnut_herr: 1, oak_panel: 1, butcher: 1, rift_oak: 1, walnut_slab: 1,
  concrete_pol: 2, travertine: 2, quartz: 2, marble_cala: 2, soapstone: 2,
  terracotta: 5,
  limewash: 3, flat_paint: 3, venetian: 3, clay_plaster: 3, shaker_paint: 3,
  lacquer_bone: 0,
  brass_unlac: 6, matte_black: 6, nickel: 6, bronze: 6,
  linen_oat: 4, boucle_cream: 4, leather_tan: 4, velvet_moss: 4,
};

// bump strength per family — enough to catch the light, never enough to look like sandpaper
const DETAIL_BY_FAMILY = { 0: 0.0, 1: 0.09, 2: 0.07, 3: 0.11, 4: 0.16, 5: 0.24, 6: 0.05, 7: 0.14, 8: 0.06 };

const fam = (m) => (m && FAMILY[m.id] !== undefined ? FAMILY[m.id] : 0);
const det = (f, scale = 1) => (DETAIL_BY_FAMILY[f] || 0) * scale;
const mul = (c, k) => [c[0] * k, c[1] * k, c[2] * k];

function slot(albedo, roughness, metallic, emissive, family, detail) {
  return { albedo, roughness, metallic, emissive, family, detail };
}

export function buildMaterialSet(catalog, sel, palette) {
  const S = catalog.surfaces;
  const find = (k, id) => S[k].find(x => x.id === id) || S[k][0];
  const F = find('floor', sel.floor);
  const W = find('wall', sel.wall);
  const C = find('counter', sel.counter);
  const K = find('cabinet', sel.cabinet);
  const M = find('metal', sel.metal);
  const X = find('textile', sel.textile);

  const lamp = (palette && palette.lamp) || [1, 0.8, 0.55];
  const acc = (palette && palette.sky) || [0.8, 0.7, 0.6];

  const out = new Array(NMAT);
  out[MAT.FLOOR]     = slot(F.albedo.slice(), F.roughness, F.metallic, [0, 0, 0], fam(F), det(fam(F), 1.0));
  out[MAT.WALL]      = slot(W.albedo.slice(), W.roughness, W.metallic, [0, 0, 0], fam(W), det(fam(W), 1.0));
  out[MAT.CEILING]   = slot(mul(W.albedo, 1.06), Math.min(1, W.roughness + 0.04), 0, [0, 0, 0], fam(W), det(fam(W), 0.6));
  out[MAT.COUNTER]   = slot(C.albedo.slice(), C.roughness, C.metallic, [0, 0, 0], fam(C), det(fam(C), 0.8));
  out[MAT.CABINET]   = slot(K.albedo.slice(), K.roughness, K.metallic, [0, 0, 0], fam(K), det(fam(K), 0.8));
  out[MAT.METAL]     = slot(M.albedo.slice(), M.roughness, M.metallic, [0, 0, 0], fam(M), det(fam(M), 1.0));
  out[MAT.TEXTILE_A] = slot(X.albedo.slice(), X.roughness, 0, [0, 0, 0], fam(X), det(fam(X), 1.0));
  out[MAT.TEXTILE_B] = slot(mul(X.albedo, 0.62), Math.min(1, X.roughness + 0.02), 0, [0, 0, 0], fam(X), det(fam(X), 1.2));
  // accent wood tracks the cabinetry when the cabinetry is wood, else stays walnut
  const woodish = fam(K) === 1 ? K : { albedo: [0.30, 0.20, 0.13], roughness: 0.44, metallic: 0, id: 'walnut_slab' };
  out[MAT.WOOD]     = slot(mul(woodish.albedo, 0.92), woodish.roughness, 0, [0, 0, 0], 1, det(1, 1.0));
  out[MAT.STONE]    = slot(mul(C.albedo, 0.86), Math.min(1, C.roughness + 0.16), 0, [0, 0, 0], 2, det(2, 1.1));
  out[MAT.GLASS]    = slot([0.62, 0.72, 0.78], 0.03, 0.0, [0, 0, 0], 0, 0);
  out[MAT.PLANT]    = slot([0.052, 0.205, 0.062], 0.54, 0.0, [0, 0, 0], 7, det(7, 1.0));
  out[MAT.EMISSIVE] = slot([0.9, 0.9, 0.9], 0.9, 0.0, mul(lamp, 5.2), 0, 0);
  out[MAT.DARK]     = slot([0.035, 0.036, 0.042], 0.42, 0.25, [0, 0, 0], 6, det(6, 0.6));
  out[MAT.ART]      = slot([acc[0] * 0.5, acc[1] * 0.42, acc[2] * 0.38], 0.72, 0.0, [0, 0, 0], 8, det(8, 1.0));
  out[MAT.TRIM]     = slot(mul(W.albedo, 1.10), Math.max(0.18, W.roughness - 0.35), 0, [0, 0, 0], 0, 0.0);
  return out;
}

/** Deep-copy so the animator has somewhere to write. */
export function cloneMaterialSet(set) {
  return set.map(m => ({
    albedo: m.albedo.slice(), roughness: m.roughness, metallic: m.metallic,
    emissive: m.emissive.slice(), family: m.family, detail: m.detail,
  }));
}

/** Blend between two sets. Family snaps at the halfway mark — you cannot half-be oak. */
export function lerpMaterialSet(out, a, bSet, t) {
  for (let i = 0; i < NMAT; i++) {
    const A = a[i], B = bSet[i], O = out[i];
    for (let c = 0; c < 3; c++) {
      O.albedo[c] = lerp(A.albedo[c], B.albedo[c], t);
      O.emissive[c] = lerp(A.emissive[c], B.emissive[c], t);
    }
    O.roughness = lerp(A.roughness, B.roughness, t);
    O.metallic = lerp(A.metallic, B.metallic, t);
    O.detail = lerp(A.detail, B.detail, t);
    O.family = t < 0.5 ? A.family : B.family;
  }
  return out;
}

export function lerpLighting(a, b, t) {
  const L = (x, y) => [lerp(x[0], y[0], t), lerp(x[1], y[1], t), lerp(x[2], y[2], t)];
  return {
    sky: L(a.sky, b.sky),
    ground: L(a.ground, b.ground),
    sun: L(a.sun, b.sun),
    lamp: L(a.lamp, b.lamp),
    sun_energy: lerp(a.sun_energy, b.sun_energy, t),
  };
}

/** The six surface choices a palette stands for. */
export function selectionFromPalette(p) {
  return {
    floor: p.floor, wall: p.wall, counter: p.counter,
    cabinet: p.cabinet, metal: p.metal, textile: p.textile,
  };
}
