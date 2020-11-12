"""
/***************************************************************************
 Pomodoro
                                 A QGIS plugin
 Pomodoro for improvements on productivity
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-01-22
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Eliton
        email                : eliton.filho@eb.mil.br
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QLabel, QHBoxLayout
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
import os.path
from .pomodoro_dockwidget import PomodoroDockWidget
from .handlePomodoro import HandlePomodoro
from .monitorCanvas import MonitorCanvas


class Pomodoro:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # Declare instance attributes
        self.actions = []
        self.menu = u'&Pomodoro'
        self.toolbar = self.iface.addToolBar(u'Pomodoro')
        self.toolbar.setObjectName(u'Pomodoro')

        # Initialize Pomodoro

        self.pluginIsActive = False
        self.dockwidget = None

        self._thread = HandlePomodoro()
        self.monitor = MonitorCanvas()
        # self.monitor.start()
        # self._thread.start()
        self.monitor.startMonitoring()

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
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        pass
        """ icon_path = ':/plugins/pomodoro/icon.png'
        self.add_action(
            icon_path,
            text=u'Pomodoro',
            callback=self.run,
            parent=self.iface.mainWindow())
        # Calls run() when initialization is complete
        self.iface.initializationCompleted.connect(self.run) """

    def handleVisibility(self):
        if self.dockwidget and not self.pluginIsActive:
            self.dockwidget.show()

    def handleSignals(self):
        # Triggers onClosePlugin when dockwidget is closed
        self.dockwidget.closingPlugin.connect(self.onClosePlugin)
        # Triggers updateHistoricByButton when button is pressed
        self.dockwidget.pushButton.clicked.connect(
            self.updateHistoricByButton)
        # Connect pyqtsignal to refresh screen
        self._thread.updateTimer.connect(self.updateLCD)
        # Connect pyqtsignal to refresh historic
        self._thread.updateHistoric.connect(self.updateHistoric)
        # Connect pyqtsignal from monitor
        self.monitor.updateByMonitor.connect(self.updateHistoricByMonitor)
        # Connect pyqtsignal from monitor (update statistics)
        self.monitor.updateTickTimer.connect(self.updateTextLabels)

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self._thread.terminate()
        self.monitor.terminate()

        # for action in self.actions:
        #     self.iface.removePluginMenu(
        #         u'&Pomodoro',
        #         action)
        #     self.iface.removeToolBarIcon(action)
        # # remove the toolbar
        # del self.toolbar

    def onStart(self):
        """Starts the thread"""
        self._thread.start()

    def closeEvent(self, event):
        if self._thread.isRunning():
            # self._thread.quit()
            self._thread.terminate()
        if self.monitor.isRunning():
            # self.monitor.quit()
            self.monitor.terminate()
        del self._thread
        del self.monitor

    def updateLCD(self):
        self.dockwidget.lcdNumber.display(self._thread.lcdString())

    def updateTextLabels(self):
        workTime = int(self.monitor.vars['workTime'])
        idleTime = int(self.monitor.vars['idleTime'])
        denom = workTime + idleTime
        if not denom:
            denom = 1

        self.dockwidget.label_1.setText('Estatística de uso (sucesso/falha): {}/{}'.format(
            self._thread.vars['sThisSession'],
            self._thread.vars['fThisSession']
        ))
        self.dockwidget.label_2.setText('Tempo de trabalho: {} min ({:.2f}%)'.format(
            workTime,
            100*workTime/(denom),
        ))
        self.dockwidget.label_3.setText('Tempo ocioso: {} min ({:.2f}%)'.format(
            idleTime,
            100*idleTime/(denom),
        ))
        self.dockwidget.label_4.setText('Maior tempo contínuo de trabalho: {} min'.format(
            self.monitor.vars['greatWorkTime']
        ))
        self.dockwidget.label_5.setText('Maior tempo contínuo de ócio: {} min'.format(
            self.monitor.vars['greatIdleTime']
        ))
        self.dockwidget.label_6.setText('Ocioso há: {} min'.format(
            self.monitor.vars['idleSince']
        ))
        self.dockwidget.label_firstAcess.setText('Primeiro acesso às: {}'.format(
            self.monitor.vars['timeFirstAcess']
        ))

    def deleteLayoutItems(self):
        for idx in range(self.dockwidget.testeLayout.count()):
            item = self.dockwidget.testeLayout.itemAt(idx)
            if item is None:
                continue
            item.widget().deleteLater()

    def updateHistoric(self):
        # TODO: Append dinamically using deleteLayoutItems
        # 1: Works dinamically, but there's no limit
        #hbox = QHBoxLayout()
        # label = QLabel()
        # last = self._thread.session['historic'][-1]
        # if last:
        #     label.setPixmap(self.dockwidget.sucess)
        #     self.dockwidget.testeLayout.addWidget(label)
        # else:
        #     label.setPixmap(self.dockwidget.fail)
        #     self.dockwidget.testeLayout.addWidget(label)
        # #self.dockwidget.testeLayout.addLayout(hbox)
        # if len(self._thread.session['historic']) > 3:
        #     self.deleteLayoutItems()

        # 2: Inserts 1, 2, 3...
        # hbox = QHBoxLayout()
        # for _id, item in enumerate(self._thread.session['historic']):
        #     label = QLabel()
        #     if item:
        #         label.setPixmap(self.dockwidget.sucess)
        #         hbox.addWidget(label)
        #     else:
        #         label.setPixmap(self.dockwidget.fail)
        #         hbox.addWidget(label)
        # self.dockwidget.testeLayout.addLayout(hbox)

        # 3: Works well, but needs to pre-define layouts on ui
        items = ['icon_0', 'icon_1', 'icon_2',
                 'icon_3', 'icon_4', 'icon_5', 'icon_6']
        historic = self._thread.session['historic'].copy()
        layout = self.dockwidget.dockWidgetContents.children()
        for item in items:
            child = self.dockwidget.dockWidgetContents.findChild(QLabel, item)
            try:
                status = historic.pop()
            except IndexError:
                break
            if status:
                child.setPixmap(self.dockwidget.sucess)
            else:
                child.setPixmap(self.dockwidget.fail)
        self.updateTextLabels()

        # hbox = QHBoxLayout()
        # for _id, item in enumerate(self._thread.session['historic']):
        #     label = QLabel()
        #     if item:
        #         label.setPixmap(self.dockwidget.sucess)
        #         hbox.addWidget(label)
        #     else:
        #         label.setPixmap(self.dockwidget.fail)
        #         hbox.addWidget(label)
        # self.dockwidget.label.setLayout(hbox)

    def updateHistoricByMonitor(self):
        '''Triggered by MonitorCanvas'''
        if self._thread.isTimerRunning:
            self._thread.refreshPomodoroByMonitor(self.monitor.isMonitoring)
            self.monitor.stopMonitoring()

    def updateHistoricByButton(self):
        '''Triggered when Novo Pomodoro button is pressed'''
        self._thread.refreshPomodoroByButton(self.monitor.isMonitoring)
        self.monitor.startMonitoring()

    def run(self):
        """Run method that loads and starts the plugin"""

        self.handleVisibility()

        if not self.pluginIsActive:
            self.pluginIsActive = True
            if self.dockwidget == None:
                # Create the dockwidget and keep reference
                self.dockwidget = PomodoroDockWidget()
            # Connect signals
            self.handleSignals()
            # Updates LCD and statistics
            self.updateTextLabels()
            self.updateLCD()

            # Starts Threads
            self._thread.start()
            self.monitor.start()

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

    def getWidget(self):
        """Run method that loads and starts the plugin"""

        self.handleVisibility()

        if not self.pluginIsActive:
            self.pluginIsActive = True
            if self.dockwidget == None:
                # Create the dockwidget and keep reference
                self.dockwidget = PomodoroDockWidget()
            # Connect signals
            self.handleSignals()
            # Updates LCD and statistics
            self.updateTextLabels()
            self.updateLCD()

            # Starts Threads
            self._thread.start()
            self.monitor.start()

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            #self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        return self.dockwidget
