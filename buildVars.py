# -*- coding: UTF-8 -*-

import os.path

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)


def _(arg):
	return arg


# Add-on information variables
addon_info = {
	# for previously unpublished addons, please follow the community guidelines
	# at: https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name": "VLCAccessEnhancement",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary": _("VLC multimedia player: Accessibility enhancements"),
	# Add-on description
	# Translators: Long description to be shown for this add-on
	# on add-on information from add-ons manager
	"addon_description": _(
		"""This addon adds a variety of commands to enhance accessibility in playing media:
- script to announce the duration of the media you've already played,
- script to announce the duration of the media remaining to be play,
- script to announce the total duration of the media,
- script to announce the current speed,
- automatic announcement of state's changes such as: pause , volume mute, speed , """
		"""repeat or random state's playback, volume's level, state of hidden or shown of menu bar,
- automatic announcement of the elapsed time after a command to jump,
- scripts to mark playback position and resume playback at this position,
- script to restart interrupted playback at time recorded by VLC,
- correct reading of the main window's status bar,
- change of some VLC's annoying keyboard shortcuts of VLC.
- and others enhancements as:
 - access to playback controls (feature 's idea of Javi Dominguez),
 - access to adjustments and effects dialog,
 - correct announcement of name and value 's slider,
 - deleting of some useless html text in description's object(code from Javi Dominguez add-on).


The list of commands is obtained by "NVDA +Control+h".
Compatible with VLC 3.0.
"""),

	# version
	"addon_version": "2.13",
	# Author(s)
	"addon_author": "PaulBer19 (paulber19@laposte.net",
	# URL for the add-on documentation support
	"addon_url": "https://github.com/paulber19/NVDAExtensionGlobalPlugin.git",
	# URL for the add-on repository where the source code can be found
	"addon_sourceURL": "https://github.com/paulber19/NVDAExtensionGlobalPlugin.git",
	
	# Documentation file name
	"addon_docFileName": "addonUserManual.html",
	# Minimum NVDA version supported (e.g. "2018.3")
	"addon_minimumNVDAVersion": "2024.1",
	# Last NVDA version supported/tested
	# (e.g. "2018.4", ideally more recent than minimum version)
	"addon_lastTestedNVDAVersion": "2025.1",
	# Add-on update channel (default is stable or None)
	"addon_updateChannel": None,
	# Add-on license such as GPL 2
	"addon_license": "GPL v2",
	# URL for the license document the ad-on is licensed under
	"addon_licenseURL": "https://www.gnu.org/licenses/gpl-2.0.html",
}

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [
	os.path.join("addon", "*.py"),
	os.path.join("addon", "appModules", "vlc", "*.py"),
	os.path.join("addon", "globalPlugins", "vlcAccessEnhancement", "*.py"),
	os.path.join(
		"addon", "globalPlugins", "vlcAccessEnhancement", "updateHandler", "*.py"),
	os.path.join("addon", "shared", "*.py"),
]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory,
# not to the root directory of your addon sources.
excludedFiles = []

# Base language for the NVDA add-on
# If your add-on is written in a language other than english, modify this variable.
# For example, set baseLanguage to "es" if your add-on is primarily written in spanish.
baseLanguage = "en"

# Markdown extensions for add-on documentation
# Most add-ons do not require additional Markdown extensions.
# If you need to add support for markup such as tables, fill out the below list.
# Extensions string must be of the form "markdown.extensions.extensionName"
# e.g. "markdown.extensions.tables" to add tables.
markdownExtensions = []
