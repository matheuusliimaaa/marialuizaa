from pathlib import Path
import json, html
ROOT=Path(__file__).resolve().parent
EDADES=[('nina-hasta-5','Niña, hasta 5 meses'),('nino-hasta-5','Niño, hasta 5 meses'),('nina-despues-5','Niña, después de 5 meses'),('nino-despues-5','Niño, después de 5 meses')]
def esc(x):return html.escape(str(x),quote=True)
def page(title,body,up=''):
 return f'''<!doctype html><html lang="es-MX"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Pequeños Retratos</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500&amp;family=Jost:wght@300;400;500&amp;display=swap"><link rel="stylesheet" href="{up}css/style.css"><link rel="stylesheet" href="{up}css/mosaicos.css"><script src="{up}js/mosaicos.js" defer></script></head><body><header class="site-header wrap"><a class="brand" href="{up}index.html">Pequeños Retratos</a></header><main class="wrap">{body}</main><footer>Portafolio de sesiones newborn · hecho con cariño</footer><dialog class="mosaic-dialog" aria-label="Sesión ampliada"><button class="close" aria-label="Cerrar">×</button><p class="status" role="status">Cargando imagen…</p><img class="original" alt=""><p class="caption"></p></dialog></body></html>'''
def build():
 data=json.loads((ROOT/'ensaios.json').read_text(encoding='utf-8'))
 cards=''
 for slug,title in EDADES:
  cover=next((f'img/{slug}/capa.{e}' for e in ['webp','jpg','jpeg','png'] if (ROOT/f'img/{slug}/capa.{e}').is_file()),None)
  media=f'<img src="{cover}" alt="{esc(title)}">' if cover else ''
  cards+=f'<a class="age-card" href="{slug}/index.html"><div class="age-media">{media}</div><div class="age-body"><h2>{esc(title)}</h2></div></a>'
 (ROOT/'index.html').write_text(page('Sesiones newborn',f'<section class="hero"><h1>Retratos que nacen con tu bebé</h1><p>Elige la edad para descubrir nuestras sesiones.</p></section><div class="grid-2">{cards}</div>'),encoding='utf-8')
 for slug,title in EDADES:
  cards=''
  for e in data:
   if slug not in e['idades']:continue
   for key in ['capa','original']:
    path=ROOT/e[key]
    if not path.is_file() or ROOT not in path.resolve().parents:raise ValueError('Imagem ausente ou caminho inválido: '+e[key])
   cards+=f'''<article class="theme-card has-img"><button class="mosaic-trigger" data-original="../{esc(e['original'])}" data-title="{esc(e['nome'])}" aria-label="Ampliar sesión {esc(e['nome'])}"><img src="../{esc(e['capa'])}" alt="{esc(e['nome'])}, mosaico de cuatro poses" loading="lazy"><span>Ver sesión en grande ⤢</span></button><div class="theme-body"><h2>{esc(e['nome'])}</h2><p>{esc(e['descricao'])}</p></div></article>'''
  if not cards:cards='<p class="empty">Pronto tendremos nuevas sesiones disponibles.</p>'
  folder=ROOT/slug;folder.mkdir(exist_ok=True)
  (folder/'index.html').write_text(page(title,f'<a class="back-link" href="../index.html">← Volver a las edades</a><section class="page-title"><h1>{esc(title)}</h1><p>Toca la imagen para ver las cuatro poses de la sesión.</p></section><div class="grid-3">{cards}</div>','../'),encoding='utf-8')
 print('Site atualizado: página inicial + 4 páginas de idades. Ensaios:',len(data))
if __name__=='__main__':build()
