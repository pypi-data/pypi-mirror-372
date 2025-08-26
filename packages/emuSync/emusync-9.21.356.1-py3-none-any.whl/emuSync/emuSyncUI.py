import os
import webbrowser
import sys

# iconnect has to be imported before PySide6, otherwise app crashes
# with std::bad_cast???

from enum import Enum
from PySide6.QtCore import (QTimer, Qt, QEvent, QPoint)
from PySide6.QtWidgets import (QApplication, QLineEdit, QToolButton, QCheckBox, QPushButton, QTableWidget, QMainWindow,
                             QFileDialog, QMessageBox, QTableWidgetItem, QMenu, QHeaderView, QRadioButton)
from PySide6.QtGui import QIcon, QColor, QAction
from emuSync.engineController import EngineController
from emuSync.workspaceController import CPUState, CPUCommand
from emuSync.configurationController import LogLevel
import logging as log
from emuSync import ui_emuSyncUI
from pathlib import Path


class MainUI(QMainWindow, ui_emuSyncUI.Ui_EmuSync):
    def __init__(self, configurationFile):
        super(MainUI, self).__init__()
        self.setupUi(self)
        self.engineCtrl = EngineController()

        # Icon setup
        emuSyncIcon = QIcon()
        icon_path = os.path.join(os.path.dirname(__file__),'res', 'EmuSync.ico')
        emuSyncIcon.addFile(icon_path)
        self.setWindowIcon(emuSyncIcon)

        # Options menu
        self.setDemoMode = self.findChild(QAction, "actionUseDemoMode")
        self.setDemoMode.triggered.connect(self.toggleDemoMode)
        self.showModuleData = self.findChild(QAction, "actionModuleData")
        self.showModuleData.triggered.connect(self.showModuleDataMessageBox)

        # Logging menu
        self.loggingMenu = self.findChild(QMenu, "menuLogging")
        self.openLogFolder = self.findChild(QAction, "actionOpenLogFolder")
        self.openLogFolder.triggered.connect(self.openLoggingFolder)
        self.enableLogging1 = self.findChild(QAction, "actionLogging1")
        self.enableLogging1.triggered.connect(self.toggleLogging1)
        self.enableLogging2 = self.findChild(QAction, "actionLogging2")
        self.enableLogging2.triggered.connect(self.toggleLogging2)
        self.enableLogging3 = self.findChild(QAction, "actionLogging3")
        self.enableLogging3.triggered.connect(self.toggleLogging3)
        self.loggingOff = self.findChild(QAction, "actionOff")
        self.loggingOff.triggered.connect(self.disableLogging)

        self.setLoggingMenuVisible(isVisible=False)

        # Configuration section setup:
        self.configurationFilePath = self.findChild(QLineEdit, "configurationFilePath")
        self.configurationToolButton = self.findChild(QToolButton, "configurationToolButton")
        self.configurationToolButton.clicked.connect(self.openConfMenu)
        self.configurationAlwaysOnTopCB = self.findChild(QCheckBox, "alwaysOnTopCB")
        self.configurationAlwaysOnTopCB.toggled.connect(self.toggleStayOnTop)

        # Instance workspaces setup
        self.addButton = self.findChild(QPushButton, "addButton")
        self.addButton.clicked.connect(self.addButtonPressed)
        self.removeButton = self.findChild(QPushButton, "removeButton")
        self.removeButton.clicked.connect(self.removeButtonPressed)

        self.instancesTable = self.findChild(QTableWidget, "instancesTable")
        self.instancesTable.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.instancesTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.instancesTable.verticalHeader().setDefaultSectionSize(24)
        self.instancesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.instancesTable.installEventFilter(self)
        self.instancesTable.itemSelectionChanged.connect(self.updateSelectedInstance)

        # Selected instance setup
        self.launchButton = self.findChild(QPushButton, "launchButton")
        self.launchButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.LAUNCH))
        self.closeButton = self.findChild(QPushButton, "closeButton")
        self.closeButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.CLOSE))
        self.attachButton = self.findChild(QPushButton, "attachButton")
        self.attachButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.ATTACH))
        self.detachButton = self.findChild(QPushButton, "detachButton")
        self.detachButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.DETACH))
        self.runButton = self.findChild(QPushButton, "runButton")
        self.runButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.RUN))
        self.stopButton = self.findChild(QPushButton, "stopButton")
        self.stopButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.STOP))
        self.downloadButton = self.findChild(QPushButton, "downloadButton")
        self.downloadButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.DOWNLOAD))
        self.resetButton = self.findChild(QPushButton, "resetButton")
        self.resetButton.clicked.connect(lambda: self.sendOneCommand(CPUCommand.RESET))

        self.slaveRB = self.findChild(QRadioButton, "slaveRB")
        self.slaveRB.toggled.connect(self.slaveRBClicked)
        self.masterRB = self.findChild(QRadioButton, "masterRB")
        self.masterRB.toggled.connect(self.masterRBClicked)

        self.selectedInstance = self.selectedInstanceComboBox
        self.selectedInstance.currentIndexChanged.connect(self.selectedInstanceChanged)
        self.refreshSelectedInstances()

        # All instances setup

        self.launchAllButton = self.findChild(QPushButton, "launchAllButton")
        self.launchAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.LAUNCH))
        self.closeAllButton = self.findChild(QPushButton, "closeAllButton")
        self.closeAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.CLOSE))
        self.attachAllButton = self.findChild(QPushButton, "attachAllButton")
        self.attachAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.ATTACH))
        self.detachAllButton = self.findChild(QPushButton, "detachAllButton")
        self.detachAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.DETACH))
        self.runAllButton = self.findChild(QPushButton, "runAllButton")
        self.runAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.RUN))
        self.stopAllButton = self.findChild(QPushButton, "stopAllButton")
        self.stopAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.STOP))
        self.downloadAllButton = self.findChild(QPushButton, "downloadAllButton")
        self.downloadAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.DOWNLOAD))
        self.resetAllButton = self.findChild(QPushButton, "resetAllButton")
        self.resetAllButton.clicked.connect(lambda: self.sendAllCommands(CPUCommand.RESET))

        self.runSlavesCB = self.findChild(QCheckBox, "runSlavesCB")
        self.runSlavesCB.clicked.connect(self.runSlavesCBToggled)
        self.closeAllOnExitCB = self.findChild(QCheckBox, "closeAllCB")

        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="UI setup complete.")

        self.setAllButtonsActive(isActive=False)

        # Refresh UI periodically with timer
        self.refreshTimer = QTimer(self)
        self.refreshTimer.timeout.connect(self.refreshInstancesTable)
        self.refreshTimer.start(10)

        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="UI refresh timer started.")

        self.installEventFilter(self)
        self.show()
        self.activateWindow()

        self.loadConfiguration(configurationFile=configurationFile, isFirstLoad=True)

    def eventFilter(self, source, event):
        # If instances table is focused (row is selected) and user presses Esc, it will remove selection
        if ((source is self.instancesTable) and (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Escape) and
                (event.modifiers() == Qt.NoModifier)):
            self.instancesTable.setCurrentCell(-1, 0)
        elif ((source is self) and (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_F1) and (event.modifiers() == Qt.NoModifier)):
            helpUrl = r"https://www.isystem.com/downloads/winIDEA/help/emusync.html"
            webbrowser.open(helpUrl, new=0, autoraise=True)
        return super(MainUI, self).eventFilter(source, event)

    def openConfMenu(self):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Creating configuration menu.")
        # Create QMenu widget and add the actions
        configurationMenu = QMenu()
        actionNewConf = QAction("New", self)
        actionNewConf.triggered.connect(self.newConfClicked)
        actionOpenConf = QAction("Open", self)
        actionOpenConf.triggered.connect(self.openConfClicked)
        actionSaveConf = QAction("Save", self)
        actionSaveConf.triggered.connect(self.saveConfClicked)
        actionSaveAsConf = QAction("Save as", self)
        actionSaveAsConf.triggered.connect(self.saveAsConfClicked)
        configurationMenu.addAction(actionNewConf)
        configurationMenu.addAction(actionOpenConf)
        configurationMenu.addAction(actionSaveConf)
        configurationMenu.addAction(actionSaveAsConf)

        # Get tool button position
        widgetRelPos = self.configurationToolButton.mapToGlobal(QPoint(0, 0))
        # Set menu position to tool button position + tool button height (so menu appears right below tool button)
        menuX = widgetRelPos.x()
        menuY = widgetRelPos.y() + self.configurationToolButton.frameGeometry().height()
        configurationMenu.move(menuX, menuY)
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Menu coordinates: x = " + str(menuX) + ", y = " + str(menuY))
        # Show menu
        configurationMenu.exec()

    def showModuleDataMessageBox(self):
        if self.engineCtrl.confCtrl.isModuleDataLoaded():
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Module data found and loaded.")
            dlg = QMessageBox()
            dlg.setIcon(QMessageBox.NoIcon)
            dlg.setWindowTitle("Module information")
            moduleData = self.engineCtrl.confCtrl.getModuleData()
            moduleInfoText = ""
            for key in moduleData:
                moduleInfoText += "\n"
                moduleInfoText += key
                moduleInfoText += ":"
                moduleInfoText += "\n"
                for keyLow in moduleData[key]:
                    moduleInfoText += "    "
                    moduleInfoText += keyLow
                    moduleInfoText += ": "
                    moduleInfoText += str(moduleData[key][keyLow])
                    moduleInfoText += "\t\n"

            dlg.setText(moduleInfoText)
            dlg.exec()

        else:
            QMessageBox.critical(self, 'Error', 'Cannot find any loaded module data.', QMessageBox.Ok)
            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Cannot find module data.")

    def toggleLogging1(self):
        if self.enableLogging1.isChecked():
            self.enableLogging2.setChecked(False)
            self.enableLogging3.setChecked(False)
            self.loggingOff.setChecked(False)
            self.engineCtrl.setLoggingLevel(logLevel=LogLevel.HIGH)
        elif not self.enableLogging1.isChecked() and not self.enableLogging2.isChecked() and not self.enableLogging3.isChecked():
            self.engineCtrl.setLoggingLevel(logLevel=LogLevel.OFF)
            self.loggingOff.setChecked(True)

    def toggleLogging2(self):
        if self.enableLogging2.isChecked():
            self.enableLogging1.setChecked(False)
            self.enableLogging3.setChecked(False)
            self.loggingOff.setChecked(False)
            self.engineCtrl.setLoggingLevel(logLevel=LogLevel.MEDIUM)
        elif not self.enableLogging1.isChecked() and not self.enableLogging2.isChecked() and not self.enableLogging3.isChecked():
            self.engineCtrl.setLoggingLevel(logLevel=LogLevel.OFF)
            self.loggingOff.setChecked(True)

    def toggleLogging3(self):
        if self.enableLogging3.isChecked():
            self.enableLogging1.setChecked(False)
            self.enableLogging2.setChecked(False)
            self.loggingOff.setChecked(False)
            self.engineCtrl.setLoggingLevel(logLevel=LogLevel.LOW)
        elif not self.enableLogging1.isChecked() and not self.enableLogging2.isChecked() and not self.enableLogging3.isChecked():
            self.engineCtrl.setLoggingLevel(logLevel=LogLevel.OFF)
            self.loggingOff.setChecked(True)

    def disableLogging(self):
        if self.loggingOff.isChecked():
            self.enableLogging1.setChecked(False)
            self.enableLogging2.setChecked(False)
            self.enableLogging3.setChecked(False)
            self.engineCtrl.setLoggingLevel(logLevel=LogLevel.OFF)
        if not self.loggingOff.isChecked():
            self.loggingOff.setChecked(True)

    def extraInfoLogging(self, logLevel, logMsg):
        logger = log.getLogger("EmuSyncUILogger")
        if self.enableLogging3.isChecked() is True:
            if logLevel == LogLevel.MEDIUM:
                logger.warning(logMsg)
            elif logLevel == LogLevel.LOW:
                logger.error(logMsg)
        elif self.enableLogging2.isChecked() is True:
            if logLevel == LogLevel.HIGH:
                logger.info(logMsg)
            elif logLevel == LogLevel.MEDIUM:
                logger.warning(logMsg)
            elif logLevel == LogLevel.LOW:
                logger.error(logMsg)
        elif self.enableLogging1.isChecked() is True:
            if logLevel == LogLevel.HIGH:
                logger.info(logMsg)
                logger.info(str(self.engineCtrl.getInstanceDataList()))
            elif logLevel == LogLevel.MEDIUM:
                logger.warning(logMsg)
            elif logLevel == LogLevel.LOW:
                logger.error(logMsg)

    def toggleDemoMode(self):
        isChecked = self.setDemoMode.isChecked()
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="\"Use demo mode\" option toggled. Is checked: " + str(isChecked))
        self.engineCtrl.toggleDemoMode(isDemoEnabled=isChecked)

    def openLoggingFolder(self):
        scriptDir = os.path.dirname(__file__)
        relLogFilePath = "log"
        absLogFilePath = os.path.join(scriptDir, relLogFilePath)
        os.startfile(absLogFilePath)

    def refreshSelectedInstances(self):
        # Remove old and add new data.
        self.selectedInstance.clear()
        if self.engineCtrl.getNumberOfProcesses():
            instancesList = self.engineCtrl.getWorkspacesList()
            self.selectedInstance.addItems(instancesList)

    def updateSelectedInstance(self):
        selectedRows = self.instancesTable.selectionModel().selectedRows()
        for index in sorted(selectedRows):
            #self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Selected instance now: " + str(self.instancesTable.item(index.row(), 2).text()))
            self.selectedInstance.setCurrentIndex(index.row())

    def refreshInstancesTable(self):
        # Save selected index if row is selected
        selectedRow = self.instancesTable.currentRow()

        # Remove old table entries.
        self.engineCtrl.checkForStatusUpdates()
        self.instancesTable.setRowCount(0)
        # Get new data and input it into the Table.
        tableData = self.engineCtrl.getInstanceDataList()
        if len(tableData) == 0:
            self.setAllButtonsActive(isActive=False)
            self.instancesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.instancesTable.horizontalHeader().setStretchLastSection(True)
        else:
            self.instancesTable.horizontalHeader().setStretchLastSection(False)
            self.refreshInstanceButtons(instanceIndex=self.selectedInstance.currentIndex())
            self.refreshAllInstancesButtons()

        for instance in tableData:
            rowPosition = self.instancesTable.rowCount()
            self.instancesTable.insertRow(rowPosition)
            for j in range(len(instance)):
                self.instancesTable.setItem(rowPosition, j, QTableWidgetItem(instance[j]))
            self.setStatusCellColor(rowPosition)

        # Resize columns to content at end of data refresh
        self.instancesTable.resizeColumnsToContents()
        self.instancesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # Select same row as before
        if ((selectedRow < self.instancesTable.rowCount()) and (selectedRow >= 0)):
            self.instancesTable.setCurrentCell(selectedRow, 0)

        # Remove selection from table (so it doesn't stay grey/selected)
        if ((QApplication.focusWidget() is not self.instancesTable) and (QApplication.focusWidget() is not self.removeButton)):
            self.removeTableSelection()

    def removeTableSelection(self):
        self.instancesTable.setCurrentCell(-1, 0)

    def setStatusCellColor(self, rowPosition):
        if self.instancesTable.item(rowPosition, 1).text() == CPUState.OFFLINE.value:
            self.instancesTable.item(rowPosition, 1).setBackground(QColor(128, 0, 0))
            self.instancesTable.item(rowPosition, 1).setForeground(QColor(255, 255, 0))
        elif self.instancesTable.item(rowPosition, 1).text() == CPUState.RUNNING.value:
            self.instancesTable.item(rowPosition, 1).setBackground(QColor(0, 255, 0))
            self.instancesTable.item(rowPosition, 1).setForeground(QColor(0, 0, 0))
        elif self.instancesTable.item(rowPosition, 1).text() == CPUState.STOPPED.value:
            self.instancesTable.item(rowPosition, 1).setBackground(QColor(0, 128, 0))
            self.instancesTable.item(rowPosition, 1).setForeground(QColor(255, 255, 255))
        elif self.instancesTable.item(rowPosition, 1).text() == CPUState.NOTATTACHED.value:
            self.instancesTable.item(rowPosition, 1).setForeground(QColor(0, 0, 0))
        else:
            self.instancesTable.item(rowPosition, 1).setBackground(QColor(128, 0, 128))
            self.instancesTable.item(rowPosition, 1).setForeground(QColor(255, 255, 255))

    def saveAsPromptAndSave(self):
        configurationSavePath = QFileDialog.getSaveFileName(self, "Select file name and location.", '', "EmuSync Configuration File(*.EmuSync)")
        savePath = str(configurationSavePath[0])
        try:
            savePathRel = os.path.relpath(savePath)
        except ValueError as exception:
            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Cannot create relative path: " + str(exception))
            savePathRel = savePath
        if savePathRel != "":
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Configuration file selected. Saving to " + savePathRel)
            # If user selected save file
            self.configurationFilePath.setText(savePathRel)
            self.engineCtrl.setConfigurationFilePath(savePathRel)
            self.engineCtrl.confCtrl.saveConfiguration()
        else:
            # If save file dialog dismissed, ignore click
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Configuration file selection cancelled. ")
            return

    def saveConfClicked(self):
        if self.engineCtrl.confCtrl.isDataLoadedAndChanged():
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Save configuration button clicked.")
            if self.configurationFilePath.text() == "":
                self.extraInfoLogging(logLevel=LogLevel.MEDIUM, logMsg="No file path specified.")
                # Else: ask where to save file
                self.saveAsPromptAndSave()
            else:
                self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Saving configuration to " + self.engineCtrl.confCtrl.fileName)
                # If path known: save changes
                self.engineCtrl.confCtrl.saveConfiguration()

    def saveAsConfClicked(self):
        if self.engineCtrl.confCtrl.isDataLoaded():
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Save as configuration button clicked.")
            # ask where to save file
            self.saveAsPromptAndSave()

    def newConfClicked(self):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="New configuration button triggered.")

        if self.engineCtrl.confCtrl.isDataLoadedAndChanged():
            buttonClicked = QMessageBox.question(
                self, 'Quitting application...', 'Save changes made to the configurations file?', QMessageBox.Yes | QMessageBox.No
                | QMessageBox.Cancel)
            if buttonClicked == QMessageBox.Cancel:
                # If "Cancel" clicked, ignore click.
                self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Save prompt cancelled.")
                return
            else:
                if buttonClicked == QMessageBox.Yes:
                    # If "Yes" clicked: check if file path already selected
                    if self.engineCtrl.isConfigurationFilePathSet():
                        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Saving configuration to " + self.engineCtrl.confCtrl.fileName)
                        # If path known: save changes
                        self.engineCtrl.confCtrl.saveConfiguration()
                    else:
                        self.extraInfoLogging(logLevel=LogLevel.MEDIUM, logMsg="No file path specified.")
                        # Else: ask where to save file
                        self.saveAsPromptAndSave()
                # Remove old instances and add new configuration.
                self.engineCtrl.terminateAll(isCloseChecked=False)
                self.configurationFilePath.setText("")
                # Refresh UI
                self.setLoggingMenuVisible(False)
                self.refreshSelectedInstances()
                self.refreshInstancesTable()
        self.configurationFilePath.setText("")
        self.engineCtrl.terminateAll(isCloseChecked=False)
        self.engineCtrl.confCtrl.createNewConfiguration()
        self.refreshSelectedInstances()

    def openConfClicked(self):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Open Configuration button triggered.")
        # Open File Dialog and show selected path. Filter for yaml files only.
        configurationFilePathText = QFileDialog.getOpenFileName(
            self, "Select configuration file", os.path.expanduser('~'),
            "EmuSync Configuration File(*.EmuSync)")
        savePath = str(configurationFilePathText[0])
        try:
            savePathRel = os.path.relpath(savePath)
        except ValueError as exception:
            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Cannot create relative path: " + str(exception))
            savePathRel = savePath
        if savePathRel != '':
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Configuration file selected: " + str(savePathRel))
            self.configurationFilePath.setText("")
            self.loadConfiguration(configurationFile=savePathRel, isFirstLoad=False)
        else:
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="No file selected.")

    def slaveRBClicked(self):
        # Check if selectedWorkspace index is within normal bounds
        selectedInstanceIndex = self.selectedInstance.currentIndex()
        if selectedInstanceIndex >= 0:
            # If CB is checked, set as Slave, if it is unchecked, set as Master.
            if self.slaveRB.isChecked():
                self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Workspace " + str(self.selectedInstance.currentText()) + " set to slave.")
                self.engineCtrl.setSlave(listIndex=selectedInstanceIndex)
                if self.masterRB.isChecked():
                    self.masterRB.setChecked(False)
            else:
                self.engineCtrl.setMaster(listIndex=selectedInstanceIndex)
                self.masterRB.setChecked(True)
            self.refreshInstancesTable()

    def masterRBClicked(self):
        # Check if selectedWorkspace index is within normal bounds
        selectedInstanceIndex = self.selectedInstance.currentIndex()
        if selectedInstanceIndex >= 0:
            # If CB is checked, set as Master, if it is unchecked, set as Slave.
            if self.masterRB.isChecked():
                self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Workspace " + str(self.selectedInstance.currentText()) + " set to master.")
                self.engineCtrl.setMaster(listIndex=selectedInstanceIndex)
                if self.slaveRB.isChecked():
                    self.slaveRB.setChecked(False)
            else:
                self.engineCtrl.setSlave(listIndex=selectedInstanceIndex)
                self.slaveRB.setChecked(True)
            self.refreshInstancesTable()

    def selectedInstanceChanged(self, value):
        if self.engineCtrl.getNumberOfProcesses():
            # Update Slave/Master CB when selected instance is changed.
            if self.engineCtrl.isMasterProcess(value):
                self.masterRB.setChecked(True)
                self.slaveRB.setChecked(False)
            else:
                self.masterRB.setChecked(False)
                self.slaveRB.setChecked(True)
        else:
            self.masterRB.setChecked(False)
            self.slaveRB.setChecked(False)

    def closeEvent(self, event):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Close event detected.")
        # Check if any data has been loaded and changed (comparing to selected configurations file)
        if self.engineCtrl.confCtrl.isDataLoadedAndChanged():
             # Ask user if they want to save changes to Configurations
            buttonClicked = QMessageBox.question(
                self, 'Quitting application...', 'Save changes made to the configurations file?', QMessageBox.Yes | QMessageBox.No
                | QMessageBox.Cancel)
            if buttonClicked == QMessageBox.Cancel:
                # If "Cancel" clicked, ignore exit event.
                self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Save prompt cancelled.")
                event.ignore()
                return
            else:
                # If "No" or "Yes" clicked:
                if buttonClicked == QMessageBox.Yes:
                    # If "Yes" clicked: check if file path already selected
                    if self.engineCtrl.isConfigurationFilePathSet():
                        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Saving configuration to " + self.engineCtrl.confCtrl.fileName)
                        # If path known: save changes
                        self.engineCtrl.confCtrl.saveConfiguration()
                    else:
                        self.extraInfoLogging(logLevel=LogLevel.MEDIUM, logMsg="No file path specified.")
                        # Else: ask where to save file
                        configurationSavePath = QFileDialog.getSaveFileName(
                            self, "Select file name and location.", '', "EmuSync Configuration File(*.EmuSync)")
                        savePath = str(configurationSavePath[0])
                        try:
                            savePathRel = os.path.relpath(savePath)
                        except ValueError as exception:
                            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Cannot create relative path: " + str(exception))
                            savePathRel = savePath
                        if savePathRel != '':
                            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Configuration file selected. Saving to " + str(savePathRel))
                            # If user selected save file
                            self.engineCtrl.setConfigurationFilePath(str(savePathRel))
                            self.engineCtrl.confCtrl.saveConfiguration()
                        else:
                            # If save file dialog dismissed, ignore exit event.
                            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Configuration file selection cancelled. ")
                            event.ignore()
                            return
        # If this is reached, check "Close all on exit" CB for winIDEA close option, terminate processes and accept close event.
        self.extraInfoLogging(logLevel=LogLevel.MEDIUM, logMsg="Configurations file not changed or loaded.")
        self.engineCtrl.terminateAll(isCloseChecked=self.closeAllOnExitCB.isChecked())
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Accepting close event.")
        event.accept()

    def loadConfiguration(self, configurationFile, isFirstLoad=False):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Loading configuration.")
        # Remove old instances and add new configuration.
        self.engineCtrl.terminateAll(isCloseChecked=False)
        configurationFilePath = Path(configurationFile)
        if configurationFilePath.is_file():
            if str(configurationFilePath).endswith(".EmuSync"):
                self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Adding configurations from file...")
                isLoaded = self.engineCtrl.addFileConfigurations(filePath=str(configurationFilePath))
                if not isLoaded:
                    # Could not load file. Likely wrong file structure.
                    QMessageBox.warning(self, 'Loading file failed.', 'Please check the configurations file format/data.', QMessageBox.Ok)
                    self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Error during load. Please check the configurations file format/data.")
                    if isFirstLoad:
                        self.loadConfiguration("configurations.EmuSync", False)
                else:
                    self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Load successful.")
                    self.setLoggingMenuVisible(self.engineCtrl.confCtrl.isLoggingEnabled())
                    self.configurationFilePath.setText(configurationFile)
            else:
                # Incorrect file type error
                QMessageBox.warning(self, "Incorrect file type", "Incorrect file type. Configuration files use .EmuSync extension.", QMessageBox.Ok)
                self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Configuration file " + configurationFile + " has wrong file type extension.")
                self.engineCtrl.resetConfigurationCtrl()
                if isFirstLoad:
                    self.loadConfiguration(configurationFile="configurations.EmuSync", isFirstLoad=False)
        else:
            # File not found / doesn't exist error.
            warningMsg = "Configuration file " + configurationFile + " doesn't exist."
            QMessageBox.warning(self, "File not found", warningMsg, QMessageBox.Ok)
            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Configuration file " + configurationFile + " doesn't exist.")
            self.engineCtrl.resetConfigurationCtrl()
            if isFirstLoad:
                self.engineCtrl.confCtrl.createNewConfiguration()
                self.engineCtrl.confCtrl.saveConfiguration(configurationFile)
                self.loadConfiguration(configurationFile=configurationFile, isFirstLoad=False)

        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Refreshing UI.")
        self.refreshSelectedInstances()
        self.refreshInstancesTable()

    def addButtonPressed(self):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Add button pressed.")
        # Open file dialog (.xjrf filter), add new workspace as slave and update UI.
        newWorkspace = QFileDialog.getOpenFileName(self, "Select workspace file", '', "winIDEA workspace (*.xjrf)")
        try:
            wsPathRel = os.path.relpath(newWorkspace[0], os.path.dirname(os.path.abspath(self.engineCtrl.confCtrl.fileName)))
        except ValueError as exception:
            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg="Cannot create relative path: " + str(exception))
            wsPathRel = newWorkspace[0]
        if wsPathRel != '':
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Adding workspace: " + wsPathRel)
            self.engineCtrl.addWorkspace(wsPath=wsPathRel)
            self.refreshInstancesTable()
            self.refreshSelectedInstances()

    def removeButtonPressed(self):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Remove button pressed.")
        # Remove workspace corresponding to selected row in Instance Table.
        selectedRows = self.instancesTable.selectionModel().selectedRows()
        for index in sorted(selectedRows):
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Removing workspace: " + str(self.instancesTable.item(index.row(), 2).text()))
            self.engineCtrl.removeWorkspace(index=index.row())
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="Refreshing UI.")
        self.refreshSelectedInstances()
        self.removeTableSelection()
        self.refreshInstancesTable()
        self.refreshSelectedInstances()

    def sendOneCommand(self, commandForOne):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg=commandForOne.value + " button pressed.")
        selectedWorkspace = self.selectedInstance.currentIndex()
        if ((selectedWorkspace >= 0) and (selectedWorkspace < self.engineCtrl.getNumberOfProcesses())):
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg=str(commandForOne.value) + ": " + self.selectedInstance.currentText())
            self.engineCtrl.commandOne(command=commandForOne, listIndex=selectedWorkspace)
        else:
            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg=Errors.oneButtonErrorString.value)
            self.invalidWorkspaceError()

    def sendAllCommands(self, commandForAll):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg=commandForAll.value + " all button pressed.")
        numOfProcesses = self.engineCtrl.getNumberOfProcesses()
        if numOfProcesses:
            self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg=str(commandForAll.value) + ": " + str(numOfProcesses) + " winIDEA processes.")
            self.engineCtrl.commandAll(commandForAll)
        else:
            self.extraInfoLogging(logLevel=LogLevel.LOW, logMsg=Errors.allButtonsErrorString.value)
            self.noWorkspacesError()

    def runSlavesCBToggled(self):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="\"Run slaves when master runs\" toggled. Is checked: " +
                              str(self.runSlavesCB.isChecked()))
        self.engineCtrl.toggleRunSlaves()

    def toggleStayOnTop(self):
        self.extraInfoLogging(logLevel=LogLevel.HIGH, logMsg="\"Stay on top\" toggled. Is checked: " +
                              str(self.configurationAlwaysOnTopCB.isChecked()))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        self.show()

    def invalidWorkspaceError(self):
        QMessageBox.critical(self, 'Error', 'Invalid workspace selected', QMessageBox.Ok)

    def noWorkspacesError(self):
        QMessageBox.critical(self, 'Error', 'No workspaces found.\nPlease add or load configurations.', QMessageBox.Ok)

    def setAllButtonsActive(self, isActive):
        self.launchButton.setEnabled(isActive)
        self.launchAllButton.setEnabled(isActive)
        self.closeButton.setEnabled(isActive)
        self.closeAllButton.setEnabled(isActive)
        self.attachButton.setEnabled(isActive)
        self.attachAllButton.setEnabled(isActive)
        self.detachButton.setEnabled(isActive)
        self.detachAllButton.setEnabled(isActive)
        self.runButton.setEnabled(isActive)
        self.runAllButton.setEnabled(isActive)
        self.stopButton.setEnabled(isActive)
        self.stopAllButton.setEnabled(isActive)
        self.downloadButton.setEnabled(isActive)
        self.downloadAllButton.setEnabled(isActive)
        self.resetButton.setEnabled(isActive)
        self.resetAllButton.setEnabled(isActive)

        self.slaveRB.setEnabled(isActive)
        self.masterRB.setEnabled(isActive)
        self.runSlavesCB.setEnabled(isActive)
        self.closeAllOnExitCB.setEnabled(isActive)

        self.selectedInstance.setEnabled(isActive)
        self.removeButton.setEnabled(isActive)

    def refreshInstanceButtons(self, instanceIndex):
        isInstanceConnected = self.engineCtrl.isInstanceConnected(listIndex=instanceIndex)
        instanceStatus = self.engineCtrl.getWorkspaceStatus(processIndex=instanceIndex)

        if isInstanceConnected:
            self.launchButton.setEnabled(False)
            self.attachButton.setEnabled(False)
            self.closeButton.setEnabled(True)
            self.detachButton.setEnabled(True)
            self.downloadButton.setEnabled(True)
            self.resetButton.setEnabled(True)
            if instanceStatus == CPUState.RUNNING.value:
                self.runButton.setEnabled(False)
                self.stopButton.setEnabled(True)
            else:
                self.runButton.setEnabled(True)
                self.stopButton.setEnabled(False)
        else:
            self.launchButton.setEnabled(True)
            self.attachButton.setEnabled(True)
            self.closeButton.setEnabled(False)
            self.detachButton.setEnabled(False)
            self.runButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.downloadButton.setEnabled(False)
            self.resetButton.setEnabled(False)

        self.slaveRB.setEnabled(True)
        self.masterRB.setEnabled(True)
        self.runSlavesCB.setEnabled(True)
        self.closeAllOnExitCB.setEnabled(True)

        self.selectedInstance.setEnabled(True)
        self.removeButton.setEnabled(True)

    def refreshAllInstancesButtons(self):
        isInstanceListConnected = self.engineCtrl.isInstanceListConnected()

        if isInstanceListConnected:
            self.launchAllButton.setEnabled(True)
            self.attachAllButton.setEnabled(True)
            self.closeAllButton.setEnabled(True)
            self.detachAllButton.setEnabled(True)
            self.runAllButton.setEnabled(True)
            self.stopAllButton.setEnabled(True)
            self.downloadAllButton.setEnabled(True)
            self.resetAllButton.setEnabled(True)
        else:
            self.launchAllButton.setEnabled(True)
            self.attachAllButton.setEnabled(True)
            self.closeAllButton.setEnabled(False)
            self.detachAllButton.setEnabled(False)
            self.runAllButton.setEnabled(False)
            self.stopAllButton.setEnabled(False)
            self.downloadAllButton.setEnabled(False)
            self.resetAllButton.setEnabled(False)

    def setLoggingMenuVisible(self, isVisible):
        self.loggingMenu.menuAction().setVisible(isVisible)
        self.loggingOff.setChecked(True)


class Errors(Enum):
    allButtonsErrorString = "No workspaces found. Command ignored."
    oneButtonErrorString = "No workspace selected. Command ignored."


def main(configurationPath='configurations.EmuSync'):
    #dirPath = os.path.dirname(os.path.realpath(__file__))
    homePath = os.path.expanduser('~')
    logDir = os.path.join(homePath, "emuSyncLog")
    Path(logDir).mkdir(parents=True, exist_ok=True)
    if not os.path.isdir(logDir):
        os.makedirs(logDir)
    logPath = os.path.join(logDir, 'emuSyncUI.log')
    log.basicConfig(filename=logPath, filemode='w', level=log.INFO)

    if os.name == 'nt':
        sys.argv += ['-platform', 'windows:darkmode=1']
    app = QApplication(sys.argv)
    MainUI(configurationFile=configurationPath)
    app.exec()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        confFile = str(sys.argv[1])
        main(configurationPath=confFile)
    else:
        main()
