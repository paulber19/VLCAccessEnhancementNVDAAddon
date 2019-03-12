# Lecteur  multimédia VLC : compléments d'accessibilité - manuel utilisateur #


*	Auteurs :  Paulber19 avec la participation très active de  Daniel Poiraud.
*	Télécharger  version 1.1.1:
	* [serveur de téléchargement 1][1]
	* [serveur de téléchargement 2][2]


Ce module complémentaire ajoute diverses commandes pour faciliter la lecture des médias avec NVDA.  

Il a été testé sur VLC 3.0, Windows 10  NVDA 2018.2.1 et NVDA 2018.3.

## Gestes de commande apportés par le module: ##
*	NVDA+Control+H : Afficher l'aide sur les raccourcis possibles dans la fenêtre principale,
*	virgule : annoncer la  durée lue du média,
*	point-virgule : annoncer la durée du média restante à lire,
*	deux points : annoncer la durée totale du média,
*	point d'exclamation : annoncer la vitesse de lecture,
*	Control + virgule : Afficher le dialogue pour  définir un temps et déplacer le curseur de lecture à ce temps,
*	NVDA+control+f5: enregistrer le temps courant du média pour une future relance de la lecture,
*	NVDA+control+f6: relancer la lecture  au temps enregistré pour ce média,
* alt+control+r: relancer la lecture interrompue à la position mémorisée par VLC.


Ces gestes de commandes peuvent être modifiés  avec le dialogue "Gestes de commande" de NVDA.

## Raccourcis clavier propre à VLC vocalisés par le module: ##
Certains raccourcis prévus par défaut par VLC posent des problèmes et doivent être modifiés. Ce sont:

*	Les raccourcis-clavier "Crochet fermé" et "Crochet ouvert" pour la vitesse de lecture un peu plus rapide ou un peu plus lente,   car ils ne sont pas utilisables en clavier français. Ils seront remplacés par "I" et "U". ,
*	les raccourcis -clavier "control+alt+flèche droite ou gauche" pour avancer ou reculer de 5 minutes le média, car ne fonctionnant pas dans certaines configuration. Ils seront remplacés par "control+majuscule+flèche droite ou gauche".
*	les raccourcis-clavier "+" et"-" du clavier alphanumérique pour modifier la vitesse de lecture, car mal placés. Ils seront remplacés par "o" et "y".


Pour mettre en place ces nouveaux raccourcis, vous devez procéder  à la modification du fichier de configuration  "vlcrc" de VLC comme ceci:

*	après  avoir installé VLC ou supprimé le dossier de configuration deVLC, lancez le une première fois  en utilisant le raccourci du bureau ou en lisant un média, puis arrêtez  le.
*	tapez "NVDA+n" et  dans le sous-menu "préférences", sélectionner le sous-menu "Lecteur multimédiaVLC: compléments d'accessibilité - paramètres ",
*	enfin, appuyez sur le bouton "Modifier les raccourcis du lecteur média  VLC".


Voici les raccourcis clavier que le module vocalise:

*	Y : diminuer la vitesse de lecture.
*	U : diminuer un peu la vitesse de lecture.
*	I : augmenter un peu la vitesse de lecture.
*	O : augmenter la vitesse de lecture.
*	signe égal : retourner à la vitesse normale,
*	m : couper ou remettre le son,
*	espace : lancer ou mettre en pause la lecture,
* s: arrêter le média,
*	l : basculer l'état de répétition du média entre   répéter tout, répéter le média courant, ne pas répéter,
*	majuscule + flèche droite ou gauche: avancer ou reculer la durée lue du média de 3 secondes,
*	alt + flèche droite ou gauche : avancer ou reculer la durée lue du média de 10 secondes,
*	control + flèche droite ou gauche : avancer ou reculer  la durée lue du média de 1 minute,
*	control majuscule+ flèche droite ou gauche: avancer ou reculer la durée lue du média de 5 minutes.
*	flèche haut ou bas: augmenter ou baisser le volume,
*	control flèche haut ou bas: augmenter ou baisser le volume,
* espace: mettre en pause le média ou relancer la lecture.


Pour ne pas gêner l'utilisateur, la  durée lue automatiquement  est vocalisée uniquement lorsque le média est en pause ou en lecture avec le son coupé.

Un contrôle est fait pour empêcher un saut en dehors  des limites du média. Par exemple, il n'est pas possible de faire un saut de 5 minutes s'il ne reste que 2 minutes restantes à lire ou bien reculer de 10 secondes si la durée déjà lue est de 3 secondes.  

L'état "son coupé" est signalé lors  du lancement de la lecture.

Le niveau du volume est annoncé à chaque modification.

Le passage en pause est annoncé.

## Script Afficher le dialogue pour  définir un temps et déplacer le curseur de lecture à ce temps ##
VLC offre la possibilité à l'aide du raccourci "contrôl+t" de se déplacer à un temps précis du média. Mais la boite de dialogue qu'il présente pose des problèmes d’accessibilité.

Le module offre une autre solution  (préférable) pour se déplacer à un temps avec le  raccourci "control+virgule".  
Ce raccourci présente une boite de dialogue qui vous permet de définir le temps (heures, minutes, secondes) où positionner le curseur de lecture du média, dans la limite de la durée totale du média diminuée de 5 secondes.


## Relance de la lecture ##
Pour pouvoir reprendre  la lecture d'un média, deux solutions sont possibles:
### Première solution ###
VLC mémorise la position courante de lecture au moment  où celle-ci est interrompue,  c'est à dire   soit suite à une  commande  VLC, soit en quittant l'application.

Lorsque le média est relancé, VLC affiche la possibilité de reprise dans la barre d'état pendant un temps très court (quelques secondes)  et en tapant le raccourci "alt+r", la lecture est relancée à la position enregistrée pour ce média.

Comme ceci est difficilement utilisable pour un non voyant,le module apporte un script qui permet de relancer la lecture à la position enregistrée par VLC sans avoir cette contrainte de temps.

Lorsque un média est relancé et que VLC a enregistré , pour ce média, une position de reprise de la lecture,  l'annonce vocale"Reprise de la lecture alt+control+r"  l'indique. En utilisant le geste de commande "alt+control+r",  la lecture du média continue à la position enregistrée.

Ce geste de commande est modifiable par l'utilisateur.


### Seconde solution ###
Cette seconde solution  nécessite tout d'abord de marquer la position de reprise de la lecture à l'aide du geste de commande "nvda+control+f5".
Il est préférable de mettre en pause le média au préalable.
Vous n'êtes pas obligé de quitter VLC pour reprendre la lecture de ce média.

Pour reprendre la lecture d'un  média, la commande clavier "NVDA+control+f6"  relancera la lecture   à la position enregistrée par le module pour ce média.

Cette position est enregistrée dans le fichier de configuration du module et pour chaque média sont enregistrés le nom du média et la position associée. Seuls les médias les plus récemment ouverts sont conservés dans ce fichier.

Attention: le nom du média  est unique dans ce fichier. Si deux fichiers de même noms sont dans des dossiers différents, seul le dernier  enregistrement pour ce nom sera retenu.

## Compléments techniques ##
### Réinitialisation de la configuration de VLC ###
Lors de son démarage, VLC crée dans le dossier de configuration utilisateur de Windows,  le dossier "vlc" qui contient les fichiers de configuration de VLC.

Pour réinitialiser la configuration deVLC sans avoir à le réinstaller, il suffit de supprimer ce dossier.

Pour faciliter cela, le module offre le bouton "Supprimer le dossier de configuration de VLC" dans le dialogue de configuration du module .

Par la suite, si le bouton "Modifier les raccourcis du lecteur média  VLC  " doit être utiliser, il est nécessaire de lancer au moins une fois VLC pour recréer ce dossier et les fichiers de configuration de VLC.



### Support du multilinguisme du lecteur multimédia VLC ###
Comme les concepteurs du lecteur multimédia n'ont pas prévu dans le logiciel de fournir des informations pertinentes pour identifier  les objets le constituant, le module s'appuie sur leur nom ou leur description.
Pour ce faire, il est nécessaire de définir pour chaque langue de VLC les objets utilisés par le module. Ces définitions se trouvent dans les fichiers "strings-xx.ini" (xx = identifiant de la langue) du dossier "VLCLocale du module.
Ces fichiers sont enregistrés en codage "UTF-8" sans BOM.
Pour connaitre la langue configuré dans VLC, le module utilise le nom du second menu de la barre de menus et c'est la  clé "StringToFindLanguage " de la section "main" qui le défini.
La section "VLC" du fichier   contient les clés permettant d'identifier les objets. Ce sont:

*	VLCAppTitle =  définit le titre de la fenêtre de VLC sans média lancé.
*	PlayButtonDescription = définit la description du bouton lecture
*	PauseThePlaybackButtonDescription =  définit la description du bouton pause
*	UnMuteImageDescription =  définit la description du bouton pour couper ou remettre le son
*	LoopCheckButtonDescription = définit la description du bouton pour mettre la lecture du média en mode répétition ou non.
*	RandomCheckButtonDescription = définit la description du bouton pour une lecture en mode normal ou aléatoire



### Définition des raccourcis-clavier à modifier ###
Comme indiqué précédemment, certains raccourcis de VLC ne sont pas exploitables  suivant le type de clavier. Le module permet de les définir et de les modifier.

Les définitions de ces raccourcis à modifier sont dans le fichier "settings.ini" du dossier "locale" pour  chaque langue de NVDA supportée par le module.
Dans ce fichier, la section "vlc-keynames"  définit par un numéro, les  identifiants VLC  des raccourcis à modifier et la section "vlc-assignements", associe à chaque identifiant le nouveau raccourcis.
Les raccourcis doivent être sous la forme comprise par VLC(par exemple, Ctrl pour control, left pour flèche gauch).

### Définition des gestes de commande ###
Les gestes de commandes du module sont également définis dans le fichier "settings.ini".
Ils se trouvent dans la section "script-gestures" et pour chaque script, il est possible d'attribuer un ou plusieurs gestes de commande sous la forme NVDA,  (par exemple kb:(desktop):control+c, kb:nvda+shift+alt+f1).
Les identifiants des scripts sont:

*	goToTime=script "Afficher le dialogue pour  définir un temps et déplacer le curseur de lecture à ce temps",
*	reportElapsedTime=script "Annoncer la durée déjà lue du média ",
*	reportRemainingTime=script "Annoncer la durée du média restante à lire",
*	reportTotalTime=script "Annoncer la durée totale du média",
*	reportCurrentSpeed="script Annoncer  la vitesse courante  ",
*	recordResumeFile=script "Enregistrer la position courante de lecture pour ce média ",
*	resumePlayback= script "Relancer la lecture à la position  enregistrée pour ce média ".
* continuePlayback= script "Reprendre la lecture interrompue à la position mémorisée par VLC"


## Historique ##

### Version 1.1.2 (21/02/2019) ###
Correction du fichier manifest.ini pour compatibilité avec NVDA 2019.1.0

### Version 1.1.1 (25/12/2018) ###
correction de la documentation pour les liens de téléchargement

### Version 1.1 (21/12/2018) ###

*	correction de non reprise de la lecture lorsque la liste des médias récents n'a qu'un seul média,
*	corrections de la documentation,
*	mise en compatibilité avec les versions alpha 2019.1 de NVDA.


### Version 1.0 (29/10/2018) ###
Pour éviter une confusion avec d'autres modules complémentaires pour VLC, le nom du module est renommé en "VLCAccessEnhancement" et dans le gestionnaire de modules complémentaires, il se nomme "Lecteur multimédia VLC: compléments d'accessibilité".

Nouveautés:

*	mise en compatibilité avec NVDA 2018.3,
* changement du nom du module pour éviter toute confusion avec d'autres modules pour VLC.
*	annonce  de l'indication de la possibilité de reprise de la lecture interrompue à la position mémorisée parVLC et reprise de la lecture à l'aide du geste de commande "alt+control+r",
*	ajout du bouton pour supprimer le fichier de configuration deVLC,


Changement interne:

* remaniement complet du code,
*	fichier style.css renommé en style_md.css,
*	reconversion du fichier manuel utilisateur pour conformité  de forme avec les modules complémentaires  internationnaux,
*	renomage du menu de configuration du module.


## Historique précédent##
### Version 3.0 (19/06/2018) ###
Cette version est  compatible avec VLC 3.0, incompatible avec les anciennes versions.

Nouveauté:

*	vocalisation de l'indicateur de répétition du média,
*	lecture correcte de la barre d'état,
*	annonce de l'état  lecture ou pause avec le son coupé lors de  la focalisation de la fenêtre principale.


Changements:

*	le fichier de configuration de VLC n'est plus modifié automatiquement pour  définir les raccourcis clavier.  Leur mise en place est faite manuellement par l'utilisateur à l’aide d'un simple bouton,
*	la boite de dialogue "Aller au temps" de VLC n'est plus vocalisée.
*	le niveau du volume est maintenant annoncé à chaque modification.


### Version 2.3.1 ###
*	correction de bugs (régression de "nvda+control+h")


### Version 2.3 ###
*	ajout des scripts pour la relance de la lecture
*	ajout de la gestion d'un fichier de configuration pour le module


### Version 2.2 ###

*	configuration du fichier vlcrc pour modifier les touches de variations de vitesse,
*	annonce de la durée lue lors des sauts de  lecture,
*	annonce de la coupure /remise du son,
*	annonce du passage en pause,
*	vocalisation de la boite de dialogue de VLC "Aller au temps",
* modification de la boite de dialogue du module "Aller au temps".



### Changements pour la version 2.0 ###

*	 Première version multilingue.


[1]: http://angouleme.avh.asso.fr/fichesinfo/fiches_nvda/data/VLCAccessEnhancement-1.1.2.nvda-addon
[2]: https://rawgit.com/paulber007/AllMyNVDAAddons/master/VLC/VLCAccessEnhancement-1.1.2.nvda-addon


