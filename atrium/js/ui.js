// ATRIUM — the interface. Reads the same catalog the renderer and the estimate do.

import { money, moneyShort } from './pricing.js';

const $ = (id) => document.getElementById(id);
const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html !== undefined) n.innerHTML = html;
  return n;
};

const srgb = (c) => {
  // linear albedo → a hex chip that looks like the material
  const f = (v) => {
    const s = v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(Math.max(v, 0), 1 / 2.4) - 0.055;
    return Math.round(Math.min(1, Math.max(0, s)) * 255).toString(16).padStart(2, '0');
  };
  return `#${f(c[0])}${f(c[1])}${f(c[2])}`;
};

const GROUPS = [
  { key: 'floor', label: 'Floor', unit: '/sq ft' },
  { key: 'wall', label: 'Walls & ceiling', unit: '/sq ft' },
  { key: 'counter', label: 'Countertops', unit: '/lin ft' },
  { key: 'cabinet', label: 'Cabinetry', unit: '/lin ft' },
  { key: 'metal', label: 'Metal finish', unit: 'uplift' },
  { key: 'textile', label: 'Upholstery', unit: 'uplift' },
];

export class UI {
  constructor(catalog, plan, handlers) {
    this.catalog = catalog;
    this.plan = plan;
    this.on = handlers;
    this.captionState = '';
    this.build();
  }

  build() {
    /* ---- palette rail ---- */
    const rail = $('rail');
    rail.innerHTML = '';
    this.swatches = this.catalog.palettes.map((p) => {
      const btn = el('button', 'swatch');
      const wall = this.catalog.surfaces.wall.find(x => x.id === p.wall);
      const floor = this.catalog.surfaces.floor.find(x => x.id === p.floor);
      const metal = this.catalog.surfaces.metal.find(x => x.id === p.metal);
      btn.innerHTML =
        `<span class="nm">${p.name}</span>` +
        `<span class="dot" style="background:conic-gradient(${srgb(wall.albedo)} 0deg 130deg,` +
        `${srgb(floor.albedo)} 130deg 260deg,${srgb(metal.albedo)} 260deg 360deg)"></span>`;
      btn.title = p.line;
      btn.addEventListener('click', () => this.on.palette(p.id));
      rail.appendChild(btn);
      return { id: p.id, btn };
    });

    /* ---- surface drawer ---- */
    const groups = $('groups');
    groups.innerHTML = '';
    this.optButtons = {};
    for (const g of GROUPS) {
      const wrap = el('div', 'group');
      const rate = el('h4', null, `${g.label}<em id="rate-${g.key}"></em>`);
      wrap.appendChild(rate);
      const opts = el('div', 'opts');
      this.optButtons[g.key] = [];
      for (const m of this.catalog.surfaces[g.key]) {
        const btn = el('button', 'opt');
        const price = m.unit === 'pct'
          ? (m.cost === 0 ? 'included' : `+${Math.round(m.cost * 100)}%`)
          : `${money(m.cost, m.cost < 100 ? 2 : 0)}/${m.unit === 'sqft' ? 'sf' : 'lf'}`;
        btn.innerHTML =
          `<span class="chip" style="background:${srgb(m.albedo)}"></span>` +
          `<span class="t">${m.name}</span><span class="p">${price}</span>`;
        btn.addEventListener('click', () => this.on.surface(g.key, m.id));
        opts.appendChild(btn);
        this.optButtons[g.key].push({ id: m.id, btn });
      }
      wrap.appendChild(opts);
      groups.appendChild(wrap);
    }
    $('drawernote').textContent = this.catalog.meta.basis;
    $('foot-basis').textContent = 'Estimate basis: ' + this.catalog.meta.basis.split('.')[0].trim() + '.';

    $('surfbtn').addEventListener('click', () => this.toggleDrawer(true));
    $('drawerclose').addEventListener('click', () => this.toggleDrawer(false));
    $('totalchip').addEventListener('click', () => this.toggleLedger(true));
    $('ledgerclose').addEventListener('click', () => this.toggleLedger(false));

    /* ---- tiers ---- */
    const tiers = $('tiers');
    tiers.innerHTML = '';
    this.catalog.plans.forEach((p, i) => {
      const card = el('div', 'tier' + (i === 1 ? ' feat' : ''));
      card.innerHTML =
        `<h3>${p.name}</h3>` +
        `<span class="line">${p.line}</span>` +
        `<div class="price"><span class="n">$${p.price}</span><span class="c">/ ${p.cadence}</span></div>` +
        `<ul>${p.features.map(f => `<li>${f}</li>`).join('')}</ul>`;
      const cta = el('a', 'btn cta' + (i === 1 ? ' solid' : ''), `Start ${p.name}`);
      cta.href = '#';
      cta.dataset.plan = p.id;
      cta.addEventListener('click', (e) => { e.preventDefault(); this.on.subscribe(p.id); });
      card.appendChild(cta);
      tiers.appendChild(card);
    });

    $('lg-spec').addEventListener('click', () => this.on.exportSpec());
    $('lg-print').addEventListener('click', () => window.print());

    $('plate-sqft').textContent = this.plan.rooms
      .filter(r => r.priced)
      .reduce((s, r) => s + (r.x1 - r.x0) * (r.z1 - r.z0), 0)
      .toLocaleString('en-US');
  }

  toggleDrawer(open) {
    $('drawer').classList.toggle('open', open);
    if (open) $('ledger').classList.remove('open');
  }
  toggleLedger(open) {
    $('ledger').classList.toggle('open', open);
    if (open) $('drawer').classList.remove('open');
  }

  setAccent(hex) {
    document.documentElement.style.setProperty('--accent', hex);
  }

  setPalette(id, sel) {
    for (const s of this.swatches) s.btn.classList.toggle('on', s.id === id);
    const p = this.catalog.palettes.find(x => x.id === id);
    $('plate-pal').textContent = p ? p.name : 'Custom';
    this.setSelection(sel);
  }

  setSelection(sel) {
    for (const g of GROUPS) {
      for (const o of this.optButtons[g.key]) o.btn.classList.toggle('on', o.id === sel[g.key]);
      const m = this.catalog.surfaces[g.key].find(x => x.id === sel[g.key]);
      const r = $(`rate-${g.key}`);
      if (r && m) {
        r.textContent = m.unit === 'pct'
          ? (m.cost === 0 ? '—' : `+${Math.round(m.cost * 100)}%`)
          : `${money(m.cost, m.cost < 100 ? 2 : 0)}${g.unit}`;
      }
    }
  }

  markCustom() { for (const s of this.swatches) s.btn.classList.remove('on'); $('plate-pal').textContent = 'Custom'; }

  /* ---------------------------------------------------------- estimate */
  setEstimate(est) {
    $('totalval').textContent = moneyShort(est.totals.grand);
    $('lg-grand').textContent = money(est.totals.grand);
    $('lg-sub').textContent =
      `${Math.round(est.totals.sqft).toLocaleString('en-US')} sq ft  ·  ${money(est.totals.per_sqft)} per sq ft`;

    const rooms = $('lg-rooms');
    const openIds = new Set(Array.from(rooms.querySelectorAll('details[open]')).map(d => d.dataset.id));
    rooms.innerHTML = '';
    for (const r of est.rooms) {
      const d = el('details', 'lroom');
      d.dataset.id = r.id;
      if (openIds.has(r.id)) d.open = true;
      const q = r.q;
      d.innerHTML =
        `<summary><span><span class="rn">${r.name}</span>` +
        `<div class="rq">${q.floor_sqft.toLocaleString('en-US')} sq ft floor · ${Math.round(q.wall_sqft).toLocaleString('en-US')} sq ft wall` +
        `${q.counter_lf ? ` · ${q.counter_lf} lf counter` : ''}</div></span>` +
        `<span class="rv">${money(r.subtotal)}</span></summary>`;
      const lines = el('div', 'lines');
      for (const L of r.lines) {
        lines.appendChild(el('div', 'line',
          `<span>${L.label}</span><span class="q">${L.qty} ${L.unit} × ${money(L.rate, L.rate < 100 ? 2 : 0)}</span>` +
          `<span class="a">${money(L.amount)}</span>`));
      }
      d.appendChild(lines);
      rooms.appendChild(d);
    }

    const t = est.totals;
    $('lg-totals').innerHTML =
      `<div class="lrow hd"><span class="k">Materials</span><span class="v">${money(t.materials)}</span></div>` +
      `<div class="lrow"><span class="k">Labor, installed</span><span class="v">${money(t.labor)}</span></div>` +
      `<div class="lrow"><span class="k">Fixtures & furnishing</span><span class="v">${money(t.fixtures)}</span></div>` +
      `<div class="lrow"><span class="k">Design fee (${Math.round(this.catalog.fees.design_pct * 100)}%)</span><span class="v">${money(t.design)}</span></div>` +
      `<div class="lrow"><span class="k">Contingency held (${Math.round(this.catalog.fees.contingency_pct * 100)}%)</span><span class="v">${money(t.contingency)}</span></div>`;

    $('lg-note').textContent =
      this.catalog.labor.note + ' ' + this.catalog.meta.basis;
  }

  /* ---------------------------------------------------------- caption */
  setCaption(idx, total, title, body, stats) {
    const key = title + body;
    const cap = $('caption');
    if (key === this.captionState) {
      this.updateStats(stats);
      return;
    }
    this.captionState = key;
    cap.classList.add('out');
    clearTimeout(this._capT);
    this._capT = setTimeout(() => {
      $('cap-idx').textContent = `${String(idx).padStart(2, '0')} / ${String(total).padStart(2, '0')}`;
      $('cap-title').textContent = title;
      $('cap-body').textContent = body;
      this.updateStats(stats);
      cap.classList.remove('out');
    }, 260);
  }

  updateStats(stats) {
    const box = $('cap-stats');
    if (!stats || !stats.length) { box.innerHTML = ''; return; }
    box.innerHTML = stats.map(s => `<div><div class="n">${s.n}</div><div class="k">${s.k}</div></div>`).join('');
  }

  setProgress(t) {
    $('progfill').style.width = (t * 100).toFixed(1) + '%';
    $('progpct').textContent = Math.round(t * 100) + '%';
  }

  showRail(v) { $('rail').classList.toggle('hidden', !v); $('surfbtn').classList.toggle('hidden', !v); }
  showHint(v) { $('hint').style.opacity = v ? '1' : '0'; }
  showTags(v) { $('tags').classList.toggle('on', v); }

  setTags(list) {
    const box = $('tags');
    if (!list) { box.innerHTML = ''; return; }
    if (box.children.length !== list.length) {
      box.innerHTML = list.map(() => `<div class="tag"><div class="tn"></div><div class="tv"></div><div class="ts"></div></div>`).join('');
    }
    list.forEach((t, i) => {
      const n = box.children[i];
      if (!n) return;
      if (t.visible) {
        n.style.display = '';
        n.style.left = t.x + 'px';
        n.style.top = t.y + 'px';
        n.children[0].textContent = t.name;
        n.children[1].textContent = t.value;
        n.children[2].textContent = t.sub;
      } else {
        n.style.display = 'none';
      }
    });
  }

  boot(p, msg) {
    const b = document.getElementById('bootbar');
    if (b) b.style.right = (100 - p * 100) + '%';
    if (msg) document.getElementById('bootmsg').textContent = msg;
  }
  bootDone() {
    const b = document.getElementById('boot');
    b.classList.add('gone');
    setTimeout(() => b.remove(), 1000);
  }
}

export { srgb };
