// ATRIUM — minimal linear algebra. No dependencies, column-major like GL.

export const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = (t) => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };
export const smootherstep = (t) => { t = clamp(t, 0, 1); return t * t * t * (t * (t * 6 - 15) + 10); };
export const invLerp = (a, b, v) => (b === a ? 0 : (v - a) / (b - a));
export const DEG = Math.PI / 180;

/* ---------- vec3 ---------- */
export const v3 = (x = 0, y = 0, z = 0) => new Float32Array([x, y, z]);
export const v3set = (o, x, y, z) => { o[0] = x; o[1] = y; o[2] = z; return o; };
export const v3copy = (o, a) => { o[0] = a[0]; o[1] = a[1]; o[2] = a[2]; return o; };
export const v3add = (o, a, b) => { o[0] = a[0] + b[0]; o[1] = a[1] + b[1]; o[2] = a[2] + b[2]; return o; };
export const v3sub = (o, a, b) => { o[0] = a[0] - b[0]; o[1] = a[1] - b[1]; o[2] = a[2] - b[2]; return o; };
export const v3scale = (o, a, s) => { o[0] = a[0] * s; o[1] = a[1] * s; o[2] = a[2] * s; return o; };
export const v3dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const v3len = (a) => Math.hypot(a[0], a[1], a[2]);
export function v3norm(o, a) {
  const l = Math.hypot(a[0], a[1], a[2]) || 1;
  o[0] = a[0] / l; o[1] = a[1] / l; o[2] = a[2] / l; return o;
}
export function v3cross(o, a, b) {
  const x = a[1] * b[2] - a[2] * b[1];
  const y = a[2] * b[0] - a[0] * b[2];
  const z = a[0] * b[1] - a[1] * b[0];
  o[0] = x; o[1] = y; o[2] = z; return o;
}
export function v3lerp(o, a, b, t) {
  o[0] = a[0] + (b[0] - a[0]) * t;
  o[1] = a[1] + (b[1] - a[1]) * t;
  o[2] = a[2] + (b[2] - a[2]) * t;
  return o;
}

/* ---------- mat4 (column-major) ---------- */
export const m4 = () => new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);

export function m4identity(o) {
  o.fill(0); o[0] = o[5] = o[10] = o[15] = 1; return o;
}

export function m4mul(o, a, b) {
  const a00=a[0],a01=a[1],a02=a[2],a03=a[3], a10=a[4],a11=a[5],a12=a[6],a13=a[7],
        a20=a[8],a21=a[9],a22=a[10],a23=a[11], a30=a[12],a31=a[13],a32=a[14],a33=a[15];
  for (let i = 0; i < 4; i++) {
    const b0=b[i*4], b1=b[i*4+1], b2=b[i*4+2], b3=b[i*4+3];
    o[i*4]   = b0*a00 + b1*a10 + b2*a20 + b3*a30;
    o[i*4+1] = b0*a01 + b1*a11 + b2*a21 + b3*a31;
    o[i*4+2] = b0*a02 + b1*a12 + b2*a22 + b3*a32;
    o[i*4+3] = b0*a03 + b1*a13 + b2*a23 + b3*a33;
  }
  return o;
}

export function m4perspective(o, fovy, aspect, near, far) {
  const f = 1 / Math.tan(fovy / 2);
  o.fill(0);
  o[0] = f / aspect; o[5] = f; o[11] = -1;
  o[10] = (far + near) / (near - far);
  o[14] = (2 * far * near) / (near - far);
  return o;
}

export function m4ortho(o, l, r, b, t, n, f) {
  o.fill(0);
  o[0] = 2 / (r - l); o[5] = 2 / (t - b); o[10] = -2 / (f - n);
  o[12] = -(r + l) / (r - l); o[13] = -(t + b) / (t - b); o[14] = -(f + n) / (f - n);
  o[15] = 1; return o;
}

const _x = v3(), _y = v3(), _z = v3();
export function m4lookAt(o, eye, target, up) {
  v3norm(_z, v3sub(_z, eye, target));
  if (v3len(_z) < 1e-6) _z[2] = 1;
  v3norm(_x, v3cross(_x, up, _z));
  if (v3len(_x) < 1e-6) { _x[0] = 1; _x[1] = 0; _x[2] = 0; }
  v3cross(_y, _z, _x);
  o[0]=_x[0]; o[1]=_y[0]; o[2]=_z[0]; o[3]=0;
  o[4]=_x[1]; o[5]=_y[1]; o[6]=_z[1]; o[7]=0;
  o[8]=_x[2]; o[9]=_y[2]; o[10]=_z[2]; o[11]=0;
  o[12]=-v3dot(_x, eye); o[13]=-v3dot(_y, eye); o[14]=-v3dot(_z, eye); o[15]=1;
  return o;
}

export function m4trs(o, tx, ty, tz, ry, sx, sy, sz) {
  const c = Math.cos(ry), s = Math.sin(ry);
  o[0] = c * sx;  o[1] = 0;   o[2] = -s * sx; o[3] = 0;
  o[4] = 0;       o[5] = sy;  o[6] = 0;       o[7] = 0;
  o[8] = s * sz;  o[9] = 0;   o[10] = c * sz; o[11] = 0;
  o[12] = tx;     o[13] = ty; o[14] = tz;     o[15] = 1;
  return o;
}

// Translate * Ry * Rx * Scale — enough to hang a round mirror on a wall or lay a
// handle on its side without a full quaternion stack.
export function m4trs2(o, tx, ty, tz, rx, ry, sx, sy, sz) {
  const cx = Math.cos(rx), sxr = Math.sin(rx);
  const cy = Math.cos(ry), syr = Math.sin(ry);
  o[0] = cy * sx;          o[1] = 0;          o[2] = -syr * sx;       o[3] = 0;
  o[4] = syr * sxr * sy;   o[5] = cx * sy;    o[6] = cy * sxr * sy;   o[7] = 0;
  o[8] = syr * cx * sz;    o[9] = -sxr * sz;  o[10] = cy * cx * sz;   o[11] = 0;
  o[12] = tx;              o[13] = ty;        o[14] = tz;             o[15] = 1;
  return o;
}

// Inverse-transpose of the upper 3x3, written into a mat3 (9 floats).
export function normalMat3(o, m) {
  const a00=m[0],a01=m[1],a02=m[2], a10=m[4],a11=m[5],a12=m[6], a20=m[8],a21=m[9],a22=m[10];
  const b01 =  a22*a11 - a12*a21, b11 = -a22*a10 + a12*a20, b21 =  a21*a10 - a11*a20;
  let det = a00*b01 + a01*b11 + a02*b21;
  if (!det) { o.set([1,0,0, 0,1,0, 0,0,1]); return o; }
  det = 1 / det;
  o[0] = b01*det;                     o[1] = (-a22*a01 + a02*a21)*det;  o[2] = ( a12*a01 - a02*a11)*det;
  o[3] = b11*det;                     o[4] = ( a22*a00 - a02*a20)*det;  o[5] = (-a12*a00 + a02*a10)*det;
  o[6] = b21*det;                     o[7] = (-a21*a00 + a01*a20)*det;  o[8] = ( a11*a00 - a01*a10)*det;
  return o;
}

export function m4invert(o, m) {
  const a00=m[0],a01=m[1],a02=m[2],a03=m[3], a10=m[4],a11=m[5],a12=m[6],a13=m[7],
        a20=m[8],a21=m[9],a22=m[10],a23=m[11], a30=m[12],a31=m[13],a32=m[14],a33=m[15];
  const b00=a00*a11-a01*a10, b01=a00*a12-a02*a10, b02=a00*a13-a03*a10,
        b03=a01*a12-a02*a11, b04=a01*a13-a03*a11, b05=a02*a13-a03*a12,
        b06=a20*a31-a21*a30, b07=a20*a32-a22*a30, b08=a20*a33-a23*a30,
        b09=a21*a32-a22*a31, b10=a21*a33-a23*a31, b11=a22*a33-a23*a32;
  let det = b00*b11 - b01*b10 + b02*b09 + b03*b08 - b04*b07 + b05*b06;
  if (!det) return m4identity(o);
  det = 1 / det;
  o[0]=(a11*b11-a12*b10+a13*b09)*det;  o[1]=(a02*b10-a01*b11-a03*b09)*det;
  o[2]=(a31*b05-a32*b04+a33*b03)*det;  o[3]=(a22*b04-a21*b05-a23*b03)*det;
  o[4]=(a12*b08-a10*b11-a13*b07)*det;  o[5]=(a00*b11-a02*b08+a03*b07)*det;
  o[6]=(a32*b02-a30*b05-a33*b01)*det;  o[7]=(a20*b05-a22*b02+a23*b01)*det;
  o[8]=(a10*b10-a11*b08+a13*b06)*det;  o[9]=(a01*b08-a00*b10-a03*b06)*det;
  o[10]=(a30*b04-a31*b02+a33*b00)*det; o[11]=(a21*b02-a20*b04-a23*b00)*det;
  o[12]=(a11*b07-a10*b09-a12*b06)*det; o[13]=(a00*b09-a01*b07+a02*b06)*det;
  o[14]=(a31*b01-a30*b03-a32*b00)*det; o[15]=(a20*b03-a21*b01+a22*b00)*det;
  return o;
}

// Mirror a point/direction across the plane y = h (used for the floor reflection pass).
export function mirrorY(o, a, h) { o[0] = a[0]; o[1] = 2 * h - a[1]; o[2] = a[2]; return o; }

/* ---------- Catmull-Rom through the journey waypoints ---------- */
export function catmull(p0, p1, p2, p3, t) {
  const t2 = t * t, t3 = t2 * t;
  return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3);
}

export function catmullV3(out, pts, i, t) {
  const n = pts.length;
  const a = pts[clamp(i - 1, 0, n - 1)], b = pts[clamp(i, 0, n - 1)];
  const c = pts[clamp(i + 1, 0, n - 1)], d = pts[clamp(i + 2, 0, n - 1)];
  out[0] = catmull(a[0], b[0], c[0], d[0], t);
  out[1] = catmull(a[1], b[1], c[1], d[1], t);
  out[2] = catmull(a[2], b[2], c[2], d[2], t);
  return out;
}

/* ---------- deterministic noise (no Math.random anywhere in the render path) ---------- */
export function hash1(n) {
  const s = Math.sin(n * 127.1) * 43758.5453123;
  return s - Math.floor(s);
}
export function hash3(n) {
  return [hash1(n), hash1(n + 17.13), hash1(n + 91.7)];
}
