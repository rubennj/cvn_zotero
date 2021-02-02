# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 15:30:54 2021

@author: Ruben
"""
from configparser import ConfigParser
from pathlib import Path
import subprocess
import shutil

config = ConfigParser()
config.read('config.txt')

PDFTK = config.get('paths', 'PDFTK')
DIR_DESTINO = config.get('paths', 'DIR_DESTINO')

# if input('Pulsa "s" para generar el PDF final. Ver lista_pdfs_a_juntar.txt ') != 's':
#     raise SystemExit('No se ha seleccionado "s"')
    
fichero_pdf_final = config.get('pdf', 'fichero_pdf_final')

with open(Path(DIR_DESTINO, 'lista_pdfs_a_juntar.txt')) as f:
    lista_pdfs = f.readlines()

lista_nomnbres_pdfs = ' '.join('"'+str(nombre)+'"' for nombre in lista_pdfs).replace('\n', '')

path_fichero_pdf_final = Path(DIR_DESTINO, fichero_pdf_final)
if path_fichero_pdf_final.exists():
    path_fichero_pdf_final.unlink()
    #{DIR_DESTINO}/{fichero_pdf_final}
subprocess.run(f'{PDFTK} {lista_nomnbres_pdfs} cat output meritos_CVN.pdf', capture_output=True)

#%% Borra directorio temporal de papers
# shutil.rmtree(Path(DIR_DESTINO, DIR_PAPERS))
