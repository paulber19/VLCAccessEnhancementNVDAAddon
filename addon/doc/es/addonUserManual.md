# Reproductor multimedia VLC: complementos de accesibilidad - manual del usuario #


*	Autores:  Paulber19 con la participación muy activa de  Daniel Poiraud.
*	Descargar versión 1.3.1:
	* [servidor de descarga 1][1]
	* [servidor de descarga 2][2]


Este complemento añade varias órdenes para facilitar la reproducción de medios con NVDA.  


Esta versión es compatible con versiones de VLC superiores a 3.0.

Es incompatible con las versiones NVDA inferiores a 2018.3.2.

## Gestos de Entrada proporcionados por el complemento: ##
*	NVDA+Control+H: Mostrar ayuda sobre posibles órdenes en la ventana principal,
*	coma: anunciar la duración ya reproducido del medio,
*	punto: anunciar la duración restante del medio para ser reproducido,
*	guión: anunciar la duración total del medio,
*	n tilde: anunciar la velocidad de reproducción,
*	Control + coma: Mostrar el cuadro de diálogo para establecer el tiempo y mover el cursor de reproducción en este tiempo,
*	NVDA+control+f5: guardar el tiempo actual del medio para una futura reanudación de la reproducción,
*	NVDA+control+f6: reanudar la reproducción del tiempo registrado para este medio,
* alt+control+r: reanudar la reproducción interrumpida en la posición memorizada por VLC.


Estos gestos de entrada se pueden modificar con el cuadro de diálogo "Gestos de entrada" de NVDA.

## Órdenes de teclado propios a VLC vocalizado por el complemento: ##
Algunos atajos predeterminados de VLC son problemáticos y deben modificarse. Son:

*	Las órdenes de teclado "cierra corchete" y "abre corchete" para la velocidad de reproducción un poco más rápido o un poco más lento,   porque no se pueden utilizar en el teclado francés. Serán reemplazados por "I" y "U". Nota del traductor: Estos mismos serán reemplazados en el teclado español.
*	Las órdenes de teclado "control+alt+flecha derecha o izquierda" para avanzar o retroceder de 5 minutos el medio, porque no funciona en algunas configuraciones. Se reemplazarán por "control+mayúscula+flecha derecha o izquierda".
*	Las órdenes de teclado "+" y "-" teclado alfanumérico para cambiar la velocidad de reproducción, porque están mal colocados. Serán reemplazados por "o" y "y".


Para configurar estos nuevos atajos, debe modificar el archivo de configuración "vlcrc" de VLC como sigue:

*	después de instalar VLC o eliminar la carpeta de configuración de VLC, inícielo una vez con el atajo del escritorio o reproduciendo un medio y luego deténgalo.
*	pulsar "NVDA+n" y en el submenú "Preferencias", seleccione el submenú "Reproductor multimedia VLC: complementos de accesibilidad - opciones",
*	por último, pulsa el botón "Modificar los atajos del Reproductor multimedia VLC".


Aquí están las órdenes de teclado que este complemento vocaliza:

*	Y: decrementar la velocidad de reproducción.
*	U: decrementar un poco la velocidad de reproducción.
*	I: incrementar un poco la velocidad de reproducción.
*	O: incrementar la velocidad de reproducción.
*	abrir exclamación: retorno a la velocidad normal,
*	m: silenciar o desilenciar el sonido,
*	espacio:  iniciar o pausar la reproducción,
* s: detener el medio,
*	l: alternar el estado de repetición del medios entre   repetir todo, repetir el medio actual, no repetir,
*	mayúscula + flecha derecha o izquierda: avanzar o retroceder la duración reproducido del medio de 3 segundos,
*	alt + flecha  derecha o izquierda: avanzar o retroceder la duración reproducido del medio de 10 segundos,
*	control + flecha derecha o izquierda: avanzar o retroceder la duración reproducido del medio de 1 minuto,
*	control mayúscula + flecha derecha o izquierda: avanzar o retroceder la duración reproducido del medio de 5 minutos.
*	flecha arriba o abajo: subir o bajar el volumen,
*	control flecha arriba o abajo: subir o bajar el volumen,
* espacio: poner en pausa el medio o reanudar la reproducción.


Para no molestar al usuario, el tiempo reproducido automáticamente solo se vocaliza cuando el medio está en pausa o se está reproduciendo con el sonido silenciado.

Se realiza una comprobación para evitar un salto fuera de los límites del medio. Por ejemplo, No es posible hacer un salto de 5 minutos Si quedan  sólo 2 minutos restantes para reproducir o bien retroceder de 10 segundos si la duración ya  reproducida es de 3 segundos.  

El estado "sonido silenciado" es señalado al iniciar la reproducción.

El nivel de volumen se anuncia en cada cambio.

El pasaje en pausa es anunciado.

## Script Mostrar el cuadro de diálogo para establecer el tiempo y mover el cursor de reproducción en este tiempo ##
VLC ofrece la posibilidad de utilizar el atajo "control+t" para moverse a un tiempo específico  del medio. Pero el cuadro de diálogo que se presenta plantea problemas de accesibilidad.

Este complemento ofrece otra solución  (preferible) para moverse a un tiempo con el atajo "control+coma".  
Este atajo presenta un cuadro de diálogo que  te permite configurar el tiempo (horas, minutos, segundos) para colocar el cursor de reproducción del medio, dentro de los  límites de la duración totale del medio disminuido de 5 segundos.  


## Reanudar la reproducción ##
Para reanudar la reproducción de un medio, son posibles dos soluciones:
### Primera solución ###
VLC almacena la posición de  la reproducción actual cuando esta se interrumpe, es decir, ya sea seguido de una órden de VLC, ya sea al salir de la aplicación.

Cuando se reinicia el medio, VLC muestra la posibilidad de reanudar en la barra de estado por un tiempo muy corto (unos segundos) y al pulsar el atajo "alt+r", la reproducción se reinicia en la posición registrada para este medio.

Como esto es difícil de usar  por la gente ciega, este complemento proporciona un script que permite que la reproducción se reanude en la posición registrada por VLC sin tener esta restricción de tiempo.

Cuando se reinicia un medio y VLC ha registrado, para este medio, una posición para reanudar la reproducción, el mensaje de voz "Reanudar la reproducción alt+control+r" lo indica. Al utilizar el gesto de entrada "alt+control+r",  la reproducción del medio continúa en la posición registrada.

Este gesto de entrada puede ser modificado por el usuario.


### Segunda solución ###
Esta segunda solución requiere en primer lugar marcar una posición para reanudar la reproducción con el gesto de entrada "nvda+control+f5".
Es preferible de poner en pausa  el medio de antemano.
No tienes que salir de VLC para reanudar la reproducción de este medio.

Para reanudar la reproducción de un medio, la órdenes de teclado "NVDA+control+f6" reiniciará la reproducción en la posición registrada por  el complemento para este medio.

Esta posición se guarda en el archivo de configuración del complemento y para cada medio se registra el nombre del medio y la posición asociada. En este archivo solo se guardan los medios abiertos más recientemente.

Advertencia: el nombre del medio es único en este archivo. Si dos archivos con el mismo nombre están en carpetas diferentes, solo se conservará el último registro para ese nombre.

## Complementos tecnicos ##
### Reinicialización de la configuración de VLC ###
Cuando VLC arranca por primera vez, crea en la carpeta de configuración de usuario de Windows,  la carpeta "vlc" que contiene los archivos de configuración de VLC.

Para restablecer la configuración de VLC sin tener que reinstalarlo, simplemente elimine esta carpeta.

Para facilitar esto, el complemento ofrece el botón "Eliminar la carpeta de configuración de VLC" en el cuadro de diálogo de configuración del complemento.

Después, si el botón "Modificar los atajos del Reproductor multimedia VLC" debe utilizarse, es necesario iniciar VLC al menos una vez para volver a crear esta carpeta y los archivos de configuración de VLC.



### Soporte multilingüe del Reproductor multimedia VLC ###
Dado que los diseñadores del reproductor multimedia no pretenden que el software proporcione información relevante para identificar los objetos que lo constituyen, este complemento se basa en su nombre o descripción.
Para hacer esto, es necesario definir para cada idioma de VLC los objetos utilizados por el complemento. Estas definiciones se encuentran en los archivos "strings-xx.ini" (xx = identificador de idioma) de la carpeta "VLCLocale" del complemento.
Estos archivos se guardan en codificación "UTF-8" sin BOM.
Para conocer el idioma configurado en VLC, este complemento usa el nombre del segundo menú de la barra de menús y es la clave "StringToFindLanguage" de la sección "main" que lo define.
La sección "VLC" del archivo contiene las claves para identificar los objetos. Son:

*	VLCAppTitle =  establece el título de la ventana de VLC sin el medio lanzado.
*	PlayButtonDescription = Define la descripción del botón de reproducción
*	PauseThePlaybackButtonDescription =  Define la descripción del botón de pausa
*	UnMuteImageDescription =  define la descripción del botón para silenciar o desilenciar el sonido
*	LoopCheckButtonDescription = define la descripción del botón para poner la reproducción del medio en modo  repetición o no.
*	RandomCheckButtonDescription = define la descripción del botón para la reproducción normal o aleatoria



### Definición de las órdenes de teclado a modificar ###
Como se mencionó anteriormente, algunos atajos de VLC no son explotables dependiendo del tipo de teclado. Este complemento permite definirlos y modificarlos.

Las definiciones de estos atajos a modificar están en el archivo "settings.ini" de la carpeta "locale" para cada idioma de NVDA admitido por el complemento.
En este archivo, la sección "vlc-keynames"  definidos por un número, los identificadores VLC de los atajos a modificar y la sección "vlc-assignements", asocia con cada identificador el nuevo atajo.
Los atajos deben estar en la forma entendida por VLC (por ejemplo, Ctrl para control, left para flecha izquierda).

### Definición de los gestos de entrada ###
Los gestos de entrada de esste complemento también se definen en el archivo "settings.ini".
Estan en la seccion "script-gestures" y para cada script, es posible asignar uno o más gestos de entrada en la forma NVDA,  (por ejemplo kb:(desktop):control+c, kb:nvda+shift+alt+f1).
Los identificadores de los scripts son:

*	goToTime=script "Mostrar el cuadro de diálogo para establecer el tiempo y mover el cursor de reproducción en este tiempo",
*	reportElapsedTime=script "Anunciar la duración ya reproducido del medio",
*	reportRemainingTime=script "Anunciar la duración restante del medio para ser reproducido",
*	reportTotalTime=script "Anunciar la duración total del medio",
*	reportCurrentSpeed=script "Anunciar la velocidad actual",
*	recordResumeFile=script "Guardar la posición de reproducción actual para este medio",
*	resumePlayback= script "Reanudar la reproducción en la posición guardada para este medio".
* continuePlayback= script "Reanudar la reproducción interrumpida en la posición memorizada por VLC"


## Historial ##
### Versión 1.3.1 (11/06/2019) ###
* corrección del archivo buildVars.py 
* se añade traducción al español


### Versión 1.3 (01/06/2019) ###
Compatibilidad con NVDA 2019.2.0 (actualización del manifest.ini).

### Versión 1.2 (06/03/2019) ###
* reemplazo de los botones "sí" y "no" con los botones "ok" y "cancelar" en los cuadros de confirmación para usar la tecla "Escape".
* reemplazo del termino "module complémentaire " por "extension impuesto por los traductores de NVDA en francés).
* compatibilidad con NVDA 2019.1.0.
* preparación para la compatibilidad con python3.


### Versión 1.1 (21/12/2018) ###
*	corrección de no reanudar la reproducción cuando la lista de medios recientes tiene solo un medio,
*	corrección de la documentación,
*	puesta en compatibilidad con versiones alpha 2019.1 de NVDA.


### Versión 1.0 (29/10/2018) ###
Para evitar confusiones con otros complementos para VLC, el nombre del complemento cambia a "VLCAccessEnhancement" y en el   Administrador de Complementos, se llama "Reproductor multimedia VLC: complementos de accesibilidad".

Novedades:

*	puesta en compatibilidad con NVDA 2018.3,
* cambio en el nombre del complemento para evitar confusiones con otros complementos para VLC.
*	anuncia la indicación de la posibilidad de reanudar la reproducción interrumpida en la posición memorizada por VLC y reanuda la reproducción con el gesto de entrada "alt+control+r",
*	se añade el botón para eliminar el archivo de configuración de VLC,


Cambio interno::

* Reelaboración completa del código,
*	archivo style.css renombrado en style_md.css,
*	reconversión del archivo del manual del usuario para la conformidad en la  forma con los complementos internacionales,
*	renombrado el menú de configuración del complemento.


## Historial anterior ##
### Versión 3.0 (19/06/2018) ###
Esta versión es compatible con VLC 3.0, incompatible con versiones anteriores.

Novedades:

*	vocalización del indicador de repetición del medio,
*	lectura correcta de la barra de estado,
*	anuncio del estado   reproduciendo o en pausa con el sonido silenciado al enfocar la ventana principal.


Cambios:

*	el archivo de configuración de VLC ya no se modifica automáticamente para definir atajos de teclado.  Su implementación se realiza manualmente por el usuario con la ayuda de un simple botón,
*	el cuadro de diálogo "Ir a tiempo" de VLC ya no se vocaliza.
*	el nivel de volumen ahora se anuncia con cada cambio.


### Versión 2.3.1 ###
*	correcciones de errores (regresión de "nvda+control+h")


### Versión 2.3 ###
*	se añade los scripts para Reanudar la reproducción
*	se añade la gestión de un archivo de configuración para el complemento


### Versión 2.2 ###

*	configuración del archivo vlcrc para cambiar las teclas de variaciones de velocidad,
*	anuncio de la duración reproducida durante los saltos de  reproducción,
*	anuncio del silenciado/desilenciado del sonido,
*	anuncio del pasaje en pausa,
*	vocalización del cuadro de diálogo de VLC "Ir a tiempo",
* modificación del cuadro de diálogo del complemento "Ir a tiempo".



### Cambios para la versión 2.0 ###

*	 Primera versión multilingüe.


[1]: http://angouleme.avh.asso.fr/fichesinfo/fiches_nvda/data/VLCAccessEnhancement-1.3.1.nvda-addon
[2]: https://rawgit.com/paulber007/AllMyNVDAAddons/master/VLC/VLCAccessEnhancement-1.3.1.nvda-addon
