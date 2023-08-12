# -*- coding: utf-8 -*-
# Copyright (C) 2023 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import globalPluginHandler
import addonHandler
import globalVars
import ui
from scriptHandler import script
from comtypes import CoInitialize
from comtypes.client import GetModule, CreateObject
from ctypes import POINTER, c_void_p
from comtypes.automation import IDispatch

addonHandler.initTranslation()

# Define el CLSID para CUIAutomation
CLSID_CUIAutomation = "{FF48DBA4-60EF-4201-AA87-54103EEF594E}"

def obtener_nombre_escritorio():
	"""
	Obtiene el nombre del escritorio utilizando la interfaz de automatización de UI de Windows.
	
	Devuelve:
		str: El nombre del escritorio si se pudo obtener, de lo contrario devuelve un mensaje de error.
	"""
	try:
		# Inicializa el sistema COM.
		CoInitialize()

		# Importa el módulo UIAutomationClient
		GetModule("UIAutomationCore.dll")
		from comtypes.gen.UIAutomationClient import IUIAutomation, CUIAutomation

		# Crea el objeto UIAutomation
		uia = CreateObject(CUIAutomation, interface=IUIAutomation, clsctx=1)

		# Obtiene el elemento raíz (Escritorio)
		root = uia.GetRootElement()

		# Obtiene el nombre del elemento raíz
		return root.CurrentName
	except COMError:
		return _("No se pudo obtener el nombre del escritorio.")

def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()

	@script(gesture=None, description= _("Anuncia el escritorio virtual actual"), category= "EnhanceTools")
	def script_anuncia_escritorio(self, gesture):
		ui.message(obtener_nombre_escritorio())
