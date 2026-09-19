// ATRIUM — all GLSL. WebGL2 / GLSL ES 3.00.

export const MAT = {
  FLOOR: 0, WALL: 1, CEILING: 2, COUNTER: 3, CABINET: 4, METAL: 5,
  TEXTILE_A: 6, TEXTILE_B: 7, WOOD: 8, STONE: 9, GLASS: 10, PLANT: 11,
  EMISSIVE: 12, DARK: 13, ART: 14, TRIM: 15,
};
export const NMAT = 16;
export const MAXLIGHTS = 12;

/* Shared noise + detail library, injected into fragment shaders that need it. */
const NOISE = `
float h21(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
float vnoise(vec2 p){
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(h21(i), h21(i + vec2(1,0)), f.x),
             mix(h21(i + vec2(0,1)), h21(i + vec2(1,1)), f.x), f.y);
}
float fbm(vec2 p){
  float a = 0.5, s = 0.0;
  for (int i = 0; i < 5; i++){ s += a * vnoise(p); p = p * 2.03 + 17.0; a *= 0.5; }
  return s;
}
float ridge(vec2 p){ return 1.0 - abs(fbm(p) * 2.0 - 1.0); }
`;

/* ============================================================ MAIN SCENE */
export const SCENE_VS = `#version 300 es
precision highp float;
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNrm;
layout(location=2) in vec2 aUV;
layout(location=3) in float aObj;
layout(location=4) in float aMat;
layout(location=5) in vec3 aPivot;
layout(location=6) in float aAO;

uniform mat4 uViewProj;
uniform mat4 uLightVP;
uniform sampler2D uObjTex;
uniform float uTime;

out vec3 vPos;
out vec3 vNrm;
out vec2 vUV;
flat out int vMat;
out vec4 vLightPos;
out float vAO;
out float vReveal;

void main(){
  vec4 od = texelFetch(uObjTex, ivec2(int(aObj + 0.5), 0), 0);
  float rev = clamp(od.r, 0.0, 1.0);
  float e = rev * rev * (3.0 - 2.0 * rev);

  vec3 p = mix(aPivot, aPos, e);
  p.y += (1.0 - e) * od.g;

  // gentle life: a breath on soft goods, a sway on foliage
  float sway = od.b;
  if (sway > 0.001) {
    float h = max(0.0, aPos.y - aPivot.y);
    p.x += sin(uTime * 0.9 + aPivot.x * 2.1) * sway * h * 0.02;
    p.z += cos(uTime * 0.7 + aPivot.z * 1.7) * sway * h * 0.018;
  }

  vPos = p;
  vNrm = normalize(aNrm);
  vUV = aUV;
  vMat = int(aMat + 0.5);
  vAO = aAO;
  vReveal = rev;
  vLightPos = uLightVP * vec4(p, 1.0);
  gl_Position = uViewProj * vec4(p, 1.0);
}`;

export const SCENE_FS = `#version 300 es
precision highp float;
precision highp sampler2D;

in vec3 vPos;
in vec3 vNrm;
in vec2 vUV;
flat in int vMat;
in vec4 vLightPos;
in float vAO;
in float vReveal;

layout(location=0) out vec4 oColor;

uniform vec3 uEye;
uniform vec3 uAlbedo[${NMAT}];
uniform float uRough[${NMAT}];
uniform float uMetal[${NMAT}];
uniform vec3 uEmissive[${NMAT}];
uniform int uFamily[${NMAT}];
uniform float uDetail[${NMAT}];

uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform float uSunEnergy;
uniform vec3 uSkyColor;
uniform vec3 uGroundColor;
uniform float uAmbient;

uniform int uNumLights;
uniform vec3 uLightPos[${MAXLIGHTS}];
uniform vec3 uLightColor[${MAXLIGHTS}];
uniform float uLightRange[${MAXLIGHTS}];

uniform sampler2D uShadow;
uniform vec2 uShadowTexel;
uniform float uShadowStrength;

uniform sampler2D uRefl;
uniform vec2 uResolution;
uniform float uReflStrength;
uniform int uReflectionPass;
uniform float uClipY;

uniform float uTime;
uniform float uXray;      // 0 = solid, 1 = assembling wireframe glow

${NOISE}

/* ---- procedural surface detail: returns a height field, tweaks albedo/rough ---- */
float detailField(int fam, vec2 uv, inout vec3 alb, inout float rough){
  float h = 0.0;
  if (fam == 1) {                                   // wood
    float grain = fbm(vec2(uv.x * 0.9, uv.y * 0.18));
    float rings = sin((uv.y * 0.6 + grain * 2.2) * 1.7) * 0.5 + 0.5;
    float fine = fbm(vec2(uv.x * 3.0, uv.y * 7.0));
    float plank = abs(fract(uv.x / 0.75) - 0.5);
    float seam = 1.0 - smoothstep(0.462, 0.5, plank);
    alb *= mix(0.86, 1.09, rings * 0.6 + fine * 0.4);
    alb *= mix(0.62, 1.0, seam);
    rough = clamp(rough + (rings - 0.5) * 0.05, 0.03, 1.0);
    h = rings * 0.3 + fine * 0.15 - (1.0 - seam) * 1.1;
  } else if (fam == 2) {                            // stone / marble
    vec2 q = uv * 0.55;
    float warp = fbm(q * 1.4);
    float vein = ridge(q * vec2(0.7, 2.2) + warp * 1.8);
    vein = pow(clamp(vein, 0.0, 1.0), 3.0);
    float speck = fbm(uv * 9.0);
    alb *= mix(1.0, 0.62, vein * 0.9);
    alb *= 0.94 + speck * 0.12;
    rough = clamp(rough + vein * 0.08 - 0.02, 0.02, 1.0);
    h = vein * 0.5 + speck * 0.15;
  } else if (fam == 3) {                            // plaster / limewash
    float m = fbm(uv * 0.9) * 0.62 + fbm(uv * 3.0) * 0.28 + fbm(uv * 8.0) * 0.10;
    alb *= 0.93 + m * 0.14;
    rough = clamp(rough - m * 0.05, 0.2, 1.0);
    h = m * 0.8;
  } else if (fam == 4) {                            // textile — cloth, not gingham
    float slub = fbm(uv * 14.0);
    float fibre = fbm(vec2(uv.x * 60.0, uv.y * 22.0));
    alb *= 0.955 + slub * 0.075 + fibre * 0.035;
    rough = clamp(rough + (slub - 0.5) * 0.05, 0.3, 1.0);
    h = slub * 0.55 + fibre * 0.25;
  } else if (fam == 5) {                            // tile
    vec2 g = abs(fract(uv / 1.0) - 0.5);
    float grout = 1.0 - smoothstep(0.44, 0.49, max(g.x, g.y));
    float tone = h21(floor(uv / 1.0));
    alb *= mix(0.42, 1.0, grout) * (0.88 + tone * 0.22);
    rough = clamp(rough + (1.0 - grout) * 0.35, 0.05, 1.0);
    h = grout * 0.9;
  } else if (fam == 6) {                            // brushed metal
    float streak = fbm(vec2(uv.x * 18.0, uv.y * 1.2));
    alb *= 0.95 + streak * 0.10;
    rough = clamp(rough + (streak - 0.5) * 0.08, 0.02, 1.0);
    h = streak * 0.2;
  } else if (fam == 7) {                            // foliage
    float leaf = fbm(uv * 3.5);
    float vein2 = abs(sin(uv.y * 9.0 + leaf * 5.0));
    alb *= 0.78 + leaf * 0.40;
    alb *= 0.92 + vein2 * 0.12;
    rough = clamp(rough - leaf * 0.12, 0.15, 1.0);
    h = leaf * 0.5 + vein2 * 0.18;
  } else if (fam == 8) {                            // canvas / art
    float f = fbm(uv * 3.0 + 4.0);
    float g2 = fbm(uv * 1.1 + 19.0);
    alb = mix(alb, alb.bgr * 1.15, smoothstep(0.45, 0.75, g2));
    alb *= 0.80 + f * 0.4;
    h = f * 0.3;
  }
  return h;
}

/* ---- GGX ---- */
float D_GGX(float NoH, float a){
  float a2 = a * a;
  float d = NoH * NoH * (a2 - 1.0) + 1.0;
  return a2 / max(3.14159265 * d * d, 1e-7);
}
float V_Smith(float NoV, float NoL, float a){
  float a2 = a * a;
  float gv = NoL * sqrt(NoV * NoV * (1.0 - a2) + a2);
  float gl = NoV * sqrt(NoL * NoL * (1.0 - a2) + a2);
  return 0.5 / max(gv + gl, 1e-6);
}
vec3 F_Schlick(vec3 f0, float u){ return f0 + (1.0 - f0) * pow(1.0 - u, 5.0); }

vec3 brdf(vec3 N, vec3 V, vec3 L, vec3 alb, float rough, float metal, out float NoL){
  vec3 H = normalize(V + L);
  NoL = max(dot(N, L), 0.0);
  float NoV = max(dot(N, V), 1e-4);
  float NoH = max(dot(N, H), 0.0);
  float VoH = max(dot(V, H), 0.0);
  float a = max(rough * rough, 0.002);
  vec3 f0 = mix(vec3(0.045), alb, metal);
  vec3 F = F_Schlick(f0, VoH);
  vec3 spec = F * (D_GGX(NoH, a) * V_Smith(NoV, NoL, a));
  vec3 kd = (1.0 - F) * (1.0 - metal);
  return (kd * alb / 3.14159265 + spec) * NoL;
}

float shadowFactor(vec3 N, vec3 L){
  vec3 pc = vLightPos.xyz / vLightPos.w;
  pc = pc * 0.5 + 0.5;
  if (pc.z > 1.0 || pc.x < 0.001 || pc.x > 0.999 || pc.z < 0.0 || pc.y < 0.001 || pc.y > 0.999) return 1.0;
  float bias = max(0.0016 * (1.0 - dot(N, L)), 0.0006);
  float sum = 0.0;
  for (int y = -1; y <= 1; y++){
    for (int x = -1; x <= 1; x++){
      float d = texture(uShadow, pc.xy + vec2(float(x), float(y)) * uShadowTexel * 1.35).r;
      sum += (pc.z - bias > d) ? 0.0 : 1.0;
    }
  }
  return sum / 9.0;
}

/* 4x4 ordered dither — lets one opaque pass fake glass without sorting. */
float bayer(vec2 fc){
  int x = int(mod(fc.x, 4.0)), y = int(mod(fc.y, 4.0));
  int i = y * 4 + x;
  float t[16] = float[16](0.0,8.0,2.0,10.0, 12.0,4.0,14.0,6.0, 3.0,11.0,1.0,9.0, 15.0,7.0,13.0,5.0);
  return t[i] / 16.0;
}

void main(){
  if (vReveal < 0.004) discard;
  if (uReflectionPass == 1 && vPos.y < uClipY - 0.02) discard;

  int m = clamp(vMat, 0, ${NMAT - 1});
  if (m == ${MAT.GLASS}) {
    // keep the grazing edges and the sun glint, drop most of the face
    float g = 1.0 - abs(dot(normalize(vNrm), normalize(uEye - vPos)));
    float keep = 0.10 + pow(g, 3.0) * 0.75;
    if (bayer(gl_FragCoord.xy) > keep) discard;
  }
  vec3 alb = uAlbedo[m];
  float rough = uRough[m];
  float metal = uMetal[m];
  int fam = uFamily[m];

  vec3 N = normalize(vNrm);
  vec3 V = normalize(uEye - vPos);

  float h = 0.0;
  if (fam > 0) h = detailField(fam, vUV, alb, rough);

  // surface-gradient bump from the detail height field
  float bump = uDetail[m];
  if (bump > 0.001) {
    vec3 dpx = dFdx(vPos), dpy = dFdy(vPos);
    float dhx = dFdx(h), dhy = dFdy(h);
    vec3 r1 = cross(dpy, N), r2 = cross(N, dpx);
    float det = dot(dpx, r1);
    vec3 grad = (abs(det) < 1e-8) ? vec3(0.0) : (dhx * r1 + dhy * r2) / det;
    N = normalize(N - grad * bump);
  }

  float ao = vAO;

  // ---------------- direct: sun
  vec3 L = normalize(-uSunDir);
  float NoL;
  vec3 direct = brdf(N, V, L, alb, rough, metal, NoL) * uSunColor * uSunEnergy;
  float sh = mix(1.0, shadowFactor(N, L), uShadowStrength);
  direct *= sh;

  // ---------------- direct: lamps
  for (int i = 0; i < ${MAXLIGHTS}; i++){
    if (i >= uNumLights) break;
    vec3 dv = uLightPos[i] - vPos;
    float dist = length(dv);
    if (dist > uLightRange[i]) continue;
    vec3 Ld = dv / max(dist, 1e-4);
    float att = clamp(1.0 - dist / uLightRange[i], 0.0, 1.0);
    att = att * att / (1.0 + dist * dist * 0.05);
    float nl;
    direct += brdf(N, V, Ld, alb, rough, metal, nl) * uLightColor[i] * att * 14.0;
  }

  // ---------------- ambient: hemisphere, occluded
  float upn = N.y * 0.5 + 0.5;
  vec3 sky = mix(uGroundColor, uSkyColor, upn);
  // bounced light is never as saturated as the sky it came from
  vec3 diffSky = mix(vec3(dot(sky, vec3(0.2126, 0.7152, 0.0722))), sky, 0.58);
  float NoV = max(dot(N, V), 1e-4);
  vec3 f0 = mix(vec3(0.045), alb, metal);
  vec3 Fr = F_Schlick(f0, NoV) * (1.0 - rough * 0.85);

  // a cheap analytic environment — without it every metal and mirror reads as a dark hole
  vec3 R = reflect(-V, N);
  vec3 env = mix(uGroundColor * 0.8, uSkyColor, smoothstep(0.28, 0.74, R.y * 0.5 + 0.5));
  env += uSunColor * pow(max(dot(R, L), 0.0), mix(20.0, 380.0, 1.0 - rough)) * uSunEnergy * 0.32;

  vec3 ambient = diffSky * uAmbient * ao * alb * (1.0 - metal) * 0.85
               + env * Fr * uAmbient * (0.95 + metal * 2.3) * mix(ao, 1.0, metal * 0.7);

  vec3 col = direct * mix(0.45, 1.0, ao) + ambient;

  // ---------------- floor reflection
  if (uReflStrength > 0.001 && uReflectionPass == 0 && m == ${MAT.FLOOR}) {
    vec2 suv = gl_FragCoord.xy / uResolution;
    suv.y = 1.0 - suv.y;
    float wob = (fbm(vUV * 0.9 + uTime * 0.02) - 0.5);
    suv += vec2(wob * 0.004, wob * 0.006) * (1.0 - rough);
    vec3 r = texture(uRefl, clamp(suv, 0.002, 0.998)).rgb;
    float fres = pow(1.0 - NoV, 4.0);
    float k = uReflStrength * (1.0 - rough * 1.35) * (0.10 + fres * 0.9);
    col = mix(col, col * 0.55 + r * 1.05, clamp(k, 0.0, 0.85));
  }

  col += uEmissive[m];

  // assembly glow — edges light up while a piece is arriving
  if (uXray > 0.001) {
    float edge = 1.0 - abs(dot(N, V));
    float arriving = smoothstep(0.02, 0.75, vReveal) * (1.0 - smoothstep(0.75, 1.0, vReveal));
    col += vec3(1.0, 0.72, 0.36) * pow(edge, 2.5) * arriving * 2.4 * uXray;
  }

  oColor = vec4(col, 1.0);
}`;

/* ============================================================ SHADOW PASS */
export const DEPTH_VS = `#version 300 es
precision highp float;
layout(location=0) in vec3 aPos;
layout(location=3) in float aObj;
layout(location=5) in vec3 aPivot;
uniform mat4 uLightVP;
uniform sampler2D uObjTex;
out float vRev;
void main(){
  vec4 od = texelFetch(uObjTex, ivec2(int(aObj + 0.5), 0), 0);
  float rev = clamp(od.r, 0.0, 1.0);
  float e = rev * rev * (3.0 - 2.0 * rev);
  vec3 p = mix(aPivot, aPos, e);
  p.y += (1.0 - e) * od.g;
  vRev = rev;
  gl_Position = uLightVP * vec4(p, 1.0);
}`;

export const DEPTH_FS = `#version 300 es
precision highp float;
in float vRev;
out vec4 o;
void main(){ if (vRev < 0.004) discard; o = vec4(1.0); }`;

/* ============================================================== SKY DOME */
export const SKY_VS = `#version 300 es
precision highp float;
layout(location=0) in vec2 aP;
out vec2 vUV;
void main(){ vUV = aP * 0.5 + 0.5; gl_Position = vec4(aP, 1.0, 1.0); }`;

export const SKY_FS = `#version 300 es
precision highp float;
in vec2 vUV;
out vec4 o;
uniform mat4 uInvViewProj;
uniform vec3 uEye;
uniform vec3 uSunDir;
uniform vec3 uSkyColor;
uniform vec3 uGroundColor;
uniform vec3 uSunColor;
uniform float uSunEnergy;
${NOISE}
void main(){
  vec4 h = uInvViewProj * vec4(vUV * 2.0 - 1.0, 1.0, 1.0);
  vec3 dir = normalize(h.xyz / h.w - uEye);
  vec3 L = normalize(-uSunDir);

  float t = clamp(dir.y * 0.5 + 0.5, 0.0, 1.0);
  vec3 horizon = mix(uGroundColor * 1.4, uSkyColor, smoothstep(0.35, 0.62, t));
  vec3 zenith = uSkyColor * 0.55 + vec3(0.02, 0.05, 0.12);
  vec3 col = mix(horizon, zenith, smoothstep(0.5, 1.0, t));
  // hold the dome under 1.0 so a window shows sky, not a white hole
  col *= 0.66;

  float sd = max(dot(dir, L), 0.0);
  col += uSunColor * pow(sd, 900.0) * 22.0 * uSunEnergy;          // disc
  col += uSunColor * pow(sd, 6.0) * 0.55 * uSunEnergy;            // bloom around it
  col += uSunColor * pow(sd, 1.6) * 0.12;                          // wide haze

  // a thin band of cloud so the windows have something to look at
  float cl = fbm(vec2(dir.x, dir.z) / max(abs(dir.y) + 0.12, 0.12) * 0.55);
  float band = smoothstep(0.02, 0.42, dir.y) * (1.0 - smoothstep(0.4, 0.95, dir.y));
  col = mix(col, col * 0.75 + uSunColor * 0.55, smoothstep(0.52, 0.82, cl) * band * 0.75);

  o = vec4(max(col, vec3(0.0)), 1.0);
}`;

/* ============================================================= FULLSCREEN */
export const FS_VS = `#version 300 es
precision highp float;
layout(location=0) in vec2 aP;
out vec2 vUV;
void main(){ vUV = aP * 0.5 + 0.5; gl_Position = vec4(aP, 0.0, 1.0); }`;

export const BRIGHT_FS = `#version 300 es
precision highp float;
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
uniform float uThreshold;
uniform float uSoft;
void main(){
  vec3 c = texture(uTex, vUV).rgb;
  float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
  float k = smoothstep(uThreshold, uThreshold + uSoft, l);
  o = vec4(c * k, 1.0);
}`;

export const BLUR_FS = `#version 300 es
precision highp float;
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
uniform vec2 uDir;      // texel-sized direction
void main(){
  // 9-tap gaussian, linear-sampling weights
  vec3 c = texture(uTex, vUV).rgb * 0.2270270270;
  c += texture(uTex, vUV + uDir * 1.3846153846).rgb * 0.3162162162;
  c += texture(uTex, vUV - uDir * 1.3846153846).rgb * 0.3162162162;
  c += texture(uTex, vUV + uDir * 3.2307692308).rgb * 0.0702702703;
  c += texture(uTex, vUV - uDir * 3.2307692308).rgb * 0.0702702703;
  o = vec4(c, 1.0);
}`;

export const GODRAY_FS = `#version 300 es
precision highp float;
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
uniform vec2 uSunUV;
uniform float uDensity;
uniform float uDecay;
uniform float uWeight;
uniform float uExposure;
void main(){
  vec2 uv = vUV;
  vec2 delta = (uv - uSunUV) * (uDensity / 28.0);
  vec3 col = texture(uTex, uv).rgb;
  float illum = uExposure;
  for (int i = 0; i < 28; i++){
    uv -= delta;
    vec3 s = texture(uTex, clamp(uv, 0.0, 1.0)).rgb;
    col += s * illum * uWeight;
    illum *= uDecay;
  }
  o = vec4(col, 1.0);
}`;

export const COMPOSITE_FS = `#version 300 es
precision highp float;
in vec2 vUV; out vec4 o;
uniform sampler2D uScene;
uniform sampler2D uBloom;
uniform sampler2D uRays;
uniform float uBloomAmt;
uniform float uRayAmt;
uniform float uExposure;
uniform float uVignette;
uniform float uGrain;
uniform float uAberration;
uniform float uTime;
uniform float uFade;
uniform float uSaturation;
uniform vec3 uTint;
uniform vec2 uResolution;

${NOISE}

vec3 aces(vec3 x){
  const float a = 2.51, b = 0.03, c = 2.43, d = 0.59, e = 0.14;
  return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}

void main(){
  vec2 uv = vUV;
  vec2 c = uv - 0.5;
  float r2 = dot(c, c);

  // barrel + chromatic aberration, both strongest at the edge
  vec2 duv = c * r2 * uAberration;
  vec3 col;
  col.r = texture(uScene, uv + duv * 1.00).r;
  col.g = texture(uScene, uv).g;
  col.b = texture(uScene, uv - duv * 1.00).b;

  col += texture(uBloom, uv).rgb * uBloomAmt;
  col += texture(uRays, uv).rgb * uRayAmt;

  col *= uExposure;
  col *= uTint;
  col = aces(col);

  // a gentle S-curve — interiors go milky without it
  col = mix(col, col * col * (3.0 - 2.0 * col), 0.42);

  float lum = dot(col, vec3(0.2126, 0.7152, 0.0722));
  col = mix(vec3(lum), col, uSaturation);

  // vignette
  float vig = smoothstep(0.95, 0.18, r2 * 2.0);
  col *= mix(1.0, vig, uVignette);

  // film grain, animated but deterministic
  float g = h21(gl_FragCoord.xy + fract(uTime) * 91.7) - 0.5;
  col += g * uGrain * (1.0 - lum * 0.6);

  // gentle filmic toe so blacks are never pure void
  col = pow(max(col, 0.0), vec3(0.9091));
  col = mix(vec3(0.012, 0.013, 0.018), col, uFade);

  o = vec4(col, 1.0);
}`;

/* ================================================================ MOTES */
export const MOTE_VS = `#version 300 es
precision highp float;
layout(location=0) in vec3 aSeed;
uniform mat4 uViewProj;
uniform vec3 uEye;
uniform float uTime;
uniform float uSpread;
uniform float uSize;
out float vA;
void main(){
  vec3 s = aSeed;
  // drift inside a box that follows the camera, wrapped so motes never run out
  vec3 p;
  p.x = mod(s.x * 41.7 + uTime * 0.22 + sin(uTime * 0.31 + s.y * 9.0) * 0.6, uSpread) - uSpread * 0.5;
  p.y = mod(s.y * 37.3 + uTime * 0.09 + cos(uTime * 0.24 + s.z * 7.0) * 0.5, uSpread * 0.55) - uSpread * 0.14;
  p.z = mod(s.z * 53.1 + uTime * 0.15 + sin(uTime * 0.19 + s.x * 5.0) * 0.7, uSpread) - uSpread * 0.5;
  vec3 w = uEye + p;
  vec4 cp = uViewProj * vec4(w, 1.0);
  gl_Position = cp;
  float d = max(cp.w, 0.5);
  gl_PointSize = clamp(uSize / d, 1.0, 14.0);
  vA = clamp(1.0 - d / (uSpread * 0.7), 0.0, 1.0) * (0.25 + fract(s.x * 13.7) * 0.75);
}`;

export const MOTE_FS = `#version 300 es
precision highp float;
in float vA; out vec4 o;
uniform vec3 uColor;
void main(){
  vec2 d = gl_PointCoord - 0.5;
  float f = 1.0 - smoothstep(0.10, 0.5, length(d));
  float a = f * vA;
  if (a < 0.012) discard;          // never leave an unlit sprite quad behind
  o = vec4(uColor * a, a);
}`;

/* ============================================================ BLIT (copy) */
export const BLIT_FS = `#version 300 es
precision highp float;
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
void main(){ o = texture(uTex, vUV); }`;
