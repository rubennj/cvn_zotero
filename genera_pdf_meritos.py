# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 16:41:17 2018

@author: ruben
"""
import re
from pathlib import Path
import shutil
import subprocess
import filecmp
from configparser import ConfigParser
import textwrap

from reportlab.pdfgen import canvas
from pyzotero import zotero
from PyPDF2 import PdfFileReader
import pandas as pd

config = ConfigParser()
config.read('config.txt')

ZOTERO_STORAGE = config.get('paths', 'ZOTERO_STORAGE')
PDFTK = config.get('paths', 'PDFTK')
DIR_DESTINO = config.get('paths', 'DIR_DESTINO')
STYLE_ZOTERO = config.get('zotero', 'STYLE_ZOTERO')

def clean_filename(filename):
    valid_chars = '-_.() '
    filename_cleaned = ''.join(c for c in filename if c.isalnum() or c in valid_chars).rstrip()

    return filename_cleaned

def get_colletionID(bib_zotero, name):
    collections = bib_zotero.collections()
    for collection in collections:
        if collection['data']['name'] == name:
            print(f"Colección: {collection['data']['name']}, key:{collection['key']}")
            key = collection['key']
            return key
        else:
            key = None

    return key

def lista_items_zotero(bib_zotero, items_zotero, seccion):
    lista_items = []
    for item in items_zotero:
        if item['data']['itemType'] != 'attachment':
            año = re.findall(r"\d{4}", item['data']['date'])[0]
            titulo = item['data']['title']
            tipo = item['data']['itemType']
#            
            if tipo == 'conferencePaper':
                publicador = item['data']['conferenceName']
            elif tipo == 'bookSection':
                publicador = item['data']['publisher']
            else:
                publicador = item['data']['publicationTitle']
            
            # Busca hijos del elemento, normalmente un .pdf
            lista_hijos = bib_zotero.children(item['key'])
            lista_hijos_pdf_key = [hijo['data']['key'] for hijo in lista_hijos if hijo['data']['contentType'] == 'application/pdf']
            texto_referencia = texto_referencia_item(bib_zotero, item)
            
            lista_items.append({'año':año, 'titulo':titulo, 'seccion':seccion,
                                'publicador':publicador,
                                'lista_hijos_pdf_key':lista_hijos_pdf_key,
                                'texto_referencia':texto_referencia
                                })
    
    return lista_items

def copia_pdfs_item(item, directorio):
    numero_pdf = 1
    for key in item.lista_hijos_pdf_key:
        nombre_archivo = clean_filename(f'{item.año} - {item.seccion[:2]} - {item.publicador[:40]} - {item.titulo[:40]}_{numero_pdf}.pdf')

        path_pdf_src = sorted(Path(ZOTERO_STORAGE, key).glob('*.pdf'))[0]
    
        print('\n Copiando desde Zotero', nombre_archivo)
        shutil.copy(src=path_pdf_src, dst=Path(directorio, nombre_archivo))
        numero_pdf += 1

def texto_referencia_item(bib_zotero, item, style=STYLE_ZOTERO):
    bib_zotero.add_parameters(content='bib', style=style)
    text = bib_zotero.item(item['data']['key'])[0]
    
#    text = re.sub('\n', '', text)
    text = re.sub('<[^<]+?>', '', text)#.split(']')[1].strip(' ')

    return text

def lee_num_pags_pdf(pdf_filename):
    pdftk_output = subprocess.run(f'{PDFTK} "{pdf_filename}" dump_data', stdout=subprocess.PIPE).stdout.decode()
    linea_num_pags = [linea for linea in pdftk_output.split('\n') if 'NumberOfPages' in linea][0]
    
    return int(linea_num_pags.split(':')[1])

def elimina_pdfs_duplicados(path_directorio):
    for paper_src in path_directorio.glob('*.pdf'):
        for paper in path_directorio.glob('*.pdf'):
            try:
                if filecmp.cmp(paper_src, paper) and paper_src != paper:
                    print('\n Borrando duplicado', paper)
                    paper.unlink()
            except FileNotFoundError:
                pass

def pdf2txt(fname):
    PDF = PdfFileReader(open(fname, 'rb'))
    
    text = ''
    for page in PDF.pages:
        text += page.extractText()

    return text

def genera_portadas_secciones(lista_secciones):
    for seccion in lista_secciones:
        dir_seccion = Path(DIR_DESTINO, seccion)
        
        print('Genera portada:', seccion)
        
        if seccion[2] == ' ': # Capitulo
            num_seccion = seccion[:1]
            texto_portada = seccion
        else: # Subcapítulo
            num_seccion = seccion[:4].replace('.', '_')
            texto_portada = seccion[5:]
        
        c = canvas.Canvas(str(dir_seccion.joinpath('0_portada_' + num_seccion + '.pdf')))
        
        t = c.beginText()
        t.setFont('Helvetica-Bold', 48)
        t.setCharSpace(3)
        t.setTextOrigin(50, 700)
        t.textLines('\n'.join(textwrap.wrap(texto_portada, 16)))
        c.drawText(t)
        c.save()
        
#%% Inicializa variables Zotero
LIBRARY_ID = keyring.get_password("zotero", "library_id") # la contraseña se tiene que añadir previamente en "Windows Credential Locker" usando el comando en CLI: "keyring set zotero library_id"
API_KEY = keyring.get_password("zotero", "api_key") # la contraseña se tiene que añadir previamente en "Windows Credential Locker" usando el comando en CLI: "keyring set zotero api_key"

bib_zotero = zotero.Zotero(library_id=LIBRARY_ID, library_type='user', api_key=API_KEY)

DIR_PAPERS = config.get('paths', 'DIR_PAPERS')

COLECCION_CV_ZOTERO = config.get('zotero', 'COLECCION_CV_ZOTERO')
COLECCIONES_PAPERS_ZOTERO = config.get('zotero', 'COLECCIONES_PAPERS_ZOTERO')
COLECCIONES_QUITAR_ZOTERO = config.get('zotero', 'COLECCIONES_QUITAR_ZOTERO')

#%% Copia pdfs de secciones de CV en Zotero (excepto las publicaciones)
secciones_cv = bib_zotero.all_collections(
        get_colletionID(bib_zotero, name=COLECCION_CV_ZOTERO))

for seccion in secciones_cv:
    path_seccion = Path(DIR_DESTINO, seccion['data']['name'])
    if path_seccion.exists():
        shutil.rmtree(path_seccion)
    path_seccion.mkdir(parents=True)

secciones_pubs_zotero = COLECCIONES_PAPERS_ZOTERO.split(' - ')
secciones_quitar_zotero = COLECCIONES_QUITAR_ZOTERO.split(' - ')

secciones_cv_sin_pubs = [seccion for seccion in secciones_cv if seccion['data']['name'] not in (secciones_pubs_zotero or secciones_quitar_zotero)]

# raise SystemExit

for seccion in secciones_cv_sin_pubs:
    path_seccion = Path(DIR_DESTINO, seccion['data']['name'])

    pdfs_secciones_cv = bib_zotero.everything(bib_zotero.collection_items(seccion['key']))
    
    for item in pdfs_secciones_cv:
        nombre_archivo = item['data']['filename']

        path_pdf_src = sorted(Path(ZOTERO_STORAGE, item['key']).glob('*.pdf'))[0]
    
        print('\n Copiando desde Zotero', nombre_archivo)
        shutil.copy(src=path_pdf_src, dst=path_seccion.joinpath(nombre_archivo))

#%% Lee items de referencias Zotero (publicaciones)
if Path(DIR_DESTINO, DIR_PAPERS).exists():
    shutil.rmtree(Path(DIR_DESTINO, DIR_PAPERS))
Path(DIR_DESTINO, DIR_PAPERS).mkdir(parents=True)

path_pdf_enteros = Path(DIR_DESTINO, DIR_PAPERS, 'enteros')
path_pdf_enteros.mkdir(parents=True)

items = []
for seccion_pubs_zotero in secciones_pubs_zotero:
    items_zotero = (bib_zotero.everything(
            bib_zotero.collection_items(
            get_colletionID(bib_zotero, name=seccion_pubs_zotero))))
    
    items.extend(lista_items_zotero(bib_zotero, items_zotero, seccion_pubs_zotero))

items_df = pd.DataFrame(items)

#%% Copia desde Zotero los pdfs de la Colección
for _, item in items_df.iterrows():
    copia_pdfs_item(item, path_pdf_enteros)

elimina_pdfs_duplicados(path_pdf_enteros)

#%% Genera fichero texto con listado referencias
with open(Path(DIR_DESTINO, 'lista_referencias.txt'), 'w', encoding='utf-8') as f:
    seccion_anterior = ''
    for _, item in items_df.iterrows():
        if item.seccion != seccion_anterior:
            f.write(item.seccion + '\n')
        seccion_anterior = item.seccion
        
        f.write(item.texto_referencia + item.año + item.titulo + '\n')

#%% Genera mini pdfs con 1º y ult. páginas de cada publicación
for paper in path_pdf_enteros.glob('*.pdf'):
    # Evita 1ª página de 
    if 'INTERNATIONAL CONFERENCE ON CONCENT' in paper.name and pdf2txt(str(paper)).find('AIP Conf. Proc.') != -1:
        primera_hoja = 2
    else:
        primera_hoja = 1
    
    if lee_num_pags_pdf(paper) > 1:
        comando = f'{PDFTK} "{paper}" cat {primera_hoja} r1 output "{DIR_DESTINO}/{DIR_PAPERS}/{paper.stem+"_mini"+paper.suffix}"'
    else: # Si solo hay 1 pagina, no incluye la 1º y la ultimo (que la duplicaría)
        comando = f'{PDFTK} "{paper}" cat output "{DIR_DESTINO}/{DIR_PAPERS}/{paper.stem+"_mini"+paper.suffix}"'
    
    subprocess.run(comando)

#%% Copia archivos de publicaciones a carpetas de CV
for paper in Path(DIR_DESTINO, DIR_PAPERS).glob('*.pdf'):
    destino = [seccion for seccion in secciones_pubs_zotero if paper.name[7:9] in seccion][0]
    shutil.copy(src=paper, dst=Path(DIR_DESTINO, destino))
    print(f'\n Copiando a CV {paper.name} en {destino}')

#%% Genera portadas de cada sección y fichero con la lista de pdfs a juntar
lista_secciones = sorted([seccion['data']['name'] for seccion in secciones_cv])

genera_portadas_secciones(lista_secciones)

lista_pdfs = []
for seccion in lista_secciones:
    lista_pdf_seccion = list(Path(DIR_DESTINO, seccion).glob('*.pdf'))
    if len(lista_pdf_seccion) > 1 or seccion[2] == ' ': # si solo hay un fichero (portada) está vacío y no lo copia. Sí lo copia si es capítulo
        for nombre in lista_pdf_seccion:
            lista_pdfs.append(nombre)

lista_pdfs = sorted(lista_pdfs)
with open(Path(DIR_DESTINO, 'lista_pdfs_a_juntar.txt'), 'w') as f:
    for pdf in lista_pdfs:
        f.write(str(pdf) + '\n')
