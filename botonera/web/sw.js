// Solo avisos: no cachea nada, asi un deploy nunca deja una pagina vieja.
self.addEventListener('install', function(){ self.skipWaiting(); });
self.addEventListener('activate', function(e){ e.waitUntil(self.clients.claim()); });

self.addEventListener('push', function(e){
  var m = {};
  try{ m = e.data ? e.data.json() : {}; }catch(err){}
  e.waitUntil(self.registration.showNotification(m.titulo || 'Botonera', {
    body: m.cuerpo || '',
    tag: m.tag || 'aviso',
    renotify: true,
    icon: '/icon-192.png',
    badge: '/icon-192.png'
  }));
});

self.addEventListener('notificationclick', function(e){
  e.notification.close();
  e.waitUntil(self.clients.matchAll({type: 'window', includeUncontrolled: true}).then(function(lista){
    for(var i = 0; i < lista.length; i++){
      if(new URL(lista[i].url).pathname === '/' && lista[i].focus) return lista[i].focus();
    }
    return self.clients.openWindow('/');
  }));
});
