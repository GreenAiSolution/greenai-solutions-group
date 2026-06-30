/* Nexus AI — 3D Background · Three.js ES module */
import * as THREE from 'three';

const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const canvas = document.getElementById('scene');
let renderer, scene, camera, core_group, ring, sats=[], stars, neb=[], raf;
const R = 1.4;
const pointer = { x:0, y:0 };
const clock = new THREE.Clock();

function init(){
  renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true, powerPreference:'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x06080f, 0.04);

  camera = new THREE.PerspectiveCamera(42, window.innerWidth/window.innerHeight, 0.1, 120);
  camera.position.set(0,0,9);

  scene.add(new THREE.AmbientLight(0x1a0a3a, 1.0));
  const key = new THREE.PointLight(0x8b5cf6, 70, 60); key.position.set(5,4,7); scene.add(key);
  const rim = new THREE.PointLight(0x22d3ee, 30, 60); rim.position.set(-7,-3,2); scene.add(rim);
  const fill = new THREE.PointLight(0x7c3aed, 28, 60); fill.position.set(-4,5,-5); scene.add(fill);

  buildCore();
  buildStars();
  buildNebula();

  window.addEventListener('resize', onResize, { passive:true });
  window.addEventListener('pointermove', onPointer, { passive:true });
  animate();

  window.__nx = { THREE, get core(){ return core_group; }, get camera(){ return camera; } };
}

function buildCore(){
  core_group = new THREE.Group();

  // inner sphere — deep violet emissive
  const core = new THREE.Mesh(
    new THREE.SphereGeometry(R, 64, 64),
    new THREE.MeshStandardMaterial({ color:0x1a0a3a, emissive:0x7c3aed, emissiveIntensity:0.85, roughness:0.5, metalness:0.5 })
  );
  core_group.add(core); core_group.userData.core = core;

  // wireframe grid — violet
  const grid = new THREE.Mesh(
    new THREE.SphereGeometry(R*1.012, 28, 20),
    new THREE.MeshBasicMaterial({ color:0x8b5cf6, wireframe:true, transparent:true, opacity:0.2 })
  );
  core_group.add(grid); core_group.userData.grid = grid;

  // icosahedron cage — cyan
  const cage = new THREE.Mesh(
    new THREE.IcosahedronGeometry(R*1.32, 1),
    new THREE.MeshBasicMaterial({ color:0x22d3ee, wireframe:true, transparent:true, opacity:0.28 })
  );
  core_group.add(cage); core_group.userData.cage = cage;

  // atmosphere halo — violet
  const atmo = new THREE.Mesh(
    new THREE.SphereGeometry(R*1.5, 48, 48),
    new THREE.MeshBasicMaterial({ color:0x8b5cf6, transparent:true, opacity:0.07, side:THREE.BackSide, blending:THREE.AdditiveBlending, depthWrite:false })
  );
  core_group.add(atmo);

  // ring — violet
  ring = new THREE.Mesh(
    new THREE.RingGeometry(R*1.7, R*2.5, 128),
    new THREE.MeshBasicMaterial({ color:0x8b5cf6, transparent:true, opacity:0.25, side:THREE.DoubleSide, blending:THREE.AdditiveBlending, depthWrite:false })
  );
  ring.rotation.set(Math.PI/2.1, 0.3, 0);
  core_group.add(ring);

  // thin cyan ring
  const ring2 = new THREE.Mesh(
    new THREE.RingGeometry(R*2.7, R*2.78, 160),
    new THREE.MeshBasicMaterial({ color:0x22d3ee, transparent:true, opacity:0.42, side:THREE.DoubleSide })
  );
  ring2.rotation.copy(ring.rotation);
  core_group.add(ring2);

  // satellites
  const satDefs = [
    { r:R*2.0, size:0.06, color:0x8b5cf6, speed:0.55, tilt:[Math.PI/2.4,0,0], phase:0 },
    { r:R*2.5, size:0.05, color:0x22d3ee, speed:-0.4, tilt:[Math.PI/1.7,0.4,0], phase:2 },
    { r:R*3.1, size:0.07, color:0xa78bfa, speed:0.3, tilt:[Math.PI/3,-0.5,0.4], phase:4 },
  ];
  satDefs.forEach(d => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(d.size,18,18), new THREE.MeshBasicMaterial({ color:d.color }));
    m.userData=d; core_group.add(m); sats.push(m);
    const trail = new THREE.Mesh(new THREE.TorusGeometry(d.r, 0.004, 8, 128), new THREE.MeshBasicMaterial({ color:d.color, transparent:true, opacity:0.16 }));
    trail.rotation.set(...d.tilt); core_group.add(trail);
  });

  // data motes — violet
  const n=220, mg=new THREE.BufferGeometry(), mp=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    const rr=R*(1.6+Math.random()*2.2), t=Math.random()*Math.PI*2, p=Math.acos(2*Math.random()-1);
    mp[i*3]=rr*Math.sin(p)*Math.cos(t); mp[i*3+1]=rr*Math.cos(p)*0.7; mp[i*3+2]=rr*Math.sin(p)*Math.sin(t);
  }
  mg.setAttribute('position', new THREE.BufferAttribute(mp,3));
  const motes = new THREE.Points(mg, new THREE.PointsMaterial({ color:0x8b5cf6, size:0.028, transparent:true, opacity:0.58, depthWrite:false, blending:THREE.AdditiveBlending }));
  core_group.add(motes); core_group.userData.motes = motes;

  positionCore();
  scene.add(core_group);
}

function positionCore(){
  const wide = window.innerWidth > 900;
  core_group.position.set(wide?3.0:0, wide?0.2:1.8, 0);
  const s = wide?1:0.66;
  core_group.scale.setScalar(s);
  core_group.userData.baseScale = s;
}

function buildStars(){
  const count = Math.min(3600, Math.floor(window.innerWidth*2.6));
  const g=new THREE.BufferGeometry(), pos=new Float32Array(count*3), col=new Float32Array(count*3);
  const cA=new THREE.Color(0x8b5cf6), cB=new THREE.Color(0x2a2f5a), cC=new THREE.Color(0x22d3ee);
  for(let i=0;i<count;i++){
    pos[i*3]=(Math.random()-.5)*80; pos[i*3+1]=(Math.random()-.5)*52; pos[i*3+2]=(Math.random()-.5)*50-10;
    const c=Math.random()<0.07?cC:(Math.random()<0.4?cA:cB);
    col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b;
  }
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('color',new THREE.BufferAttribute(col,3));
  stars=new THREE.Points(g, new THREE.PointsMaterial({ size:0.06, vertexColors:true, transparent:true, opacity:0.85, depthWrite:false, blending:THREE.AdditiveBlending }));
  scene.add(stars);
}

function buildNebula(){
  const defs=[{x:-10,y:5,z:-18,c:0x4c1d95,s:9},{x:12,y:-7,z:-22,c:0x0c4a7a,s:11},{x:6,y:9,z:-26,c:0x22d3ee,s:5}];
  defs.forEach(d=>{
    const m=new THREE.Mesh(new THREE.SphereGeometry(d.s,24,24),
      new THREE.MeshBasicMaterial({ color:d.c, transparent:true, opacity:0.05, blending:THREE.AdditiveBlending, depthWrite:false }));
    m.position.set(d.x,d.y,d.z); scene.add(m); neb.push(m);
  });
}

function onResize(){
  camera.aspect=window.innerWidth/window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight); renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  positionCore();
}
function onPointer(e){ pointer.x=(e.clientX/window.innerWidth)*2-1; pointer.y=(e.clientY/window.innerHeight)*2-1; }

function animate(){
  raf=requestAnimationFrame(animate);
  const t=clock.getElapsedTime();
  if(core_group){
    core_group.rotation.y=t*0.10;
    core_group.userData.grid.rotation.y=t*0.16;
    core_group.userData.cage.rotation.y=-t*0.22; core_group.userData.cage.rotation.x=t*0.08;
    core_group.userData.core.material.emissiveIntensity=0.78+Math.sin(t*1.3)*0.28;
    core_group.userData.motes.rotation.y=-t*0.06;
    core_group.position.y+=Math.sin(t*0.7)*0.0014;
    const sc=window.scrollY||0;
    core_group.rotation.z=sc*0.00016; core_group.rotation.x=sc*0.00010;
    sats.forEach(m=>{
      const a=t*m.userData.speed+m.userData.phase, r=m.userData.r;
      const v=new THREE.Vector3(Math.cos(a)*r,Math.sin(a)*r,0);
      v.applyEuler(new THREE.Euler(...m.userData.tilt));
      m.position.copy(v);
    });
  }
  if(stars){ stars.rotation.y=t*0.01; stars.rotation.x=t*0.004; }
  const tx=pointer.x*0.7, ty=-pointer.y*0.45;
  camera.position.x+=(tx-camera.position.x)*0.035;
  camera.position.y+=(ty-camera.position.y)*0.035;
  camera.lookAt(0,0,0);
  renderer.render(scene,camera);
}

window.addEventListener('beforeunload',()=>{ cancelAnimationFrame(raf); renderer&&renderer.dispose(); });

try{ if(canvas) init(); }
catch(e){ console.warn('WebGL unavailable',e); document.body.style.background='radial-gradient(120% 90% at 72% 8%, #1a0a3a 0%, #06080f 55%)'; }
