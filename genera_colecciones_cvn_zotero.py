# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 09:56:44 2021

@author: Ruben
"""
from configparser import ConfigParser

import yaml
from pyzotero import zotero

config = ConfigParser()
config.read('config.txt')


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

def crea_indice_cvn(fichero_indice):
    with open(fichero_indice, 'r', encoding='utf8') as file:
        try:
            indice = yaml.load(file, Loader = yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
    
    for id_capitulo in indice.keys():
        print(id_capitulo)
        bib_zotero.create_collections([{'name':id_capitulo, 'parentCollection':collection_cvn_id}])
        collection_cvn_capitulo_id = get_colletionID(bib_zotero, name=id_capitulo)
    
        if indice[id_capitulo] is not None:
            for id_subcapitulo in indice[id_capitulo]:
                print(id_subcapitulo)
                bib_zotero.create_collections([{'name':id_subcapitulo, 'parentCollection':collection_cvn_capitulo_id}])


LIBRARY_ID = keyring.get_password("zotero", "library_id") # la contraseña se tiene que añadir previamente en "Windows Credential Locker" usando el comando en CLI: "keyring set zotero library_id"
API_KEY = keyring.get_password("zotero", "api_key") # la contraseña se tiene que añadir previamente en "Windows Credential Locker" usando el comando en CLI: "keyring set zotero api_key"

COLECCION_CV_ZOTERO = config.get('zotero', 'COLECCION_CV_ZOTERO')

bib_zotero = zotero.Zotero(library_id=LIBRARY_ID, library_type='user', api_key=API_KEY)

bib_zotero.create_collections([{'name':COLECCION_CV_ZOTERO}])

collection_cvn_id = get_colletionID(bib_zotero, name=COLECCION_CV_ZOTERO)                

# Dado un indice de CVN en YAML crea la estructura como colecciones en Zotero
crea_indice_cvn('cvn_indice.yaml')
