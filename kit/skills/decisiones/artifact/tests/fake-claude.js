/* Arnés de prueba: un `window.claude` falso con db, user, room y comments en memoria.
   Tiene la misma forma que la API real (claude.use(nombre) -> namespace o null) y deja
   inspeccionar lo escrito en `window.__fake`. Se configura por la query de la URL:
     ?db=null | ?room=null | ?comments=null   ese namespace resuelve null
     ?canroom=available|no_session|off         respuesta de room.canSendToClaudeSession()
     ?cancomment=available|off|no_session      respuesta de comments.canSendToClaude()
     ?write=0                                  user.can("data.write") resuelve false
     ?lat=150                                  demora (ms) de cada escritura en la base (para probar el doble toque)
     ?mudo=1                                   las suscripciones nunca contestan (prueba del tiempo de espera) */
(function () {
  const q = new URLSearchParams(location.search);
  const opt = (k, d) => (q.has(k) ? q.get(k) : d);
  const clon = o => JSON.parse(JSON.stringify(o));
  const store = new Map();
  const subs = new Set();
  const F = (window.__fake = { docs: store, escrituras: {}, enviados: [], comentarios: [], suscripciones: 0 });

  const snapDoc = path => ({
    id: path.split('/').pop(), exists: store.has(path),
    data: () => (store.has(path) ? clon(store.get(path)) : undefined),
    metadata: { fromCache: false, hasPendingWrites: false }
  });
  const docsDe = col => [...store.keys()].filter(k => k.startsWith(col + '/') && k.split('/').length === col.split('/').length + 1);
  function snapQuery(col, order, lim) {
    let ks = docsDe(col);
    if (order) ks.sort((a, b) => { const x = store.get(a)[order.f], y = store.get(b)[order.f]; return (x < y ? -1 : x > y ? 1 : 0) * (order.d === 'desc' ? -1 : 1); });
    if (lim) ks = ks.slice(0, lim);
    const docs = ks.map(snapDoc);
    return { docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata: { fromCache: false, hasPendingWrites: false } };
  }
  function notificar() { subs.forEach(s => s.emit()); }
  function suscribir(emit) {
    F.suscripciones++;
    if (opt('mudo', '0') === '1') return () => {};
    const s = { emit };
    subs.add(s); queueMicrotask(emit);
    return () => subs.delete(s);
  }
  function Query(col, order, lim) {
    return {
      orderBy: (f, d) => Query(col, { f, d }, lim), limit: n => Query(col, order, n), where: () => Query(col, order, lim),
      get: () => Promise.resolve(snapQuery(col, order, lim)),
      onSnapshot: (next) => suscribir(() => next(snapQuery(col, order, lim)))
    };
  }
  const demora = () => new Promise(r => setTimeout(r, Number(opt('lat', '150'))));
  const db = {
    doc: path => ({
      id: path.split('/').pop(), path,
      get: () => Promise.resolve(snapDoc(path)),
      set: async data => { await demora(); F.escrituras[path] = (F.escrituras[path] || 0) + 1; store.set(path, clon(data)); notificar(); },
      update: async data => { await demora(); store.set(path, Object.assign({}, store.get(path) || {}, clon(data))); notificar(); },
      delete: async () => { store.delete(path); notificar(); },
      onSnapshot: next => suscribir(() => next(snapDoc(path)))
    }),
    collection: col => Query(col)
  };
  F.seed = (path, data) => { store.set(path, clon(data)); notificar(); };

  const user = {
    isOwner: async () => true, canEdit: async () => true, id: async () => 'u_prueba',
    can: async n => (n === 'data.write' ? opt('write', '1') !== '0' : null),
    me: async () => ({ id: 'u_prueba', name: '', avatarUrl: '', color: '#888', email: null, isOwner: true, canEdit: true })
  };
  const room = {
    canSendToClaudeSession: async () => opt('canroom', 'available'),
    sendToClaudeSession: (data, options) => {
      F.enviados.push({ data: clon(data), options: { deliver: options && options.deliver } });
      setTimeout(() => options && options.onStatus && options.onStatus({ state: 'sent' }), 20);
      return Promise.resolve({ to: 'pane' });
    }
  };
  const comments = {
    canSendToClaude: async () => opt('cancomment', 'available'),
    anchorFor: async el => ({ anchor: 'a-' + (el && el.id) }),
    sendToClaude: async t => { F.comentarios.push(clon(t)); return { threadId: 't1', commentId: 'c1' }; }
  };
  const ns = { db, user, room, comments };
  window.claude = {
    use: async name => (opt('nada', '0') === '1' || opt(name, '') === 'null' || !(name in ns) ? null : ns[name])
  };
})();
