"""
GeoAI Assistant Simple - Minimal QGIS Plugin Entry Point
Simple, beginner-friendly SQL generation with core features
"""

import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsMessageLog, Qgis

from .modules.llm_handler import LLMHandler
from .modules.sql_executor import SQLExecutor
from .modules.image_processor import ImageProcessor
from .ui.simple_dialog import SimpleDialog


class GeoAIAssistant:
    """QGIS Plugin Implementation - Simple Version with Core Features"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Initialize components
        self.actions = []
        self.menu = '&GeoAI Assistant Simple'
        self.toolbar = self.iface.addToolBar('GeoAI Assistant Simple')
        self.toolbar.setObjectName('GeoAIAssistantSimple')
        
        # Initialize modules
        self.llm_handler = None
        self.sql_executor = None
        self.image_processor = None
        
        # Dialog
        self.dialog = None

    def initGui(self):
        """Create the menu entries and toolbar icons"""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        
        # Main action
        self.add_action(
            icon_path,
            text='Open GeoAI Assistant Simple',
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_toolbar=True
        )

    def add_action(self, icon_path, text, callback, parent=None, add_to_toolbar=False):
        """Add a toolbar icon and menu item"""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        
        if add_to_toolbar:
            self.toolbar.addAction(action)
        
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        
        return action

    def initialize_modules(self):
        """Initialize core modules"""
        try:
            self.llm_handler = LLMHandler()
            self.sql_executor = SQLExecutor(self.iface)
            self.image_processor = ImageProcessor(self.llm_handler)
            
            QgsMessageLog.logMessage(
                'GeoAI Assistant Simple modules initialized successfully',
                'GeoAI Simple',
                Qgis.Info
            )
        except Exception as e:
            QgsMessageLog.logMessage(
                f'Error initializing modules: {str(e)}',
                'GeoAI Simple',
                Qgis.Critical
            )

    def run(self):
        """Run method that performs all the real work"""
        # Initialize modules if not already done
        if self.llm_handler is None:
            self.initialize_modules()
        
        if self.dialog is None:
            self.dialog = SimpleDialog(
                self.iface,
                self.llm_handler,
                self.sql_executor,
                self.image_processor
            )
            # Add as dock widget and ensure it is docked (not floating)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dialog)
            try:
                self.dialog.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
                self.dialog.setFloating(False)
            except Exception:
                pass
        
        self.dialog.show()
        QgsMessageLog.logMessage("GeoAI Assistant Simple opened", "GeoAI Simple", Qgis.Info)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI"""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        
        if self.dialog:
            self.iface.removeDockWidget(self.dialog)
            self.dialog.deleteLater()
            self.dialog = None
        
        del self.toolbar
