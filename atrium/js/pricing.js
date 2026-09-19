// ATRIUM — the estimate. Every quantity is derived from engine/plan.json,
// every rate from engine/catalog.json. Nothing here is typed in by hand.
// engine/price.py runs the identical math from the terminal.

export const SOFT_GOODS = new Set([
  'sofa_3seat', 'lounge_chair', 'reading_chair', 'bench_entry', 'bench_bed',
  'bar_stool', 'bed_king', 'rug_9x12', 'runner_rug',
]);

export const METAL_TOUCHED = new Set([
  'floor_lamp', 'pendant_small', 'island_pendant', 'sconce', 'faucet_bridge',
  'tub_filler', 'mirror_round', 'mirror_full', 'shower_glass', 'range_48',
  'fridge_counter_depth', 'hood_vent',
]);

function byId(list, id) { return list.find(x => x.id === id); }

/** Quantities for one room, straight off the plan. */
export function roomQuantities(plan, room) {
  const H = plan.meta.ceiling_height;
  const w = room.x1 - room.x0, d = room.z1 - room.z0;
  const floor = w * d;
  const perimeter = 2 * (w + d);
  const gross = perimeter * H;
  let openArea = 0;
  for (const op of plan.openings) {
    if (op.room !== room.id) continue;
    openArea += op.width * op.height;
  }
  return {
    floor_sqft: floor,
    ceiling_sqft: floor,
    perimeter_lf: perimeter,
    wall_gross_sqft: gross,
    opening_sqft: openArea,
    wall_sqft: Math.max(0, gross - openArea),
    counter_lf: room.counter_lf || 0,
    cabinet_lf: room.cabinet_lf || 0,
    fixture_count: (room.fixtures || []).length,
  };
}

/**
 * sel = { floor, wall, counter, cabinet, metal, textile } — catalog ids.
 * Returns per-room lines and portfolio totals.
 */
export function computeEstimate(plan, catalog, sel) {
  const S = catalog.surfaces;
  const floorM = byId(S.floor, sel.floor) || S.floor[0];
  const wallM = byId(S.wall, sel.wall) || S.wall[0];
  const counterM = byId(S.counter, sel.counter) || S.counter[0];
  const cabinetM = byId(S.cabinet, sel.cabinet) || S.cabinet[0];
  const metalM = byId(S.metal, sel.metal) || S.metal[0];
  const textileM = byId(S.textile, sel.textile) || S.textile[0];
  const L = catalog.labor;

  const rooms = [];
  const totals = { materials: 0, labor: 0, fixtures: 0, subtotal: 0 };

  for (const r of plan.rooms) {
    if (!r.priced) continue;
    const q = roomQuantities(plan, r);
    const lines = [];
    let mat = 0, lab = 0, fix = 0;

    const push = (label, qty, unit, rate, kind) => {
      const amount = qty * rate;
      if (Math.abs(amount) < 0.005) return;
      lines.push({ label, qty: +qty.toFixed(2), unit, rate: +rate.toFixed(2), amount, kind });
      if (kind === 'material') mat += amount;
      else if (kind === 'labor') lab += amount;
      else fix += amount;
    };

    push(`${floorM.name} — flooring`, q.floor_sqft, 'sq ft', floorM.cost, 'material');
    push('Flooring, installed', q.floor_sqft, 'sq ft', L.floor_per_sqft, 'labor');

    push(`${wallM.name} — walls`, q.wall_sqft, 'sq ft', wallM.cost, 'material');
    push('Wall finish, applied', q.wall_sqft, 'sq ft', L.wall_finish_per_sqft, 'labor');

    push(`${wallM.name} — ceiling`, q.ceiling_sqft, 'sq ft', wallM.cost, 'material');
    push('Ceiling finish, applied', q.ceiling_sqft, 'sq ft', L.ceiling_per_sqft, 'labor');

    if (q.counter_lf > 0) {
      push(`${counterM.name} — countertop`, q.counter_lf, 'lin ft', counterM.cost, 'material');
      push('Countertop, templated + set', q.counter_lf, 'lin ft', L.counter_per_lf, 'labor');
    }
    if (q.cabinet_lf > 0) {
      push(`${cabinetM.name} — cabinetry`, q.cabinet_lf, 'lin ft', cabinetM.cost, 'material');
      push('Cabinetry, installed', q.cabinet_lf, 'lin ft', L.cabinet_install_per_lf, 'labor');
    }

    for (const fid of (r.fixtures || [])) {
      const f = byId(catalog.fixtures, fid);
      if (!f) continue;
      let cost = f.cost;
      if (SOFT_GOODS.has(fid)) cost *= (1 + textileM.cost);
      if (METAL_TOUCHED.has(fid)) cost *= (1 + metalM.cost);
      push(f.name, 1, 'ea', cost, 'fixture');
    }
    if (q.fixture_count > 0) {
      push('Delivery, set + install', q.fixture_count, 'ea', L.fixture_set_each, 'labor');
    }

    const subtotal = mat + lab + fix;
    rooms.push({
      id: r.id, name: r.name, q, lines,
      materials: mat, labor: lab, fixtures: fix, subtotal,
      per_sqft: subtotal / q.floor_sqft,
    });
    totals.materials += mat; totals.labor += lab; totals.fixtures += fix; totals.subtotal += subtotal;
  }

  const design = totals.subtotal * catalog.fees.design_pct;
  const contingency = totals.subtotal * catalog.fees.contingency_pct;
  const grand = totals.subtotal + design + contingency;
  const totalSqft = rooms.reduce((s, r) => s + r.q.floor_sqft, 0);

  return {
    rooms,
    totals: { ...totals, design, contingency, grand, sqft: totalSqft, per_sqft: grand / totalSqft },
    selection: {
      floor: floorM, wall: wallM, counter: counterM,
      cabinet: cabinetM, metal: metalM, textile: textileM,
    },
  };
}

export const money = (n, dp = 0) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp });

export const moneyShort = (n) => {
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(2) + 'M';
  if (n >= 1e3) return '$' + Math.round(n / 1e3) + 'k';
  return '$' + Math.round(n);
};
