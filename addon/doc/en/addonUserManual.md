# VLC media player : accessibility enhancements - user's manual # 

* Authors : Paulber19 with the very active participation of Daniel Poiraud. 
* download version 1.1.1: 
	* [download server 1][1] 
	* [download server 2][2] 



The author has used a software of translation to write this document and  presents his apologies for his very bad English.

This add-on adds a number of commands to facilitate the playback of the media with NVDA. 

This version is compatible  with VLC's versions higher to 3.0.

This version is not compatible with NVDA's versions below to 2018.3.2.

## Gestures  provided by the module: ## 

* "NVDA+Control+"H : Show the help on the available gestures  in the main window, 
* "," : announce played time of the media, 
* "." : announce the length of media remaining to be read, 
* "/" : announce the total duration of the media, 
*";" : : announce the speed of reading, 
* "Control + comma " : Display the dialog to set a time and move the playback cursor to the time, 
* "NVDA+control+f5" : save the current time of the media for a future revival of the play, 
* "NVDA+control+f6" : restart the playback to the recorded time for the medium, 
* "alt+control+" r: restart the playback interrupted position stored by VLC. 


These gestures can be modified with  the "Input gestures"dialog of NVDA.

## Keyboard shortcuts specific to VLC vocalisés by the module: ## 
Some of the shortcuts provided by default by VLC pose problems on non qwerty keyboard and must be modified. These are: 

* The keyboard shortcuts "[" and "]" for the playback speed  (little faster or little slower). They can be replaced by "I" and "U" for azerty keyboard. 
* the  "control+alt+right or left arrow" keyboard shortcut to move forward or backward 5 minutes in the media, because not working in some configuration. They can be replaced by "control+shift+left or right arrow". 
* the  "+" and "-" numeric keyboard shortcuts   for playback speed changing , because badly placed. They will be replaced by "o" and "y". 


To implement these new shortcuts, you must proceed to the modification of the configuration file "vlcrc" in VLC like this: 

* after installing VLC, or deleted the VLC configuration folder, launch   once VLC using the desktop shortcut or by reading a media, and then stop it. 
* type "NVDA+n" and in the submenu "preferences", select the  "VLC multimedia player: Accessibility enhancements add-on - settings ..." sub-menu,
* finally, press the "Modify VLC shortcuts" button.


Here are the keyboard shortcuts that the module vocalise: 

* "Y" : decrease the playback speed. 
* "U" : lower a bit the speed of reading. 
* "I" : increase a bit the speed of reading. $ $ | | $ $ * - O : increase the playback speed. 
* "=" : return to the normal speed, 
* "m" : to cut off or turn on the sound, 
* "space" : start or pause playback, 
* "s" : stop the media, 
* "l" : toggle the state of repetition of the media between repeat all, repeat the current media, not to repeat, 
* "shift + right or left arrow" : move forward or backward the played time of the media 3 seconds, 
* "alt + right or left arrow " : move forward or backward the played time to the media of 10 seconds, 
* "control +  right or left arrow ": move forward or backward the played time of the medium in 1 minute, 
* "control + shift+ right  or left arrow" : move forward or backward the played time to the media of 5 minutes. 
* "upArrow" or "downArrow" : increase or decrease the volume, 
* "control + upArrow" or "control + downArrow": increase or decrease the volume, 
* "space" : pause the media, or restart the playback. 


To not disturb the user, the played time  is automatically vocalized only when the media is paused or playing with the sound muted. 

A check is done to prevent jumping outside of the boundaries of the media. For example, it is not possible to make a break of 5 minutes if he only stays 2 minutes remaining to play, or back 10 seconds if the term already read is 3 seconds. 

Status of "mute" is indicated at the launch of the reading. 

The volume level is announced when change occurs.

The passage to the break is announced. 

## Script to Display the dialog to set a time and move the playback cursor to the time ## 
VLC offers the possibility of using the  "control+t"shortcut  to move to a specific time of the media. But the dialog box that this creates problems of accessibility. 

The module offers another solution (preferable) to move at a time with the  "control+," shortcut. 

This shortcut presents a dialog box that allows you to set the time (hours, minutes, seconds) where to position the playback cursor in the media, within the limits of the total duration of the media decreased by 5 seconds. 


## Recovery of the reading of ## 
to be able To resume playback of a media, two solutions are possible: 
### First solution ### 
VLC remembers the current playback position at the time when it is interrupted, that is to say, either following a command to VLC, either by exiting the application. 

When the media is re-launched, VLC displays the possibility of recovery in the status bar for a very short time (a few seconds) and typing the shortcut "alt+r", playback is restarted at the stored position to the media. 

As this is hardly usable for a non-seeing,the module provides a script that allows you to resume playback at the position recorded by VLC without this time constraint. 

When a media is being revived, and that VLC has saved , for the media, a restart position of the reading, the voice announcement"Resume playback alt+control+r". Using the gesture command "alt+control+r", playback of the media continues to the stored position. 

This gesture control is editable by the user. 


### Second way ### 
This second solution requires that you first mark the starting position of the playback using the gesture command "nvda+control+f5". 
It is better to pause the media in advance. 
You are not forced to leave VLC to resume the playback of this media. 

To resume playback of a media file, the keyboard command "NVDA+control+f6" to resume playback at the position recorded by the module for this media. 

This position is recorded in the module configuration file and for each media are registered in the name of the media and the position associated. Only the media, the most recently opened are kept in this file. 

Warning: the name of the media is unique in this file. If two files of the same names are in different folders, only the last record for that name will be retained. 

## Technical additions ## 
### Resetting the configuration of the VLC ### 
During its startup, VLC creates in the folder user configuration of Windows, the folder "vlc" which contains the configuration files of the VLC. 

To reset the VLC configuration  without having to reinstall, just delete the folder. 

To facilitate this, the module offers the option to Delete the VLC configuration folder  with a button.

By the result, if the button "Modify VLC shortcuts " should be used, it is necessary to run it at least once VLC to re-create this folder and the configuration files of the VLC. 


### Support for the multilingualism of the VLC media player ### 
Like the developers of the media player are not provided in the software to provide relevant information to identify the objects constituting it, the module relies on their name or their description. 
To do this, it is necessary to define for each language version of VLC objects used by the module. These definitions are in the files "strings-xx.ini" (xx = id of the language) in the folder "VLCLocale of the module. 

These files are saved in the encoding "UTF-8" without BOM. 

To get the language configured in VLC, the module uses the name of the second menu of the menu bar and this is the  "StringToFindLanguage" key  of the "main" section that is defined.

"VLC" section contains the keys to identify the objects. These are: 

* "VLCAppTitle" : sets the window title of VLC without media launched. 
* "PlayButtonDescription" : sets the description for the play button 
* "PauseThePlaybackButtonDescription"  sets the description of the pause button 
* "UnMuteImageDescription" : sets the description for the button to turn off or turn on the sound 
* "LoopCheckButtonDescription" : sets the description for the button to put the media is playing in repeat mode or not. 
* "RandomCheckButtonDescription" : = sets the description of the button for a playback in normal or random 



### Definition of keyboard shortcuts to modify ### 
As noted earlier, some shortcuts of VLC are not usable depending on the type of keyboard. The module allows you to define and modifythem.

The definitions of these shortcuts to modify are in the "settings.ini"file  in the  "local"folder  to each language of NVDA supported by the module. 

In this file, the "vlc-keynames" section , defines by a number, the  identifiers for each VLC shortcut   to be modified,  and the "vlc-assignments"section , associates each identifier with the new shortcuts. 

The shortcuts must be in the form understood by VLC(for example, Ctrl for control, left for the leftArrow). 

### Definition of the gesture command # # # 
The gestures  of the module are also defined in the  "settings.ini"file . 

They can be found in the  "script-gestures" section , and for each script, it is possible to assign one or more actions command in the form NVDA, (for example kb:(desktop):control+c, kb:nvda+shift+alt+f1). 

The identifiers of the scripts are: 

* "goToTime" : "script to Display the dialog to set a time and move the playback cursor at this time," $ $ | | $ $ * reportElapsedTime="script Announce the length already read from the media', $ $ | | $ $ * reportRemainingTime="script Announce the duration of the media remaining to read", 
* "reportTotalTime" : "script Announce the total duration of the media", 
* "reportCurrentSpeed" : "script Announce the current speed ", 
* "recordResumeFile" : "script to Save the current playback position for the media', $ $ | | $ $ * resumePlayback= "script Restart the playback at the position recorded for this media ". 
* "continuePlayback" : "script to Resume the playback interrupted position stored by VLC" 


## History ## 
### Version 1.3 (01/06/2019) ### 
- compatibility with NVDA 2019.2.0.

### Version 1.2 (21/02/2019) ### 
- compatibility with NVDA 2019.1.0.
- preparation of compatibility with Python 3


### Version 1.1 (5/12/2018) ### 

* correction of non-recovery of the playback when the media list recent has only a single medium, 
* corrections to the documentation, 
* compatibility with alpha versions 2019.1 of NVDA.


### Version 1.0 (29/10/2018) ### 
To avoid confusion with other add-ons for VLC, the name of the module is to be renamed "VLCAccessEnhancement" and in the add-ons manager, it is called "VLC multimedia player: Accessibility enhancements". 

Features: 

* compatibility with NVDA 2018.3, 
* announcement of the indication of the possibility of the resumption of the playback interrupted position stored parVLC and resume playback using the gesture command "alt+control+r", 
* added button to delete the configuration file deVLC, 


internal Change: 

* full redesign of the code, $ $ | | $ $ * - style file.css renamed style_md.css, 
* conversion of file user's manual for compliance of the form with the add-ons international, 
* renomage the configuration menu of the module. 


## Previous history ## 
### Version 3.0 (19/06/2018) ### 
This version is compatible with VLC 3.0, which is incompatible with the old versions. 

New: 

* vocalization of the indicator of repetition of the media, 
* correct reading of the status bar, 
* announcement of the state play or pause with the sound muted when the focus of the main window. 


Changes: 

* the configuration file of VLC is no longer changed automatically to set the keyboard shortcuts. Their implementation is done manually by the user using a simple button, 
* the dialog box "Go to time" of VLC is no longer vocalized. 
* the volume level is now announced at each change. 


### Version 2.3.1 ### 
* fixed bug (regression from "nvda+control+h") 


### Version 2.3 ### 
* addition of scripts to the recovery of the reading 
* addition of the management of a configuration file for the module 


### Version 2.2 ### 

* configuration of the file vlcrc to change the keys of speed variations, 
* ad of the time read during breaks, reading, 
* announcement of the cut-off /delivery of the sound, 
* announcement of the passage in pause, 
* vocalization of the dialog box of VLC "Go-time", $ $ | | $ $ * * * * modification of the dialog box of the module "Go time". 



### Changes for version 2.0 # # # $ $ | | $ $ $ $ | | $ $ * * * First multi-lingual version. $ $ | | $ $ $ $ | | $ $ 

[1]: http://angouleme.avh.asso.fr/fichesinfo/fiches_nvda/data/VLCAccessEnhancement-1.3.nvda-addon 
[2]: https://rawgit.com/paulber007/AllMyNVDAAddons/master/VLC/VLCAccessEnhancement-1.3.nvda-addon 


