/* ARTIFACT: el paso de «avisar a Claude», después de Enviar.
   La respuesta ya quedó guardada en `respuestas/<clave>` (la escribió el adaptador). Claude la lee de ahí; este paso solo
   le avisa. Tres caminos, del mejor al peor: un mensaje a la conversación de Claude (room), un comentario en la página
   (comments), o que la persona vuelva al chat y escriba «listo». El estado de cada botón vive en window.__art.aviso
   (una pintada nueva del home no lo pierde) y se bloquea tras el primer toque. */
function avRepintar(){ try{ if(estado.sw) swipeRender(); }catch(e){} try{ homePintar(); }catch(e){} }
window.__art.repintar = avRepintar;
function avEstado(c){ var S = window.__art.aviso; return S[c] || (S[c] = {room: {st: '', msg: ''}, com: {st: '', msg: ''}, copia: ''}); }
function avTitulo(c){ var t = tandas().mapa[c]; return t && t.entrada && t.entrada.titulo ? t.entrada.titulo : c; }
function avLimpio(s){   // sin caracteres de control ni invisibles: el aviso a Claude los rechaza
  return Array.from(String(s)).filter(function(ch){
    var c = ch.codePointAt(0);
    return !(c <= 8 || c === 11 || c === 12 || (c >= 14 && c <= 31) || c === 127 || c === 173 || (c >= 0x200b && c <= 0x200f) ||
      (c >= 0x2028 && c <= 0x202e) || (c >= 0x2060 && c <= 0x206f) || (c >= 0xe000 && c <= 0xf8ff) || c === 0xfeff);
  }).join('');
}
function avBoton(accion, c, txt, st){
  var bloq = st && st.st !== '';
  return '<button type="button" class="sw-big' + (accion === 'copiar' ? ' alt' : '') + '" data-av="' + accion + '" data-clave="' + esc(c) + '"' + (bloq ? ' disabled' : '') + '>' + esc(txt) + '</button>';
}
function avResultado(st){ return st && st.msg ? '<p class="av-r ' + (st.st === 'mal' ? 'mal' : 'ok') + '" role="status">' + esc(st.msg) + '</p>' : ''; }
function avisarHTML(claves){
  var A = window.__art, lista = (claves || []).filter(function(c){ return c && A.enviadas[c]; });
  if(!lista.length) return '';
  return '<div class="av"><p class="av-k">Tu respuesta quedó guardada</p>' + lista.map(function(c){
    var s = avEstado(c), h = '<div class="av-b" data-clave="' + esc(c) + '">';
    if(lista.length > 1) h += '<div class="av-t">' + esc(avTitulo(c)) + '</div>';
    if(A.canal.room){
      h += avBoton('room', c, 'Avisar a Claude', s.room) + '<p class="av-h">Claude te va a pedir que confirmes.</p>' + avResultado(s.room);
    } else if(A.canal.com){
      h += avBoton('com', c, 'Avisarle a Claude con un comentario', s.com) + '<p class="av-h">Se deja un comentario en esta página y Claude lo lee. Puede llegar con demora.</p>' + avResultado(s.com);
    }
    h += '<p class="av-h">o volvé al chat y escribí “listo”</p>' + avBoton('copiar', c, 'Copiar respuesta', null) + (s.copia ? '<p class="av-r ok" role="status">' + esc(s.copia) + '</p>' : '');
    return h + '</div>';
  }).join('') + '</div>';
}
function avCopiar(txt, listo){
  function respaldo(){
    var t = document.createElement('textarea'); t.value = txt; t.setAttribute('readonly', ''); t.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
    document.body.appendChild(t); t.focus(); t.select();
    var ok = false; try{ ok = document.execCommand('copy'); }catch(e){}
    document.body.removeChild(t); listo(ok);
  }
  try{ if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).then(function(){ listo(true); }, respaldo); return; } }catch(e){}
  respaldo();
}
function avToque(accion, c){
  var A = window.__art, s = avEstado(c), txt = A.enviadas[c]; if(!txt) return;
  if(accion === 'copiar'){
    avCopiar(txt, function(ok){ s.copia = ok ? 'Copiado. Pegalo en el chat con Claude.' : 'No pude copiar. Seleccioná el texto a mano.'; avRepintar(); });
    return;
  }
  var K = accion === 'room' ? s.room : s.com;
  if(K.st !== '') return;   // un solo toque: no se duplica el aviso
  K.st = 'enviando'; K.msg = 'Mandando el aviso…'; avRepintar();
  var t = avLimpio(txt);
  function mal(e){ K.st = 'mal'; K.msg = 'No se pudo avisar. Volvé al chat y escribí “listo”.'; avRepintar(); try{ console.warn('aviso', e && e.code || e); }catch(_){} }
  try{
    if(accion === 'room'){
      var datos = new TextEncoder().encode(t).length < 2800
        ? {label: 'Respuesta a las tarjetas', tipo: 'respuesta_tarjetas', clave: c, texto: t}
        : {label: 'Respuesta a las tarjetas', tipo: 'respuesta_tarjetas', clave: c, nota: 'La respuesta está en respuestas/' + c};
      Promise.resolve(A.room.sendToClaudeSession(datos, {deliver: 'send', attachPresence: false, onStatus: function(x){
        if(x && x.state === 'sent'){ K.st = 'ok'; K.msg = 'Claude recibió el aviso.'; avRepintar(); }
        else if(x && x.state === 'failed') mal('failed');
      }})).then(function(){ if(K.st === 'enviando'){ K.st = 'ok'; K.msg = 'Aviso enviado. Si Claude te muestra un cartel para confirmar, aceptalo.'; avRepintar(); } }, mal);
    } else {
      A.comments.anchorFor(document.getElementById('home') || document.body)
        .then(function(a){ return A.comments.sendToClaude({anchor: a, text: avLimpio('respuesta a las tarjetas · ' + c + '\n' + txt)}); })
        .then(function(){ K.st = 'ok'; K.msg = 'Comentario enviado. Claude puede tardar un rato en contestar.'; avRepintar(); }, mal);
    }
  }catch(e){ mal(e); }
}
document.addEventListener('click', function(e){
  var b = e.target && e.target.closest ? e.target.closest('[data-av]') : null; if(!b || b.disabled) return;
  e.preventDefault(); e.stopPropagation();
  avToque(b.getAttribute('data-av'), b.getAttribute('data-clave'));
}, true);
// lo que otro dispositivo dejó marcado: se adopta una vez por clave, solo si la tanda sigue abierta aquí
var avAdoptadas = {};
function adoptarMarcasRemotas(){
  var rem = window.__art.marcasRemotas ? window.__art.marcasRemotas() : {}, cambio = false;
  Object.keys(rem).forEach(function(c){
    if(estado.marcas[c] || avAdoptadas[c]) return;
    avAdoptadas[c] = true;
    if(estado.filas.some(function(f){ return f.clave === c && f.estado === 'abierta'; })){ estado.marcas[c] = rem[c]; cambio = true; }
  });
  if(cambio){ try{ localStorage.setItem(CLAVE_MARCAS, JSON.stringify(estado.marcas)); }catch(e){} }
}
