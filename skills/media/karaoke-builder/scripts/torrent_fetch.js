// Fetcher de torrents — corre en la pestaña logueada de ultrastar-es.org (vía javascript_tool).
// Usa la sesión del navegador para bajar cada .torrent y lo POStea al puente local (127.0.0.1:8899),
// que lo escribe en watched/ para que qBittorrent lo ingiera. Los tokens salen de site_hits.txt.
// En runtime se reemplaza SONGS_PLACEHOLDER por [{name:"Artista - Título", token:"..."}].
async function fetchTorrents(songs){
  const out=[];
  for(const s of songs){
    try{
      const r=await fetch('/en/canciones/descargar/torrent/'+s.token,{credentials:'include'});
      if(!r.ok){ out.push('HTTP '+r.status+'  '+s.name); continue; }
      const b=await r.arrayBuffer();
      const magic=String.fromCharCode(...new Uint8Array(b).slice(0,11));
      if(magic.indexOf('d8:announce')!==0 && b.byteLength<50){ out.push('no-torrent  '+s.name); continue; }
      const p=await fetch('http://127.0.0.1:8899/save?name='+encodeURIComponent(s.name),{method:'POST',body:b});
      out.push((p.ok?'OK '+b.byteLength+'b':'bridge '+p.status)+'  '+s.name);
    }catch(e){ out.push('ERR '+e+'  '+s.name); }
    await new Promise(r=>setTimeout(r,300));
  }
  return out.join('\n');
}
return fetchTorrents(SONGS_PLACEHOLDER);
