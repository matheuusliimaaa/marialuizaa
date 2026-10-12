#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DO SITE - portfólio de ensaios newborn

COMO USAR
1. Coloque as fotos na pasta img/ seguindo este padrão (use nomes em minúsculas):

     img/<idade>/capa.webp                   capa do card de idade (~800 px de largura)
     img/<idade>/<tema>/1.webp ... 5.webp    fotos originais (qualidade máxima)
     img/<idade>/<tema>/1-thumb.webp ...     miniaturas (1000 a 1200 px de largura)

   Também funcionam .jpg, .jpeg e .png.
   Exemplo: img/nina-hasta-5/hada/1-thumb.webp

2. Rode no terminal, dentro desta pasta:   python build.py
3. Suba a pasta inteira para o Netlify Drop (ou para o GitHub).

PARA ADICIONAR UM TEMA NOVO
   Acrescente um bloco na lista TEMAS abaixo e rode o build.py de novo.
   Ele cria sozinho as pastas de fotos de cada idade para o tema novo.

O QUE O SITE FAZ COM AS FOTOS
   - Cards de idade (início):  usam img/<idade>/capa
   - Cards de tema:            usam a miniatura da foto 1 do tema
   - Grade da galeria:         usa as miniaturas (-thumb)
   - Ao clicar numa foto:      abre a original em tela cheia (só aí ela é baixada)
   - Se faltar alguma foto, aparece um quadrado de cor no lugar (nada quebra).
"""

import html as htmllib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ======================================================================
# CONFIGURAÇÃO
# ======================================================================

NOMBRE_SITIO = "Pequeños Retratos"      # nome que aparece no topo de todas as páginas

# True  = temas sem nenhuma foto naquela idade ficam escondidos do site
# False = aparecem com quadrado de cor (bom para ver o layout antes de ter as fotos)
OCULTAR_TEMAS_SIN_FOTOS = False

FOTOS_POR_TEMA = 5                       # o layout da galeria foi desenhado para 5 fotos
EXTENSIONES = ["webp", "jpg", "jpeg", "png"]

# slug = nome da pasta (sem acento, sem espaço) | titulo/etiqueta = texto que aparece no site
EDADES = [
    {"slug": "nina-hasta-5",    "etiqueta": "Niñas", "titulo": "Niña, hasta 5 meses",       "color": "#6B3F4B"},
    {"slug": "nino-hasta-5",    "etiqueta": "Niños", "titulo": "Niño, hasta 5 meses",       "color": "#3D6B6B"},
    {"slug": "nina-despues-5",  "etiqueta": "Niñas", "titulo": "Niña, después de 5 meses",  "color": "#9A7428"},
    {"slug": "nino-despues-5",  "etiqueta": "Niños", "titulo": "Niño, después de 5 meses",  "color": "#6F8064"},
]

# Para criar um tema novo, copie um bloco, troque os dados e rode o build.py
TEMAS = [
    {
        "slug": "hada",
        "nombre": "Hada",
        "color": "#8A9A7E",
        "desc": "Alas delicadas, flores y luz suave para un cuento entre hojas y jardín.",
    },
    {
        "slug": "sirena",
        "nombre": "Sirena",
        "color": "#3D6B6B",
        "desc": "Tonos de mar, conchas y velos que ondulan como agua en calma.",
    },
    {
        "slug": "principe",
        "nombre": "Príncipe",
        "color": "#6B3F4B",
        "desc": "Coronas pequeñas, capas y una luz cálida digna de la realeza.",
    },
]

# ======================================================================
# FUNÇÕES AUXILIARES
# ======================================================================

AVISOS = set()
_dircache = {}


def esc(s):
    return htmllib.escape(s, quote=True)


def listar(rel_dir):
    if rel_dir not in _dircache:
        full = os.path.join(ROOT, rel_dir)
        _dircache[rel_dir] = os.listdir(full) if os.path.isdir(full) else []
    return _dircache[rel_dir]


def achar_img(rel_dir, base):
    """Procura rel_dir/base.<ext>. Compara o nome exato (o GitHub e o Netlify
    diferenciam maiúsculas de minúsculas, o Windows e o Mac não)."""
    nomes = listar(rel_dir)
    for ext in EXTENSIONES:
        if f"{base}.{ext}" in nomes:
            return f"{rel_dir}/{base}.{ext}"
    for n in nomes:
        stem, _, ext = n.rpartition(".")
        if stem.lower() == base.lower() and ext.lower() in EXTENSIONES:
            AVISOS.add(f"Renomeie {rel_dir}/{n} para minúsculas ({base}.{ext.lower()}); "
                       f"online o arquivo não seria encontrado.")
    return None


def fotos_do_tema(edad, tema):
    """Lista de 5 itens: {'thumb':..., 'full':...} ou None se a foto não existe."""
    pasta = f"img/{edad['slug']}/{tema['slug']}"
    saida = []
    for i in range(1, FOTOS_POR_TEMA + 1):
        orig = achar_img(pasta, str(i))
        thumb = achar_img(pasta, f"{i}-thumb")
        if not orig and not thumb:
            saida.append(None)
            continue
        if not thumb:
            AVISOS.add(f"{pasta}/{i}: falta a miniatura ({i}-thumb); a grade vai usar a "
                       f"original, que é mais pesada.")
        if not orig:
            AVISOS.add(f"{pasta}/{i}: falta a original; a ampliação vai usar a miniatura.")
        saida.append({"thumb": thumb or orig, "full": orig or thumb})
    return saida


def tem_fotos(edad, tema):
    return any(fotos_do_tema(edad, tema))


def temas_visiveis(edad):
    if OCULTAR_TEMAS_SIN_FOTOS:
        return [t for t in TEMAS if tem_fotos(edad, t)]
    return TEMAS


def escrever(rel_path, conteudo):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(conteudo)


# ======================================================================
# TEMPLATES
# ======================================================================

def head(titulo, up, galeria=False):
    js = f'<script src="{up}js/lightbox.js" defer></script>\n' if galeria else ""
    return f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,500;0,600;1,400&family=Jost:wght@300;400;500&display=swap">
<link rel="stylesheet" href="{up}css/style.css">
{js}</head>
<body>
"""


FOOT = """<footer><div class="wrap">Portafolio de sesiones newborn &middot; hecho con cariño</div></footer>
</body>
</html>
"""


def cabecalho(up):
    return (f'<div class="site-header wrap"><a class="brand" href="{up}index.html">'
            f'{esc(NOMBRE_SITIO)}</a></div>\n')


def migalhas(itens):
    """itens: lista de (texto, href ou None)"""
    partes = []
    for texto, href in itens:
        if href:
            partes.append(f'<a href="{href}">{esc(texto)}</a>')
        else:
            partes.append(f'<span class="current">{esc(texto)}</span>')
    sep = '<span class="sep">/</span>'
    return f'<div class="crumbs wrap">{sep.join(partes)}</div>\n'


# ----------------------------------------------------------------------
# Página 1: início (cards de idade)
# ----------------------------------------------------------------------
def pagina_inicio():
    cards = ""
    for e in EDADES:
        capa = achar_img(f"img/{e['slug']}", "capa")
        if capa:
            media = (f'<div class="age-media"><img src="{capa}" alt="" '
                     f'decoding="async"></div>')
        else:
            media = '<div class="age-media"></div>'   # sem capa: quadrado de cor
        cards += f"""
        <a class="age-card" style="--card-color:{e['color']}" href="{e['slug']}/index.html">
          {media}
          <div class="age-body">
            <div class="eyebrow">{esc(e['etiqueta'])}</div>
            <h2>{esc(e['titulo'])}</h2>
          </div>
        </a>"""

    html = (head(f"{NOMBRE_SITIO} - Sesiones Newborn", "") + cabecalho("") +
            """<div class="hero wrap">
          <h1>Retratos que nacen con tu bebé</h1>
          <p>Elige la edad para descubrir las sesiones temáticas disponibles y ver los estilos de fotos de cada una.</p>
        </div>
        <div class="wrap">
          <div class="grid-2">""" + cards + """
          </div>
        </div>""" + FOOT)
    escrever("index.html", html)


# ----------------------------------------------------------------------
# Página 2: temas de uma idade
# ----------------------------------------------------------------------
def pagina_idade(e):
    cards = ""
    for t in temas_visiveis(e):
        primeira = fotos_do_tema(e, t)[0]
        if primeira:
            miniatura = (f'<div class="theme-thumb"><img src="../{primeira["thumb"]}" alt="" '
                         f'loading="lazy" decoding="async"></div>')
            cls = "theme-card has-img"
        else:
            miniatura, cls = "", "theme-card"
        cards += f"""
        <a class="{cls}" style="--card-color:{t['color']}" href="{t['slug']}.html">
          {miniatura}
          <div class="theme-body">
            <span class="tag"></span>
            <h2>{esc(t['nombre'])}</h2>
            <p>{esc(t['desc'])}</p>
          </div>
        </a>"""

    html = (head(f"{e['titulo']} - Elige la sesión", "../") + cabecalho("../") +
            migalhas([("Inicio", "../index.html"), (e['titulo'], None)]) +
            f"""<div class="page-title wrap">
          <h1>{esc(e['titulo'])}</h1>
          <p>Elige el tema de la sesión para ver un ejemplo de las fotos incluidas.</p>
        </div>
        <div class="wrap">
          <div class="grid-3">""" + cards + """
          </div>
        </div>""" + FOOT)
    escrever(f"{e['slug']}/index.html", html)


# ----------------------------------------------------------------------
# Página 3: galeria com 5 fotos
# ----------------------------------------------------------------------
def pagina_galeria(e, t):
    fotos = fotos_do_tema(e, t)
    itens = ""
    for i, f in enumerate(fotos, 1):
        if f:
            alt = esc(f"Sesión {t['nombre']}, {e['titulo']}, foto {i}")
            carga = 'loading="eager"' if i <= 2 else 'loading="lazy"'
            itens += (f'<a class="ph ph-{i}" href="../{f["full"]}" aria-label="Ampliar foto {i}">'
                      f'<img src="../{f["thumb"]}" alt="{alt}" {carga} decoding="async"></a>\n')
        else:
            itens += f'<div class="ph ph-{i}">Foto {i}</div>\n'

    dica = ('<p class="gallery-hint">Toca una foto para verla en grande</p>'
            if any(fotos) else "")

    html = (head(f"Sesión {t['nombre']} - {e['titulo']}", "../", galeria=True) + cabecalho("../") +
            migalhas([("Inicio", "../index.html"), (e['titulo'], "index.html"), (t['nombre'], None)]) +
            f"""<div class="page-title wrap">
          <h1>Sesión {esc(t['nombre'])}</h1>
          <p>{esc(t['desc'])}</p>
        </div>
        <div class="wrap">
          {dica}
          <div class="gallery" style="--card-color:{t['color']}">
            {itens}
          </div>
          <a class="back-link" href="index.html">Volver a los temas de {esc(e['titulo'])}</a>
        </div>""" + FOOT)
    escrever(f"{e['slug']}/{t['slug']}.html", html)


# ======================================================================
# PRINCIPAL
# ======================================================================

def limpar_html_antigos(e):
    """Apaga os .html antigos da pasta da idade (assim um tema removido some do site)."""
    pasta = os.path.join(ROOT, e["slug"])
    if os.path.isdir(pasta):
        for nome in os.listdir(pasta):
            if nome.endswith(".html"):
                os.remove(os.path.join(pasta, nome))


def main():
    # cria as pastas de fotos de cada idade/tema para você saber onde colocar
    for e in EDADES:
        for t in TEMAS:
            os.makedirs(os.path.join(ROOT, "img", e["slug"], t["slug"]), exist_ok=True)

    pagina_inicio()
    paginas = 1
    total_ok = total_slots = 0
    sem_nenhuma, incompletos = [], []

    for e in EDADES:
        limpar_html_antigos(e)
        pagina_idade(e)
        paginas += 1
        for t in TEMAS:
            fotos = fotos_do_tema(e, t)
            achadas = sum(1 for f in fotos if f)
            total_ok += achadas
            total_slots += FOTOS_POR_TEMA
            rotulo = f"{e['slug']}/{t['slug']}"
            if achadas == 0:
                sem_nenhuma.append(rotulo)
            elif achadas < FOTOS_POR_TEMA:
                incompletos.append(f"{rotulo} ({achadas}/{FOTOS_POR_TEMA})")
            if OCULTAR_TEMAS_SIN_FOTOS and achadas == 0:
                continue
            pagina_galeria(e, t)
            paginas += 1

    print(f"Site gerado: {paginas} páginas.")
    print(f"Fotos encontradas: {total_ok} de {total_slots}.")
    if incompletos:
        print("\nTemas incompletos:")
        for r in incompletos:
            print("  -", r)
    if sem_nenhuma:
        print(f"\nTemas ainda sem fotos ({len(sem_nenhuma)}):")
        for r in sem_nenhuma:
            print("  -", r)
    if AVISOS:
        print("\nAvisos:")
        for a in sorted(AVISOS):
            print("  !", a)


if __name__ == "__main__":
    main()
