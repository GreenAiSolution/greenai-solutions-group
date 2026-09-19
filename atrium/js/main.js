// ATRIUM — main. Loads the plan, builds the house, drives the journey.

import { Renderer } from './renderer.js';
import { buildHouse } from './house.js';
import { Journey, Assembly, gradeFor } from './scroll.js';
import { buildMaterialSet, cloneMaterialSet, lerpMaterialSet, lerpLighting, selectionFromPalette } from './materials.js';
import { computeEstimate, money, moneyShort } from './pricing.js';
import { UI, srgb } from './ui.js';
import { clamp, lerp, smoothstep, v3, DEG } from './math.js';

const CAPTIONS = {
  threshold: {
    title: 'Atrium',
    body: 'A house you can walk through before it exists — and a number that moves with every choice you make inside it.',
  },
  approach: {
    title: 'The Ocotillo',
    body: 'Single level, drawn for a low western sun. Keep scrolling and it builds itself around you.',
  },
  entry: {
    title: 'Entry',
    body: 'Eighty square feet of deliberate nothing. The first thing a house should offer is somewhere to stop.',
  },
  living_in: {
    title: 'Living Room',
    body: 'Twelve feet of south glass and ten of west. Change the floor here and the whole room changes temperature.',
  },
  living_sit: {
    title: 'Living Room',
    body: 'Sit down in it. Every surface you can see is a line in the estimate, and every line is priced per unit — not allowed for.',
  },
  kitchen_in: {
    title: 'Kitchen',
    body: 'Twenty-six linear feet of counter, thirty-two of cabinetry. This is the room where a budget is won or lost.',
  },
  kitchen_is: {
    title: 'Kitchen',
    body: 'Swap the counter from quartz to Calacatta and watch one number move. That is the whole product.',
  },
  bath: {
    title: 'Primary Bath',
    body: 'One window at eye level over the tub. A vanity you will look at every morning for the next ten years.',
  },
  bedroom: {
    title: 'Primary Bedroom',
    body: 'Sixteen feet of north glass — the only room where the light is supposed to be boring.',
  },
  ledger: {
    title: 'The Ledger',
    body: 'Every square foot on this screen was measured off the drawing, then priced from the book. Nothing here was rounded to look good.',
  },
  close: {
    title: 'Yours, monthly',
    body: 'Keep the home on file. Keep changing your mind. The estimate keeps up.',
  },
};

const ROOM_FOR_SECTION = {
  entry: 'entry', living_in: 'living', living_sit: 'living',
  kitchen_in: 'kitchen', kitchen_is: 'kitchen', bath: 'bath', bedroom: 'bedroom',
};

class Atrium {
  async start() {
    const canvas = document.getElementById('gl');
    try {
      this.r = new Renderer(canvas);
    } catch (e) {
      console.error(e);
      document.getElementById('boot').remove();
      document.getElementById('fallback').style.display = 'flex';
      return;
    }

    const boot = (p, m) => this.ui ? this.ui.boot(p, m) : null;

    const [plan, catalog, config] = await Promise.all([
      fetch('./engine/plan.json').then(r => r.json()),
      fetch('./engine/catalog.json').then(r => r.json()),
      fetch('./engine/config.json').then(r => r.json()).catch(() => ({ payment_links: {} })),
    ]);
    this.plan = plan; this.catalog = catalog; this.config = config;

    this.ui = new UI(catalog, plan, {
      palette: (id) => this.setPalette(id),
      surface: (k, id) => this.setSurface(k, id),
      subscribe: (id) => this.subscribe(id),
      exportSpec: () => this.exportSpec(),
    });
    boot(0.15, 'drawing the house');

    await new Promise(r => setTimeout(r, 30));
    const t0 = performance.now();
    const built = buildHouse(plan);
    this.house = built;
    this.buildMs = performance.now() - t0;
    boot(0.62, 'baking the light');

    await new Promise(r => setTimeout(r, 30));
    this.r.uploadScene(built.mesh);
    this.journey = new Journey(plan);
    this.assembly = new Assembly(built.objects);
    boot(0.85, 'setting the surfaces');

    // sun from the plan
    const az = plan.sun.azimuth_deg * DEG, alt = plan.sun.altitude_deg * DEG;
    this.sunDir = new Float32Array([
      -(Math.cos(alt) * Math.sin(az)), -Math.sin(alt), -(Math.cos(alt) * Math.cos(az)),
    ]);

    // starting palette
    this.paletteId = catalog.palettes[0].id;
    this.sel = selectionFromPalette(catalog.palettes[0]);
    const p0 = catalog.palettes[0];
    this.matCur = buildMaterialSet(catalog, this.sel, p0);
    this.matFrom = cloneMaterialSet(this.matCur);
    this.matTo = cloneMaterialSet(this.matCur);
    this.lightFrom = { sky: p0.sky, ground: p0.ground, sun: p0.sun, lamp: p0.lamp, sun_energy: p0.sun_energy };
    this.lightTo = this.lightFrom;
    this.lightCur = this.lightFrom;
    this.blend = 1;

    this.ui.setPalette(this.paletteId, this.sel);
    this.ui.setAccent(srgb(p0.sun.map(c => c * 0.85)));
    this.recompute();

    // scroll state
    this.tTarget = 0; this.t = 0;
    this.mouse = { x: 0, y: 0, tx: 0, ty: 0 };
    this.time = 0;
    this.objData = this.r.objData;

    this.bind();
    this.resize();
    boot(1.0, 'ready');
    setTimeout(() => this.ui.bootDone(), 260);

    // handy for driving the journey from the console: __atrium.seek(0.4)
    window.__atrium = this;

    this.last = performance.now();
    requestAnimationFrame(() => this.frame());
  }

  /** Jump straight to a point in the journey, no easing. */
  seek(t) {
    const j = document.getElementById('journey');
    const span = Math.max(1, j.offsetHeight - window.innerHeight);
    window.scrollTo({ top: t * span, behavior: 'instant' });
    this.tTarget = this.t = clamp(t, 0, 1);
    return this.t;
  }

  bind() {
    window.addEventListener('resize', () => this.resize(), { passive: true });
    window.addEventListener('scroll', () => this.readScroll(), { passive: true });
    window.addEventListener('pointermove', (e) => {
      this.mouse.tx = (e.clientX / window.innerWidth) * 2 - 1;
      this.mouse.ty = (e.clientY / window.innerHeight) * 2 - 1;
    }, { passive: true });
    this.readScroll();
  }

  resize() {
    const w = window.innerWidth, h = window.innerHeight;
    this.vw = w; this.vh = h;
    // step the render scale down on very large or very dense displays
    const px = w * h * (window.devicePixelRatio || 1) ** 2;
    this.r.quality = px > 9e6 ? 0.72 : px > 5e6 ? 0.85 : 1.0;
    this.r.resize(w, h, window.devicePixelRatio || 1);
  }

  readScroll() {
    const j = document.getElementById('journey');
    const span = Math.max(1, j.offsetHeight - window.innerHeight);
    this.tTarget = clamp(window.scrollY / span, 0, 1);
    // past the runway the offer takes over and the walkthrough chrome stands down
    const past = window.scrollY - span;
    document.body.classList.toggle('in-offer', past > window.innerHeight * 0.12);
  }

  /* ------------------------------------------------------------ choices */
  setPalette(id) {
    const p = this.catalog.palettes.find(x => x.id === id);
    if (!p) return;
    this.paletteId = id;
    this.sel = selectionFromPalette(p);
    this.startBlend(buildMaterialSet(this.catalog, this.sel, p),
      { sky: p.sky, ground: p.ground, sun: p.sun, lamp: p.lamp, sun_energy: p.sun_energy });
    this.ui.setPalette(id, this.sel);
    this.ui.setAccent(srgb(p.sun.map(c => c * 0.85)));
    this.recompute();
  }

  setSurface(key, id) {
    this.sel = { ...this.sel, [key]: id };
    const pal = this.catalog.palettes.find(x => x.id === this.paletteId);
    const stillMatches = pal && Object.keys(this.sel).every(k => selectionFromPalette(pal)[k] === this.sel[k]);
    if (!stillMatches) { this.paletteId = null; this.ui.markCustom(); }
    const light = this.lightTo;
    this.startBlend(buildMaterialSet(this.catalog, this.sel, { sky: light.sky, lamp: light.lamp }), light);
    this.ui.setSelection(this.sel);
    this.recompute();
  }

  startBlend(matTo, lightTo) {
    this.matFrom = cloneMaterialSet(this.matCur);
    this.matTo = matTo;
    this.lightFrom = this.lightCur;
    this.lightTo = lightTo;
    this.blend = 0;
  }

  recompute() {
    this.est = computeEstimate(this.plan, this.catalog, this.sel);
    this.ui.setEstimate(this.est);
  }

  /* ------------------------------------------------------------ actions */
  subscribe(planId) {
    const link = (this.config.payment_links || {})[planId];
    if (link) { window.location.href = link; return; }
    const p = this.catalog.plans.find(x => x.id === planId);
    alert(`Checkout for ${p.name} ($${p.price}/${p.cadence}) is not wired to a payment link yet.\n\n` +
      `Add it to engine/config.json under payment_links.${planId} and this button will take the money.`);
  }

  exportSpec() {
    const est = this.est;
    const spec = {
      product: 'ATRIUM spec sheet',
      generated: new Date().toISOString(),
      home: { name: this.plan.meta.name, sqft: est.totals.sqft, ceiling_height: this.plan.meta.ceiling_height },
      palette: this.paletteId || 'custom',
      selection: Object.fromEntries(Object.entries(est.selection).map(([k, m]) => [k, { id: m.id, name: m.name, cost: m.cost, unit: m.unit }])),
      rooms: est.rooms.map(r => ({
        room: r.name, quantities: r.q, subtotal: r.subtotal, per_sqft: r.per_sqft,
        lines: r.lines.map(l => ({ item: l.label, qty: l.qty, unit: l.unit, rate: l.rate, amount: +l.amount.toFixed(2) })),
      })),
      totals: Object.fromEntries(Object.entries(est.totals).map(([k, v]) => [k, +v.toFixed(2)])),
      basis: this.catalog.meta.basis,
      excluded: this.catalog.labor.note,
    };
    const blob = new Blob([JSON.stringify(spec, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `atrium-spec-${(this.paletteId || 'custom')}-${Math.round(est.totals.grand)}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }

  /* -------------------------------------------------------------- frame */
  frame() {
    const now = performance.now();
    const dt = Math.min(0.05, (now - this.last) / 1000);
    this.last = now;
    this.tick(dt);
    requestAnimationFrame(() => this.frame());
  }

  /** One full step. Split out from frame() so it can be driven synchronously. */
  tick(dt) {
    this.time += dt;

    // silky scroll
    this.t += (this.tTarget - this.t) * Math.min(1, dt * 7.5);
    const t = this.t;

    // material blend
    if (this.blend < 1) {
      this.blend = Math.min(1, this.blend + dt / 0.85);
      const e = smoothstep(this.blend);
      lerpMaterialSet(this.matCur, this.matFrom, this.matTo, e);
      this.lightCur = lerpLighting(this.lightFrom, this.lightTo, e);
    }

    // camera
    const j = this.journey.update(t);
    const isLedger = t > 0.885;
    const par = isLedger ? 4.2 : 1.05;
    this.mouse.x += (this.mouse.tx - this.mouse.x) * Math.min(1, dt * 3.2);
    this.mouse.y += (this.mouse.ty - this.mouse.y) * Math.min(1, dt * 3.2);

    const eye = [
      j.eye[0] + this.mouse.x * par,
      j.eye[1] - this.mouse.y * par * 0.55,
      j.eye[2] + (isLedger ? this.mouse.y * par * 0.7 : 0),
    ];
    const look = [
      j.look[0] - this.mouse.x * par * 0.35,
      j.look[1] + this.mouse.y * par * 0.22,
      j.look[2],
    ];

    // assembly
    this.assembly.apply(this.objData, t, { force: t > 0.86 ? smoothstep(clamp((t - 0.86) / 0.05, 0, 1)) : 0 });
    this.r.syncObjects();

    // grade + lighting
    const g = gradeFor(t, { sun: this.lightCur.sun });
    const L = this.lightCur;

    const lights = [];
    const lampOn = smoothstep(clamp((t - 0.14) / 0.12, 0, 1)) * (1 - smoothstep(clamp((t - 0.90) / 0.05, 0, 1)) * 0.75);
    for (const l of this.house.lights) {
      lights.push({ pos: l.pos, color: L.lamp, intensity: l.intensity * lampOn, range: l.range });
    }
    lights.sort((a, b) => {
      const da = (a.pos[0] - eye[0]) ** 2 + (a.pos[1] - eye[1]) ** 2 + (a.pos[2] - eye[2]) ** 2;
      const db = (b.pos[0] - eye[0]) ** 2 + (b.pos[1] - eye[1]) ** 2 + (b.pos[2] - eye[2]) ** 2;
      return da - db;
    });

    this.state = {
      eye, look, fov: j.fov, time: this.time,
      materials: this.matCur,
      sunDir: this.sunDir,
      sunColor: new Float32Array(L.sun),
      sunEnergy: L.sun_energy,
      skyColor: new Float32Array(L.sky),
      groundColor: new Float32Array(L.ground),
      ambient: g.ambient,
      lights: lights.slice(0, 12),
      shadowCenter: [23, 5, 17], shadowRadius: 34,
      floorY: 0.0,
      reflStrength: g.reflStrength,
      shadowStrength: g.shadowStrength,
      bloom: g.bloom, bloomThreshold: g.bloomThreshold, rayAmount: g.rayAmount,
      exposure: g.exposure, vignette: g.vignette, grain: g.grain,
      aberration: g.aberration, saturation: g.saturation, fade: g.fade,
      tint: new Float32Array(g.tint),
      xray: g.xray,
      moteAmount: g.moteAmount,
      moteColor: [L.sun[0], L.sun[1] * 0.92, L.sun[2] * 0.82],
    };
    this.r.render(this.state);
    this.updateChrome(t, j);
  }

  updateChrome(t, j) {
    const sec = j.section;
    const cap = CAPTIONS[sec.id] || CAPTIONS.threshold;
    const total = this.plan.journey.length;
    const idx = this.plan.journey.findIndex(w => w.id === sec.id) + 1;

    // real numbers for whatever room you are standing in
    let stats = [];
    const roomId = ROOM_FOR_SECTION[sec.id];
    if (roomId && this.est) {
      const r = this.est.rooms.find(x => x.id === roomId);
      if (r) {
        stats = [
          { n: r.q.floor_sqft.toLocaleString('en-US'), k: 'sq ft floor' },
          { n: Math.round(r.q.wall_sqft).toLocaleString('en-US'), k: 'sq ft wall' },
          { n: moneyShort(r.subtotal), k: 'this room' },
        ];
      }
    } else if (sec.id === 'ledger' || sec.id === 'close') {
      stats = [
        { n: Math.round(this.est.totals.sqft).toLocaleString('en-US'), k: 'sq ft' },
        { n: moneyShort(this.est.totals.grand), k: 'all in' },
        { n: money(this.est.totals.per_sqft), k: 'per sq ft' },
      ];
    } else if (sec.id === 'approach' || sec.id === 'threshold') {
      stats = [
        { n: this.r.triCount ? (this.r.triCount / 1000).toFixed(0) + 'k' : '—', k: 'triangles' },
        { n: this.house.objects.length, k: 'pieces' },
        { n: this.buildMs ? Math.round(this.buildMs) + 'ms' : '—', k: 'to draw it' },
      ];
    }

    this.ui.setCaption(idx, total, cap.title, cap.body, stats);
    this.ui.setProgress(t);
    this.ui.showRail(t > 0.185);
    this.ui.showHint(t < 0.03);

    // floating room tags at the dollhouse view
    const showTags = t > 0.895;
    this.ui.showTags(showTags);
    if (showTags && this.est) {
      const tags = this.est.rooms.map(r => {
        const room = this.plan.rooms.find(x => x.id === r.id);
        const c = [(room.x0 + room.x1) / 2, 1.2, (room.z0 + room.z1) / 2];
        const p = this.project(c);
        return {
          visible: p.visible, x: p.x, y: p.y,
          name: r.name, value: moneyShort(r.subtotal),
          sub: `${money(r.per_sqft)}/sf · ${r.q.floor_sqft} sf`,
        };
      });
      this.ui.setTags(tags);
    }
  }

  project(p) {
    const m = this.r._vp;
    const x = m[0] * p[0] + m[4] * p[1] + m[8] * p[2] + m[12];
    const y = m[1] * p[0] + m[5] * p[1] + m[9] * p[2] + m[13];
    const w = m[3] * p[0] + m[7] * p[1] + m[11] * p[2] + m[15];
    if (w <= 0.001) return { visible: false, x: 0, y: 0 };
    const sx = (x / w * 0.5 + 0.5) * this.vw;
    const sy = (1 - (y / w * 0.5 + 0.5)) * this.vh;
    return { visible: sx > -80 && sx < this.vw + 80 && sy > -40 && sy < this.vh + 40, x: sx, y: sy };
  }
}

new Atrium().start().catch(e => {
  console.error('[ATRIUM]', e);
  const b = document.getElementById('boot');
  if (b) document.getElementById('bootmsg').textContent = 'failed: ' + e.message;
});
