# cvn_zotero
Conjunto de scripts que generan un pdf con los contenidos del CVN que los justifican.

* El script `genera_colecciones_cvn_zotero.py` crea el árbol de colecciones de CVN en Zotero. Éste deberá ser rellenado manualmente con los correspondientes contenidos.
* El script `genera_pdf_meritos.py` crea un directorio de pdfs con contenidos de Zotero incluyendo portadas de colecciones/subcolecciones del CVN.
* El script `genera_pdf_todo_junto.py` junta los pdfs creados anteriormente en un único fichero pdf.

Tanto la key de la API de Zotero como el ID de la librería de Zotero se almacenan encriptados usando `keyring`
Se tienen que añadir previamente en "Windows Credential Locker" o equivalente usando el comando en consola:
> "keyring set zotero library_id"  
> "keyring set zotero api_key"

## Comentarios
* La librería `pyzotero` realmente de Zotero on-line. Cualquier cambio en el programa se tiene que actualizar con el repositorio de Zotero
* Ojo a nombres de fichero muy largos, pueden fallar!
* Todos los documentos se han de guardar como ficheros pdf sin contenedor excepto los artículos, que se volcarán tomando la 1ª y última páginas.
* "cvn_indice.yaml" que contiene el árbol de colecciones del CVN está sacado de "ayudaPdf.pdf" (descargado de la ayuda de la web CVN)

## Nota
* Se pueden exportar los papers desde Zotero en bibtex a CVN de forma automática, lo que que permite rellenar los campos de forma automática en la aplicación de CVN.

Instalacion
-----------
conda install reportlab, 
conda install pypdf2 -c conda-forge
pip install pyzotero
