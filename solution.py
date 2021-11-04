# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SBRP
                                 A QGIS plugin
 A plugin for QGIS solve SBRP

                              -------------------
        begin                : 2020-02-23
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Andyx
        email                : ahernandezal@ceis.cujae.edu.cu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
import sys

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from os import getcwd,chmod
import processing
import os.path as P
from .Connection_2_Jar import Connection
from .sbrprocessing import SBRProcessingProvider





class SBRP:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.
        :param iface:Instancia de la interfaz de QGIS para manipular la aplicacion en tiempo de
               ejecucion
        :type iface: QgsInterface
        """
        self.iface = iface

        #para controlar las rubber bandas al construir el plugin y eliminar en caso de desicion del usuario
        self.rubber = []
        self.stopsAux = [] #stopLayer
        self.layerControl=[]
        self.annota = [] #controlar la anotation
        self.students_colors = [] #controla los colores de los estudiantes a las paradas

        #Directorio del plugin
        self.plugin_dir = os.path.dirname(__file__)


        # QAction para la interfaz de QGIS
        self.actions = []
        self.menu = self.tr(u'&SBRP')

    def tr(self, message):
        return QCoreApplication.translate('SBRP', message)

    #Esto esta super
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initprocessing(self):
        self.provider = SBRProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.initprocessing()


        icon_path = ':/plugins/solution/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'SBRP solution'),
            callback=self.run,
            parent=self.iface.mainWindow(),add_to_toolbar=False)





    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI.Generado por defecto"""
        QgsApplication.processingRegistry().removeProvider(self.provider)
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&SBRP'),
                action)


    def run(self,text):
        processing.execAlgorithmDialog('sbrprocessingprovider:sbrprocessing')



