# -*- coding: utf-8 -*-
# Copyright (C) 2023 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.
#
# El anuncio de carpeta vacía a sido extraído de un complemento de la comunidad rusa.
#
# Me quede solo con el archivo .py y no recuerdo de donde lo saque ni el nombre del complemento. En cuanto tenga más información lo pondré aquí dando los créditos adecuados.

import globalPluginHandler
import addonHandler
import UIAHandler
import IAccessibleHandler
import globalVars
import ui
import appModuleHandler
import ctypes
from NVDAObjects.UIA import UIA
from scriptHandler import script
from comtypes import CoInitialize
from comtypes.client import GetModule, CreateObject
from ctypes import POINTER, c_void_p
from comtypes.automation import IDispatch

addonHandler.initTranslation()

# Define el CLSID para CUIAutomation
CLSID_CUIAutomation = "{FF48DBA4-60EF-4201-AA87-54103EEF594E}"
# Usar ctypes para acceder a user32.dll
user32 = ctypes.windll.user32

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

class EmptyList(UIA):
	"""Representa una lista vacía en la interfaz de usuario."""
	isFocusable = True
	shouldAllowUIAFocusEvent = True

	def _get_description(self):
		"""Obtiene la descripción del objeto."""
		return _(_("Carpeta vacía"))

	def event_gainFocus(self):
		"""Manejador del evento cuando el objeto gana el foco."""
		ui.message(self.description)

def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()

		self._winEventToNVDAEvent_native = IAccessibleHandler.winEventToNVDAEvent
		IAccessibleHandler.winEventToNVDAEvent = self.winEventToNVDAEvent

	def winEventToNVDAEvent(self, eventID, window, objectID, childID, useCache=True):
		"""
		Transforma un evento de Windows en un evento de NVDA.

		Args:
			- eventID: ID del evento de Windows.
			- window: Ventana que generó el evento.
			- objectID: ID del objeto en la ventana.
			- childID: ID del hijo del objeto en la ventana.
			- useCache: Si se debe usar el cache o no.

		Returns:
			- Resultado de la transformación.
		"""
		res = self._winEventToNVDAEvent_native(eventID, window, objectID, childID, useCache=useCache)
		if res is None:
			self._winEventToNVDAEvent(eventID, window)
		return res

	def _winEventToNVDAEvent(self, eventID, window):
		"""Manejo interno de la transformación de eventos."""
		# Reemplazando winUser.EVENT_OBJECT_FOCUS con su valor real (0x8005)
		if eventID != 0x8005:
			return

		# Reemplazando winUser.isWindow con una llamada a ctypes
		if not window or not user32.IsWindow(window):
			return

		if not (UIAHandler.handler and UIAHandler.handler.isUIAWindow(window)):
			return

		# Reemplazando winUser.getWindowThreadProcessID con una llamada a ctypes
		processID = ctypes.c_uint()
		user32.GetWindowThreadProcessId(window, ctypes.byref(processID))
		if not processID.value:
			return

		if appModuleHandler.getAppModuleFromProcessID(processID.value).appName == "explorer":
			UIAElement = UIAHandler.handler.clientObject.ElementFromHandleBuildCache(window, UIAHandler.handler.baseCacheRequest)
			if UIAElement.cachedControlType == UIAHandler.UIA_ListControlTypeId and UIAElement.currentClassName == "UIItemsView":
				lastChildElement = UIAHandler.handler.baseTreeWalker.GetLastChildElementBuildCache(UIAElement, UIAHandler.handler.baseCacheRequest)
				if lastChildElement and lastChildElement.currentClassName == "Element":
					UIAElement._isEmptyList = True
					UIAHandler.handler.IUIAutomationFocusChangedEventHandler_HandleFocusChangedEvent(UIAElement)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		"""Elige las clases de superposición para el objeto NVDA."""
		if isinstance(obj, UIA) and hasattr(obj.UIAElement, "_isEmptyList"):
			clsList.insert(0, EmptyList)

	@script(gesture=None, description= _("Anuncia el escritorio virtual actual"), category= "EnhanceTools")
	def script_anuncia_escritorio(self, gesture):
		ui.message(obtener_nombre_escritorio())

	def terminate(self):
		"""Termina el plugin global y restaura la configuración."""
		IAccessibleHandler.winEventToNVDAEvent = self._winEventToNVDAEvent_native

