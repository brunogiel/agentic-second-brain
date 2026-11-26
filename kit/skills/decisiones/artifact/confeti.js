/* ARTIFACT: confeti propio, de unas 40 líneas. La web real carga canvas-confetti desde su propio sitio; una página privada
   no puede cargar scripts de afuera. Implementa solo lo que usa la web: create(canvas, {resize}) -> disparar(opciones) con
   particleCount, spread, startVelocity, ticks, origin, angle y colors; el disparo devuelve una Promise y tiene .reset(). */
(function(){
'use strict';
function crear(cv){
  var ctx = cv.getContext('2d'), parts = [], raf = 0, esperas = [];
  function medir(){ cv.width = window.innerWidth; cv.height = window.innerHeight; }
  medir(); window.addEventListener('resize', medir);
  function paso(){
    ctx.clearRect(0, 0, cv.width, cv.height);
    parts = parts.filter(function(p){
      p.vx *= 0.99; p.vy = p.vy * 0.99 + 0.45; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.t++;
      if(p.t > p.vida) return false;
      ctx.save(); ctx.globalAlpha = Math.max(0, 1 - p.t / p.vida); ctx.translate(p.x, p.y); ctx.rotate(p.r);
      ctx.fillStyle = p.c; ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); ctx.restore();
      return true;
    });
    if(parts.length) raf = requestAnimationFrame(paso);
    else { raf = 0; esperas.splice(0).forEach(function(f){ f(); }); }
  }
  function disparar(o){
    o = o || {};
    var n = o.particleCount || 50, ang = (o.angle == null ? 90 : o.angle) * Math.PI / 180, sp = (o.spread == null ? 45 : o.spread) * Math.PI / 180;
    var vel = o.startVelocity || 45, orig = o.origin || {}, ox = (orig.x == null ? 0.5 : orig.x) * cv.width, oy = (orig.y == null ? 0.5 : orig.y) * cv.height;
    var cols = o.colors && o.colors.length ? o.colors : ['#8ECAC8', '#FFD166', '#EF476F'];
    for(var i = 0; i < n; i++){
      var a = ang + (Math.random() - 0.5) * sp, v = vel * (0.5 + Math.random() * 0.5) / 2.2;
      parts.push({x: ox, y: oy, vx: Math.cos(a) * v, vy: -Math.sin(a) * v, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4,
        w: 5 + Math.random() * 5, h: 3 + Math.random() * 4, c: cols[i % cols.length], t: 0, vida: Math.min(o.ticks || 200, 160)});
    }
    if(!raf) raf = requestAnimationFrame(paso);
    return new Promise(function(ok){ esperas.push(ok); });
  }
  disparar.reset = function(){ parts = []; if(raf) cancelAnimationFrame(raf); raf = 0; ctx.clearRect(0, 0, cv.width, cv.height); esperas.splice(0).forEach(function(f){ f(); }); };
  return disparar;
}
window.confetti = {create: crear};
})();
