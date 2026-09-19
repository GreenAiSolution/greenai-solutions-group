// ATRIUM — WebGL2 renderer. Hand-written, no libraries.
// Pass order: shadow → floor reflection → main HDR → bright → blur → god rays → grade.

import * as S from './shaders.js';
import { STRIDE } from './geom.js';
import { m4, m4perspective, m4lookAt, m4mul, m4ortho, m4invert, v3, v3norm, v3sub, v3add, v3cross, v3scale, DEG } from './math.js';

function compile(gl, type, src, label) {
  const sh = gl.createShader(type);
  gl.shaderSource(sh, src);
  gl.compileShader(sh);
  if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(sh);
    console.error(`[ATRIUM] ${label} failed:\n${log}`);
    throw new Error(`${label}: ${log}`);
  }
  return sh;
}

function program(gl, vsSrc, fsSrc, label) {
  const p = gl.createProgram();
  gl.attachShader(p, compile(gl, gl.VERTEX_SHADER, vsSrc, label + '.vs'));
  gl.attachShader(p, compile(gl, gl.FRAGMENT_SHADER, fsSrc, label + '.fs'));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
    throw new Error(`${label} link: ${gl.getProgramInfoLog(p)}`);
  }
  const u = {};
  const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
  for (let i = 0; i < n; i++) {
    const info = gl.getActiveUniform(p, i);
    const name = info.name.replace(/\[0\]$/, '');
    u[name] = gl.getUniformLocation(p, name);
    if (info.size > 1) {
      for (let k = 0; k < info.size; k++) {
        u[`${name}[${k}]`] = gl.getUniformLocation(p, `${name}[${k}]`);
      }
    }
  }
  return { p, u };
}

export class Renderer {
  constructor(canvas) {
    const gl = canvas.getContext('webgl2', {
      antialias: false, alpha: false, depth: true, stencil: false,
      powerPreference: 'high-performance', preserveDrawingBuffer: false,
    });
    if (!gl) throw new Error('WebGL2 is not available in this browser.');
    this.gl = gl;
    this.canvas = canvas;

    this.floatOK = !!gl.getExtension('EXT_color_buffer_float');
    gl.getExtension('OES_texture_float_linear');

    this.prog = {
      scene: program(gl, S.SCENE_VS, S.SCENE_FS, 'scene'),
      depth: program(gl, S.DEPTH_VS, S.DEPTH_FS, 'depth'),
      sky: program(gl, S.SKY_VS, S.SKY_FS, 'sky'),
      bright: program(gl, S.FS_VS, S.BRIGHT_FS, 'bright'),
      blur: program(gl, S.FS_VS, S.BLUR_FS, 'blur'),
      rays: program(gl, S.FS_VS, S.GODRAY_FS, 'rays'),
      comp: program(gl, S.FS_VS, S.COMPOSITE_FS, 'composite'),
      motes: program(gl, S.MOTE_VS, S.MOTE_FS, 'motes'),
      blit: program(gl, S.FS_VS, S.BLIT_FS, 'blit'),
    };

    // fullscreen triangle-pair
    this.quad = gl.createVertexArray();
    gl.bindVertexArray(this.quad);
    const qb = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, qb);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 3,-1, -1,3]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    gl.bindVertexArray(null);

    // per-object animation data: 256 slots × RGBA (reveal, yOffset, sway, spare)
    this.objData = new Float32Array(256 * 4);
    this.objTex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.objTex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, 256, 1, 0, gl.RGBA, gl.FLOAT, this.objData);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

    this.SHADOW = 2048;
    this.shadow = this.makeShadow(this.SHADOW);

    this.rt = {};
    this.size = { w: 0, h: 0, dpr: 1 };

    // dust motes
    this.moteCount = 900;
    const seeds = new Float32Array(this.moteCount * 3);
    for (let i = 0; i < this.moteCount; i++) {
      const a = Math.sin(i * 12.9898) * 43758.5453;
      const b = Math.sin(i * 78.233) * 12345.6789;
      const c = Math.sin(i * 39.425) * 24634.6345;
      seeds[i * 3] = a - Math.floor(a);
      seeds[i * 3 + 1] = b - Math.floor(b);
      seeds[i * 3 + 2] = c - Math.floor(c);
    }
    this.moteVao = gl.createVertexArray();
    gl.bindVertexArray(this.moteVao);
    const mb = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, mb);
    gl.bufferData(gl.ARRAY_BUFFER, seeds, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
    gl.bindVertexArray(null);

    // scratch matrices
    this._proj = m4(); this._view = m4(); this._vp = m4(); this._inv = m4();
    this._lproj = m4(); this._lview = m4(); this._lvp = m4();
    this._eye = v3(); this._look = v3(); this._up = v3(0, 1, 0);
    this._mvp = m4(); this._mview = m4();

    this.quality = 1.0;
    this.reflectionsOn = true;
  }

  makeShadow(n) {
    const gl = this.gl;
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.DEPTH_COMPONENT24, n, n, 0, gl.DEPTH_COMPONENT, gl.UNSIGNED_INT, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_COMPARE_MODE, gl.NONE);
    const fb = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.TEXTURE_2D, tex, 0);
    gl.drawBuffers([gl.NONE]);
    gl.readBuffer(gl.NONE);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    return { tex, fb, size: n };
  }

  makeRT(w, h, depth, float) {
    const gl = this.gl;
    w = Math.max(2, w | 0); h = Math.max(2, h | 0);
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    const internal = (float && this.floatOK) ? gl.RGBA16F : gl.RGBA8;
    const type = (float && this.floatOK) ? gl.HALF_FLOAT : gl.UNSIGNED_BYTE;
    gl.texImage2D(gl.TEXTURE_2D, 0, internal, w, h, 0, gl.RGBA, type, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    const fb = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
    let rb = null;
    if (depth) {
      rb = gl.createRenderbuffer();
      gl.bindRenderbuffer(gl.RENDERBUFFER, rb);
      gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH_COMPONENT24, w, h);
      gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.RENDERBUFFER, rb);
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    return { tex, fb, rb, w, h };
  }

  resize(w, h, dpr) {
    const gl = this.gl;
    dpr = Math.min(dpr || 1, 2);
    const W = Math.max(2, Math.round(w * dpr * this.quality));
    const H = Math.max(2, Math.round(h * dpr * this.quality));
    if (this.size.w === W && this.size.h === H) return;
    this.size = { w: W, h: H, dpr };
    this.canvas.width = W; this.canvas.height = H;

    for (const k in this.rt) {
      const r = this.rt[k];
      if (r) { gl.deleteTexture(r.tex); gl.deleteFramebuffer(r.fb); if (r.rb) gl.deleteRenderbuffer(r.rb); }
    }
    const hw = Math.max(2, W >> 1), hh = Math.max(2, H >> 1);
    this.rt = {
      hdr: this.makeRT(W, H, true, true),
      refl: this.makeRT(hw, hh, true, true),
      bright: this.makeRT(hw, hh, false, true),
      blurA: this.makeRT(hw, hh, false, true),
      blurB: this.makeRT(hw, hh, false, true),
      rays: this.makeRT(hw, hh, false, true),
    };
  }

  uploadScene(mesh) {
    const gl = this.gl;
    if (this.vao) { gl.deleteVertexArray(this.vao); gl.deleteBuffer(this.vbo); gl.deleteBuffer(this.ibo); }
    this.vao = gl.createVertexArray();
    gl.bindVertexArray(this.vao);
    this.vbo = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.vbo);
    gl.bufferData(gl.ARRAY_BUFFER, mesh.vertices, gl.STATIC_DRAW);
    const s = STRIDE * 4;
    const attrs = [
      [0, 3, 0], [1, 3, 12], [2, 2, 24], [3, 1, 32], [4, 1, 36], [5, 3, 40], [6, 1, 52],
    ];
    for (const [loc, n, off] of attrs) {
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, n, gl.FLOAT, false, s, off);
    }
    this.ibo = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.ibo);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, mesh.indices, gl.STATIC_DRAW);
    gl.bindVertexArray(null);
    this.indexCount = mesh.indices.length;
    this.triCount = this.indexCount / 3;
    this.vertCount = mesh.vertices.length / STRIDE;
  }

  syncObjects() {
    const gl = this.gl;
    gl.bindTexture(gl.TEXTURE_2D, this.objTex);
    gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, 256, 1, gl.RGBA, gl.FLOAT, this.objData);
  }

  drawQuad(prog) {
    const gl = this.gl;
    gl.useProgram(prog.p);
    gl.bindVertexArray(this.quad);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  bindRT(rt) {
    const gl = this.gl;
    gl.bindFramebuffer(gl.FRAMEBUFFER, rt ? rt.fb : null);
    if (rt) gl.viewport(0, 0, rt.w, rt.h);
    else gl.viewport(0, 0, this.size.w, this.size.h);
  }

  /* ---- uniform helpers for the scene program ---- */
  setSceneMaterials(u, mats) {
    const gl = this.gl;
    for (let i = 0; i < S.NMAT; i++) {
      const m = mats[i];
      gl.uniform3f(u[`uAlbedo[${i}]`], m.albedo[0], m.albedo[1], m.albedo[2]);
      gl.uniform1f(u[`uRough[${i}]`], m.roughness);
      gl.uniform1f(u[`uMetal[${i}]`], m.metallic);
      gl.uniform3f(u[`uEmissive[${i}]`], m.emissive[0], m.emissive[1], m.emissive[2]);
      gl.uniform1i(u[`uFamily[${i}]`], m.family);
      gl.uniform1f(u[`uDetail[${i}]`], m.detail);
    }
  }

  setSceneLighting(u, st) {
    const gl = this.gl;
    gl.uniform3fv(u.uSunDir, st.sunDir);
    gl.uniform3fv(u.uSunColor, st.sunColor);
    gl.uniform1f(u.uSunEnergy, st.sunEnergy);
    gl.uniform3fv(u.uSkyColor, st.skyColor);
    gl.uniform3fv(u.uGroundColor, st.groundColor);
    gl.uniform1f(u.uAmbient, st.ambient);
    const n = Math.min(st.lights.length, S.MAXLIGHTS);
    gl.uniform1i(u.uNumLights, n);
    for (let i = 0; i < n; i++) {
      const L = st.lights[i];
      gl.uniform3f(u[`uLightPos[${i}]`], L.pos[0], L.pos[1], L.pos[2]);
      gl.uniform3f(u[`uLightColor[${i}]`], L.color[0] * L.intensity, L.color[1] * L.intensity, L.color[2] * L.intensity);
      gl.uniform1f(u[`uLightRange[${i}]`], L.range);
    }
  }

  /* ------------------------------------------------------------- render */
  render(st) {
    const gl = this.gl;
    const { w: W, h: H } = this.size;
    if (!this.vao || W < 2) return;

    const aspect = W / H;
    m4perspective(this._proj, st.fov * DEG, aspect, 0.06, 400);
    m4lookAt(this._view, st.eye, st.look, this._up);
    m4mul(this._vp, this._proj, this._view);
    m4invert(this._inv, this._vp);

    // ---- light matrix: ortho box around the house
    const c = st.shadowCenter, r = st.shadowRadius;
    const sd = st.sunDir;
    const lightEye = v3(c[0] - sd[0] * r * 2.2, c[1] - sd[1] * r * 2.2, c[2] - sd[2] * r * 2.2);
    m4ortho(this._lproj, -r, r, -r, r, 0.1, r * 5.0);
    m4lookAt(this._lview, lightEye, c, this._up);
    m4mul(this._lvp, this._lproj, this._lview);

    /* ---------------- 1. shadow depth ---------------- */
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.shadow.fb);
    gl.viewport(0, 0, this.shadow.size, this.shadow.size);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.depthMask(true);
    gl.clear(gl.DEPTH_BUFFER_BIT);
    gl.enable(gl.CULL_FACE);
    gl.cullFace(gl.FRONT);
    {
      const { p, u } = this.prog.depth;
      gl.useProgram(p);
      gl.uniformMatrix4fv(u.uLightVP, false, this._lvp);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.objTex);
      gl.uniform1i(u.uObjTex, 0);
      gl.bindVertexArray(this.vao);
      gl.drawElements(gl.TRIANGLES, this.indexCount, gl.UNSIGNED_INT, 0);
    }
    gl.cullFace(gl.BACK);

    /* ---------------- 2. floor reflection ---------------- */
    const doRefl = this.reflectionsOn && st.reflStrength > 0.002;
    if (doRefl) {
      const fy = st.floorY;
      const me = v3(st.eye[0], 2 * fy - st.eye[1], st.eye[2]);
      const ml = v3(st.look[0], 2 * fy - st.look[1], st.look[2]);
      const mview = m4(), mvp = m4();
      m4lookAt(mview, me, ml, this._up);
      m4mul(mvp, this._proj, mview);
      this.bindRT(this.rt.refl);
      gl.clearColor(0, 0, 0, 1);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      this.drawSky(mvp, me, st);
      gl.enable(gl.DEPTH_TEST);
      gl.frontFace(gl.CW);
      this.drawScene(mvp, me, st, 1, fy);
      gl.frontFace(gl.CCW);
    }

    /* ---------------- 3. main HDR ---------------- */
    this.bindRT(this.rt.hdr);
    gl.clearColor(0, 0, 0, 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    this.drawSky(this._vp, st.eye, st);
    gl.enable(gl.DEPTH_TEST);
    this.drawScene(this._vp, st.eye, st, 0, st.floorY, doRefl ? this.rt.refl.tex : null);

    // motes, additive
    if (st.moteAmount > 0.01) {
      const { p, u } = this.prog.motes;
      gl.useProgram(p);
      gl.enable(gl.BLEND);
      gl.blendEquation(gl.FUNC_ADD);
      gl.blendFunc(gl.ONE, gl.ONE);     // premultiplied in the shader
      gl.depthMask(false);
      gl.uniformMatrix4fv(u.uViewProj, false, this._vp);
      gl.uniform3fv(u.uEye, st.eye);
      gl.uniform1f(u.uTime, st.time);
      gl.uniform1f(u.uSpread, 26.0);
      gl.uniform1f(u.uSize, 90.0);
      gl.uniform3f(u.uColor, st.moteColor[0] * st.moteAmount, st.moteColor[1] * st.moteAmount, st.moteColor[2] * st.moteAmount);
      gl.bindVertexArray(this.moteVao);
      gl.drawArrays(gl.POINTS, 0, this.moteCount);
      gl.depthMask(true);
      gl.disable(gl.BLEND);
    }

    /* ---------------- 4. bright pass ---------------- */
    gl.disable(gl.DEPTH_TEST);
    this.bindRT(this.rt.bright);
    {
      const { p, u } = this.prog.bright;
      gl.useProgram(p);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.rt.hdr.tex);
      gl.uniform1i(u.uTex, 0);
      gl.uniform1f(u.uThreshold, st.bloomThreshold);
      gl.uniform1f(u.uSoft, 0.55);
      gl.bindVertexArray(this.quad);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    /* ---------------- 5. separable blur ---------------- */
    let src = this.rt.bright;
    const { p: bp, u: bu } = this.prog.blur;
    gl.useProgram(bp);
    gl.bindVertexArray(this.quad);
    for (let i = 0; i < 3; i++) {
      const scale = 1 + i * 1.6;
      this.bindRT(this.rt.blurA);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, src.tex);
      gl.uniform1i(bu.uTex, 0);
      gl.uniform2f(bu.uDir, scale / this.rt.blurA.w, 0);
      gl.drawArrays(gl.TRIANGLES, 0, 3);

      this.bindRT(this.rt.blurB);
      gl.bindTexture(gl.TEXTURE_2D, this.rt.blurA.tex);
      gl.uniform2f(bu.uDir, 0, scale / this.rt.blurB.h);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      src = this.rt.blurB;
    }

    /* ---------------- 6. god rays ---------------- */
    const sunW = v3(st.eye[0] - st.sunDir[0] * 100, st.eye[1] - st.sunDir[1] * 100, st.eye[2] - st.sunDir[2] * 100);
    const cx = this._vp[0] * sunW[0] + this._vp[4] * sunW[1] + this._vp[8] * sunW[2] + this._vp[12];
    const cy = this._vp[1] * sunW[0] + this._vp[5] * sunW[1] + this._vp[9] * sunW[2] + this._vp[13];
    const cw = this._vp[3] * sunW[0] + this._vp[7] * sunW[1] + this._vp[11] * sunW[2] + this._vp[15];
    const sunUV = [(cx / cw) * 0.5 + 0.5, (cy / cw) * 0.5 + 0.5];
    const sunVisible = cw > 0 && sunUV[0] > -0.6 && sunUV[0] < 1.6 && sunUV[1] > -0.6 && sunUV[1] < 1.6;
    this.bindRT(this.rt.rays);
    if (sunVisible && st.rayAmount > 0.001) {
      const { p, u } = this.prog.rays;
      gl.useProgram(p);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.rt.bright.tex);
      gl.uniform1i(u.uTex, 0);
      gl.uniform2f(u.uSunUV, sunUV[0], sunUV[1]);
      gl.uniform1f(u.uDensity, 0.85);
      gl.uniform1f(u.uDecay, 0.955);
      gl.uniform1f(u.uWeight, 0.052);
      gl.uniform1f(u.uExposure, 0.30);
      gl.bindVertexArray(this.quad);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    } else {
      gl.clearColor(0, 0, 0, 1);
      gl.clear(gl.COLOR_BUFFER_BIT);
    }

    /* ---------------- 7. grade to screen ---------------- */
    this.bindRT(null);
    {
      const { p, u } = this.prog.comp;
      gl.useProgram(p);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.rt.hdr.tex);   gl.uniform1i(u.uScene, 0);
      gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, src.tex);            gl.uniform1i(u.uBloom, 1);
      gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, this.rt.rays.tex);  gl.uniform1i(u.uRays, 2);
      gl.uniform1f(u.uBloomAmt, st.bloom);
      gl.uniform1f(u.uRayAmt, sunVisible ? st.rayAmount : 0.0);
      gl.uniform1f(u.uExposure, st.exposure);
      gl.uniform1f(u.uVignette, st.vignette);
      gl.uniform1f(u.uGrain, st.grain);
      gl.uniform1f(u.uAberration, st.aberration);
      gl.uniform1f(u.uTime, st.time);
      gl.uniform1f(u.uFade, st.fade);
      gl.uniform1f(u.uSaturation, st.saturation);
      gl.uniform3fv(u.uTint, st.tint);
      gl.uniform2f(u.uResolution, W, H);
      gl.bindVertexArray(this.quad);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    gl.bindVertexArray(null);
  }

  drawSky(vp, eye, st) {
    const gl = this.gl;
    const inv = m4();
    m4invert(inv, vp);
    const { p, u } = this.prog.sky;
    gl.useProgram(p);
    gl.disable(gl.DEPTH_TEST);
    gl.uniformMatrix4fv(u.uInvViewProj, false, inv);
    gl.uniform3fv(u.uEye, eye);
    gl.uniform3fv(u.uSunDir, st.sunDir);
    gl.uniform3fv(u.uSkyColor, st.skyColor);
    gl.uniform3fv(u.uGroundColor, st.groundColor);
    gl.uniform3fv(u.uSunColor, st.sunColor);
    gl.uniform1f(u.uSunEnergy, st.sunEnergy);
    gl.bindVertexArray(this.quad);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  drawScene(vp, eye, st, reflPass, floorY, reflTex) {
    const gl = this.gl;
    const { p, u } = this.prog.scene;
    gl.useProgram(p);
    gl.enable(gl.DEPTH_TEST);
    gl.enable(gl.CULL_FACE);
    gl.uniformMatrix4fv(u.uViewProj, false, vp);
    gl.uniformMatrix4fv(u.uLightVP, false, this._lvp);
    gl.uniform3fv(u.uEye, eye);
    gl.uniform1f(u.uTime, st.time);
    gl.uniform1f(u.uXray, st.xray);
    gl.uniform1i(u.uReflectionPass, reflPass);
    gl.uniform1f(u.uClipY, floorY);
    gl.uniform1f(u.uShadowStrength, st.shadowStrength);
    gl.uniform2f(u.uShadowTexel, 1 / this.shadow.size, 1 / this.shadow.size);
    gl.uniform2f(u.uResolution, this.size.w, this.size.h);
    gl.uniform1f(u.uReflStrength, reflTex ? st.reflStrength : 0.0);

    this.setSceneMaterials(u, st.materials);
    this.setSceneLighting(u, st);

    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.objTex);      gl.uniform1i(u.uObjTex, 0);
    gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, this.shadow.tex);  gl.uniform1i(u.uShadow, 1);
    gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, reflTex || this.shadow.tex); gl.uniform1i(u.uRefl, 2);

    gl.bindVertexArray(this.vao);
    gl.drawElements(gl.TRIANGLES, this.indexCount, gl.UNSIGNED_INT, 0);
  }
}
