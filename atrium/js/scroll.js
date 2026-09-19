// ATRIUM — the journey. Scroll drives a camera spline; the house assembles
// itself room by room just ahead of where you are looking.

import { v3, catmullV3, clamp, lerp, smootherstep, smoothstep, invLerp } from './math.js';

export class Journey {
  constructor(plan) {
    this.wp = plan.journey;
    this.eyes = this.wp.map(w => w.eye);
    this.looks = this.wp.map(w => w.look);
    this.eye = v3();
    this.look = v3();
    this.fov = 50;
    this.section = this.wp[0];
    this.sectionIndex = 0;
    this.sectionT = 0;
  }

  update(t) {
    const wp = this.wp;
    t = clamp(t, 0, 1);
    let i = 0;
    while (i < wp.length - 2 && t > wp[i + 1].at) i++;
    const u = clamp(invLerp(wp[i].at, wp[i + 1].at, t), 0, 1);
    const e = smootherstep(u);

    catmullV3(this.eye, this.eyes, i, e);
    catmullV3(this.look, this.looks, i, e);
    this.fov = lerp(wp[i].fov, wp[i + 1].fov, e);
    this.sectionIndex = i;
    this.sectionT = u;
    this.section = u < 0.5 ? wp[i] : wp[i + 1];
    this.from = wp[i];
    this.to = wp[i + 1];
    return this;
  }
}

/* Which scroll position each object arrives at. Rooms build just before you
   get there, so you always scroll into a room that is finishing itself. */
const ROOM_ARRIVAL = {
  entry: 0.150,
  hall: 0.190,
  living: 0.240,
  kitchen: 0.450,
  bath: 0.650,
  closet: 0.690,
  bedroom: 0.760,
};

const STRUCTURE_ARRIVAL = {
  floor: 0.030,
  // the lid goes on last, and only once you have dropped to door height —
  // otherwise it hides the very thing the opening is showing you
  ceiling: 0.152,
  glazing: 0.128,
};

export class Assembly {
  constructor(objects) {
    this.objects = objects;
    this.schedule = new Float32Array(objects.length * 2); // [start, duration]
    let structIdx = 0;
    const roomCount = {};

    for (const o of objects) {
      let start, dur;
      if (o.structural) {
        if (STRUCTURE_ARRIVAL[o.name] !== undefined) {
          start = STRUCTURE_ARRIVAL[o.name];
          dur = 0.055;
        } else {
          start = 0.045 + structIdx * 0.0075;   // walls rise one after another
          dur = 0.05;
          structIdx++;
        }
      } else {
        const base = ROOM_ARRIVAL[o.room] !== undefined ? ROOM_ARRIVAL[o.room] : 0.25;
        const n = roomCount[o.room] = (roomCount[o.room] || 0) + 1;
        start = base + (n - 1) * 0.0085;
        dur = 0.052;
      }
      this.schedule[o.id * 2] = start;
      this.schedule[o.id * 2 + 1] = dur;
    }
    this.maxStart = Math.max(...Array.from({ length: objects.length }, (_, i) => this.schedule[i * 2] + this.schedule[i * 2 + 1]));
  }

  /** Write reveal/offset/sway into the renderer's 256×RGBA object texture. */
  apply(objData, t, opts = {}) {
    const force = opts.force || 0;
    const objs = this.objects;
    let arriving = 0;
    for (let k = 0; k < objs.length; k++) {
      const o = objs[k];
      const s = this.schedule[k * 2], d = this.schedule[k * 2 + 1];
      let r = clamp((t - s) / d, 0, 1);
      if (force > 0) r = Math.max(r, force);
      const rev = smoothstep(r);
      const i4 = o.id * 4;
      objData[i4] = rev;
      // how far it sits below (or above) its resting place while arriving:
      // the ceiling and the pendants come down, everything else rises from the slab
      objData[i4 + 1] = o.name === 'ceiling' ? 7.0
        : o.structural ? 0.0
        : (o.name.startsWith('pendant') ? 2.6 : -2.2);
      // soft goods and foliage breathe a little once placed
      objData[i4 + 2] = (o.name.startsWith('plant') ? 1.0 : 0.0) * rev;
      objData[i4 + 3] = 0;
      if (rev > 0.02 && rev < 0.98) arriving++;
    }
    this.arriving = arriving;
    return arriving;
  }
}

/* The grade changes as you move through the house — this is the film, not the set. */
export function gradeFor(t, palette) {
  const g = {
    exposure: 0.92,
    bloom: 0.34,
    rayAmount: 0.55,
    bloomThreshold: 1.25,
    vignette: 0.62,
    grain: 0.028,
    aberration: 0.009,
    saturation: 1.04,
    fade: 1.0,
    ambient: 0.40,
    moteAmount: 0.45,
    shadowStrength: 0.92,
    reflStrength: 0.55,
    xray: 0.0,
    tint: [1, 1, 1],
  };

  // opening: near-black, one shaft of light, then the world resolves
  const open = smoothstep(clamp(invLerp(0.008, 0.075, t), 0, 1));
  g.fade = 0.06 + open * 0.94;
  g.exposure = lerp(0.66, 0.92, open);
  g.vignette = lerp(0.95, 0.62, open);
  g.bloom = lerp(0.85, 0.34, open);
  g.grain = lerp(0.055, 0.028, open);

  // while the house is building, the edges glow
  const build = smoothstep(clamp(invLerp(0.03, 0.10, t), 0, 1)) * (1 - smoothstep(clamp(invLerp(0.72, 0.86, t), 0, 1)));
  g.xray = build * 0.85;

  // interiors: warmer, softer, more dust in the light
  const inside = smoothstep(clamp(invLerp(0.16, 0.26, t), 0, 1)) * (1 - smoothstep(clamp(invLerp(0.88, 0.94, t), 0, 1)));
  g.ambient = lerp(0.40, 0.52, inside);
  g.moteAmount = lerp(0.20, 0.80, inside);
  g.rayAmount = lerp(0.55, 0.85, inside);

  // the ledger: pull up, cool off, let the numbers read
  const led = smoothstep(clamp(invLerp(0.88, 0.955, t), 0, 1));
  g.exposure = lerp(g.exposure, 1.02, led);
  g.saturation = lerp(g.saturation, 0.92, led);
  g.vignette = lerp(g.vignette, 0.44, led);
  g.ambient = lerp(g.ambient, 0.78, led);
  g.grain = lerp(g.grain, 0.018, led);
  g.moteAmount = lerp(g.moteAmount, 0.12, led);
  g.reflStrength = lerp(g.reflStrength, 0.30, led);
  g.aberration = lerp(g.aberration, 0.012, led);

  if (palette && palette.sun) {
    g.tint = [
      lerp(1.0, 0.5 + palette.sun[0] * 0.55, 0.35),
      lerp(1.0, 0.5 + palette.sun[1] * 0.55, 0.35),
      lerp(1.0, 0.5 + palette.sun[2] * 0.55, 0.35),
    ];
  }
  return g;
}
