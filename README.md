# cvn_zotero
Conjunto de scripts que generan un pdf con los contenidos del CVN que los justifican.

* El script `genera_colecciones_cvn_zotero.py` crea el árbol de colecciones de CVN en Zotero. Éste deberá ser rellenado manualmente con los correspondientes contenidos.
* El script `genera_pdf_meritos.py` crea un directorio de pdfs con contenidos de Zotero incluyendo portadas de colecciones/subcolecciones del CVN.
* El script `genera_pdf_todo_junto.py` junta los pdfs creados anteriormente en un único fichero pdf.

## Comentarios
* Tanto la key de la API de Zotero como el ID de la librería de Zotero se leen encriptados usando `keyring`.
Se tienen que añadir previamente en "Windows Credential Locker" o equivalente usando el comando en consola:
> `keyring set zotero library_id`  
> `keyring set zotero api_key`
* La librería `pyzotero` realmente lee ficheros y colecciones de Zotero on-line. Cualquier cambio en el programa se tiene que actualizar con el repositorio de Zotero.
* Todos los documentos se han de guardar como ficheros pdf sin contenedor excepto los artículos, que los scripts volcarán tomando la 1ª y última páginas.
* "cvn_indice.yaml" que contiene el árbol de colecciones del CVN está sacado de "ayudaPdf.pdf" (descargado de la ayuda de la web CVN).
* Ojo a nombres de fichero/path muy largos, pueden fallar!

## Nota
* Se pueden exportar los papers desde Zotero en BibTex a CVN (elemento - botón derecho - exportar elemento - formato - BibTex), lo que que permite rellenar los campos del CVN de forma automática en la aplicación.

## Instalación
* Clonar el repositorio e instalar las siguientes dependencias  
`conda install reportlab, keyring`  
`conda install pypdf2 -c conda-forge`  
`pip install pyzotero`
