# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'emuSyncUIayADQs.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QComboBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLayout, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QRadioButton, QSizePolicy, QStatusBar, QTableWidget,
    QTableWidgetItem, QToolButton, QWidget)

class Ui_EmuSync(object):
    def setupUi(self, EmuSync):
        if not EmuSync.objectName():
            EmuSync.setObjectName(u"EmuSync")
        EmuSync.resize(455, 590)
        EmuSync.setWindowTitle(u"EmuSync")
        self.useDemoModeAction = QAction(EmuSync)
        self.useDemoModeAction.setObjectName(u"useDemoModeAction")
        self.useDemoModeAction.setCheckable(True)
        self.actionUseDemoMode = QAction(EmuSync)
        self.actionUseDemoMode.setObjectName(u"actionUseDemoMode")
        self.actionUseDemoMode.setCheckable(True)
        self.actionOpenLogFile = QAction(EmuSync)
        self.actionOpenLogFile.setObjectName(u"actionOpenLogFile")
        self.actionOpenLogFile.setCheckable(False)
        self.actionOpenLogFolder = QAction(EmuSync)
        self.actionOpenLogFolder.setObjectName(u"actionOpenLogFolder")
        self.actionOpenLogFolder.setCheckable(False)
        self.actionLevel_1 = QAction(EmuSync)
        self.actionLevel_1.setObjectName(u"actionLevel_1")
        self.actionLevel_2 = QAction(EmuSync)
        self.actionLevel_2.setObjectName(u"actionLevel_2")
        self.actionLogging1 = QAction(EmuSync)
        self.actionLogging1.setObjectName(u"actionLogging1")
        self.actionLogging1.setCheckable(True)
        self.actionLogging2 = QAction(EmuSync)
        self.actionLogging2.setObjectName(u"actionLogging2")
        self.actionLogging2.setCheckable(True)
        self.actionLogging3 = QAction(EmuSync)
        self.actionLogging3.setObjectName(u"actionLogging3")
        self.actionLogging3.setCheckable(True)
        self.actionModuleData = QAction(EmuSync)
        self.actionModuleData.setObjectName(u"actionModuleData")
        self.actionOff = QAction(EmuSync)
        self.actionOff.setObjectName(u"actionOff")
        self.actionOff.setCheckable(True)
        self.centralwidget = QWidget(EmuSync)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"#centralwidget {\n"
"	margin: 50px;\n"
"}")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.allGroupBox = QGroupBox(self.centralwidget)
        self.allGroupBox.setObjectName(u"allGroupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.allGroupBox.sizePolicy().hasHeightForWidth())
        self.allGroupBox.setSizePolicy(sizePolicy)
        self.allGroupBox.setMaximumSize(QSize(16777215, 150))
        self.allGroupBox.setStyleSheet(u"QGroupBox {\n"
"	border:1px solid gray;\n"
"	border-radius: 5px;\n"
"	margin-left: 0.5em;\n"
"	margin-right: 0.5em;\n"
"	margin-top: 1em;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 24px;\n"
"	top:6px;\n"
"	padding: 0 3px 0 3px;\n"
"}")
        self.gridLayout_5 = QGridLayout(self.allGroupBox)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridFrameAll = QFrame(self.allGroupBox)
        self.gridFrameAll.setObjectName(u"gridFrameAll")
        self.gridFrameAll.setStyleSheet(u"QFrame {\n"
"	padding-left: 0.5em;\n"
"	padding-right: 0.5em;\n"
"}")
        self.gridFrameAll.setFrameShape(QFrame.NoFrame)
        self.gridFrameAll.setLineWidth(2)
        self.gridLayout_3 = QGridLayout(self.gridFrameAll)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.closeAllButton = QPushButton(self.gridFrameAll)
        self.closeAllButton.setObjectName(u"closeAllButton")

        self.gridLayout_3.addWidget(self.closeAllButton, 0, 1, 1, 1)

        self.resetAllButton = QPushButton(self.gridFrameAll)
        self.resetAllButton.setObjectName(u"resetAllButton")

        self.gridLayout_3.addWidget(self.resetAllButton, 1, 3, 1, 1)

        self.closeAllCB = QCheckBox(self.gridFrameAll)
        self.closeAllCB.setObjectName(u"closeAllCB")
        self.closeAllCB.setStyleSheet(u"QCheckBox {\n"
"	margin-left: 1px;\n"
"}")

        self.gridLayout_3.addWidget(self.closeAllCB, 2, 3, 1, 1)

        self.attachAllButton = QPushButton(self.gridFrameAll)
        self.attachAllButton.setObjectName(u"attachAllButton")

        self.gridLayout_3.addWidget(self.attachAllButton, 0, 2, 1, 1)

        self.detachAllButton = QPushButton(self.gridFrameAll)
        self.detachAllButton.setObjectName(u"detachAllButton")

        self.gridLayout_3.addWidget(self.detachAllButton, 0, 3, 1, 1)

        self.downloadAllButton = QPushButton(self.gridFrameAll)
        self.downloadAllButton.setObjectName(u"downloadAllButton")

        self.gridLayout_3.addWidget(self.downloadAllButton, 1, 2, 1, 1)

        self.runAllButton = QPushButton(self.gridFrameAll)
        self.runAllButton.setObjectName(u"runAllButton")

        self.gridLayout_3.addWidget(self.runAllButton, 1, 0, 1, 1)

        self.runSlavesCB = QCheckBox(self.gridFrameAll)
        self.runSlavesCB.setObjectName(u"runSlavesCB")
        self.runSlavesCB.setStyleSheet(u"QCheckBox {\n"
"	margin-left: 1px;\n"
"}")

        self.gridLayout_3.addWidget(self.runSlavesCB, 2, 0, 1, 2)

        self.launchAllButton = QPushButton(self.gridFrameAll)
        self.launchAllButton.setObjectName(u"launchAllButton")

        self.gridLayout_3.addWidget(self.launchAllButton, 0, 0, 1, 1)

        self.stopAllButton = QPushButton(self.gridFrameAll)
        self.stopAllButton.setObjectName(u"stopAllButton")

        self.gridLayout_3.addWidget(self.stopAllButton, 1, 1, 1, 1)


        self.gridLayout_5.addWidget(self.gridFrameAll, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.allGroupBox, 3, 0, 1, 1)

        self.instGroupBox = QGroupBox(self.centralwidget)
        self.instGroupBox.setObjectName(u"instGroupBox")
        self.instGroupBox.setMaximumSize(QSize(16777215, 400))
        self.instGroupBox.setStyleSheet(u"QGroupBox {\n"
"	border:1px solid gray;\n"
"	border-radius: 5px;\n"
"	margin-left: 0.5em;\n"
"	margin-right: 0.5em;\n"
"	margin-top: 1em;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 24px;\n"
"	top:6px;\n"
"	padding: 0 3px 0 3px;\n"
"}")
        self.horizontalLayout = QHBoxLayout(self.instGroupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.instancesTable = QTableWidget(self.instGroupBox)
        if (self.instancesTable.columnCount() < 3):
            self.instancesTable.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.instancesTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.instancesTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.instancesTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.instancesTable.setObjectName(u"instancesTable")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.instancesTable.sizePolicy().hasHeightForWidth())
        self.instancesTable.setSizePolicy(sizePolicy1)
        self.instancesTable.setFocusPolicy(Qt.StrongFocus)
        self.instancesTable.setStyleSheet(u"QHeaderView::section{\n"
"	Background-color:rgb(223,223,223);\n"
"	border: 1px solid grey;\n"
"	font-size: 11px;\n"
"} \n"
"QTableWidget {\n"
"	font-size: 11px;\n"
"	margin-left: 1.2em;\n"
"}")
        self.instancesTable.setFrameShape(QFrame.StyledPanel)
        self.instancesTable.setFrameShadow(QFrame.Sunken)
        self.instancesTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.instancesTable.setAutoScroll(False)
        self.instancesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.instancesTable.setAlternatingRowColors(True)
        self.instancesTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.instancesTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.instancesTable.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.instancesTable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.instancesTable.setRowCount(0)
        self.instancesTable.setColumnCount(3)
        self.instancesTable.horizontalHeader().setVisible(True)
        self.instancesTable.horizontalHeader().setHighlightSections(True)
        self.instancesTable.horizontalHeader().setProperty("showSortIndicator", False)
        self.instancesTable.horizontalHeader().setStretchLastSection(False)

        self.horizontalLayout.addWidget(self.instancesTable)

        self.gridFrameInst = QFrame(self.instGroupBox)
        self.gridFrameInst.setObjectName(u"gridFrameInst")
        self.gridFrameInst.setFrameShape(QFrame.NoFrame)
        self.gridFrameInst.setLineWidth(2)
        self.gridLayout_6 = QGridLayout(self.gridFrameInst)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.addButton = QPushButton(self.gridFrameInst)
        self.addButton.setObjectName(u"addButton")

        self.gridLayout_6.addWidget(self.addButton, 0, 0, 1, 1)

        self.removeButton = QPushButton(self.gridFrameInst)
        self.removeButton.setObjectName(u"removeButton")

        self.gridLayout_6.addWidget(self.removeButton, 1, 0, 1, 1)


        self.horizontalLayout.addWidget(self.gridFrameInst)


        self.gridLayout_2.addWidget(self.instGroupBox, 1, 0, 1, 1)

        self.selectedGroupBox = QGroupBox(self.centralwidget)
        self.selectedGroupBox.setObjectName(u"selectedGroupBox")
        self.selectedGroupBox.setMaximumSize(QSize(16777215, 150))
        self.selectedGroupBox.setStyleSheet(u"QGroupBox {\n"
"	border:1px solid gray;\n"
"	border-radius: 5px;\n"
"	margin-left: 0.5em;\n"
"	margin-right: 0.5em;\n"
"	margin-top: 1em;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 24px;\n"
"	top:6px;\n"
"	padding: 0 3px 0 3px;\n"
"}")
        self.selectedGroupBox.setFlat(False)
        self.selectedGroupBox.setCheckable(False)
        self.gridLayout_4 = QGridLayout(self.selectedGroupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridFrameSelected = QFrame(self.selectedGroupBox)
        self.gridFrameSelected.setObjectName(u"gridFrameSelected")
        self.gridFrameSelected.setStyleSheet(u"QFrame {\n"
"	padding-left: 0.5em;\n"
"	padding-right: 0.5em;\n"
"}")
        self.gridFrameSelected.setFrameShape(QFrame.NoFrame)
        self.gridFrameSelected.setFrameShadow(QFrame.Plain)
        self.gridFrameSelected.setLineWidth(2)
        self.gridLayout = QGridLayout(self.gridFrameSelected)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.gridLayout.setContentsMargins(9, 9, 9, 9)
        self.closeButton = QPushButton(self.gridFrameSelected)
        self.closeButton.setObjectName(u"closeButton")

        self.gridLayout.addWidget(self.closeButton, 1, 1, 1, 1)

        self.detachButton = QPushButton(self.gridFrameSelected)
        self.detachButton.setObjectName(u"detachButton")

        self.gridLayout.addWidget(self.detachButton, 1, 3, 1, 1)

        self.selectedInstanceComboBox = QComboBox(self.gridFrameSelected)
        self.selectedInstanceComboBox.setObjectName(u"selectedInstanceComboBox")

        self.gridLayout.addWidget(self.selectedInstanceComboBox, 0, 0, 1, 5)

        self.runButton = QPushButton(self.gridFrameSelected)
        self.runButton.setObjectName(u"runButton")

        self.gridLayout.addWidget(self.runButton, 2, 0, 1, 1)

        self.resetButton = QPushButton(self.gridFrameSelected)
        self.resetButton.setObjectName(u"resetButton")

        self.gridLayout.addWidget(self.resetButton, 2, 3, 1, 1)

        self.launchButton = QPushButton(self.gridFrameSelected)
        self.launchButton.setObjectName(u"launchButton")

        self.gridLayout.addWidget(self.launchButton, 1, 0, 1, 1)

        self.downloadButton = QPushButton(self.gridFrameSelected)
        self.downloadButton.setObjectName(u"downloadButton")

        self.gridLayout.addWidget(self.downloadButton, 2, 2, 1, 1)

        self.stopButton = QPushButton(self.gridFrameSelected)
        self.stopButton.setObjectName(u"stopButton")

        self.gridLayout.addWidget(self.stopButton, 2, 1, 1, 1)

        self.attachButton = QPushButton(self.gridFrameSelected)
        self.attachButton.setObjectName(u"attachButton")

        self.gridLayout.addWidget(self.attachButton, 1, 2, 1, 1)

        self.slaveRB = QRadioButton(self.gridFrameSelected)
        self.slaveRB.setObjectName(u"slaveRB")
        self.slaveRB.setStyleSheet(u"QCheckBox {\n"
"	margin-left: 1px;\n"
"}")

        self.gridLayout.addWidget(self.slaveRB, 1, 4, 1, 1)

        self.masterRB = QRadioButton(self.gridFrameSelected)
        self.masterRB.setObjectName(u"masterRB")
        self.masterRB.setStyleSheet(u"QCheckBox {\n"
"	margin-left: 1px;\n"
"}")

        self.gridLayout.addWidget(self.masterRB, 2, 4, 1, 1)


        self.gridLayout_4.addWidget(self.gridFrameSelected, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.selectedGroupBox, 2, 0, 1, 1)

        self.confGroupBox = QGroupBox(self.centralwidget)
        self.confGroupBox.setObjectName(u"confGroupBox")
        self.confGroupBox.setMaximumSize(QSize(16777215, 150))
        self.confGroupBox.setStyleSheet(u"QGroupBox {\n"
"	border:1px solid gray;\n"
"	border-radius: 5px;\n"
"	margin-left: 0.5em;\n"
"	margin-right: 0.5em;\n"
"	margin-top: 1em;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 24px;\n"
"	top:6px;\n"
"	padding: 0 3px 0 3px;\n"
"}")
        self.horizontalLayout_2 = QHBoxLayout(self.confGroupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridFrameConf = QFrame(self.confGroupBox)
        self.gridFrameConf.setObjectName(u"gridFrameConf")
        self.gridFrameConf.setStyleSheet(u"QFrame {\n"
"	padding-left: 0.5em;\n"
"	padding-right: 0.5em;\n"
"}")
        self.gridFrameConf.setFrameShape(QFrame.NoFrame)
        self.gridFrameConf.setFrameShadow(QFrame.Plain)
        self.gridFrameConf.setLineWidth(2)
        self.gridLayout_7 = QGridLayout(self.gridFrameConf)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setSizeConstraint(QLayout.SetNoConstraint)
        self.gridLayout_7.setContentsMargins(9, 9, 9, 9)
        self.configurationToolButton = QToolButton(self.gridFrameConf)
        self.configurationToolButton.setObjectName(u"configurationToolButton")
        self.configurationToolButton.setStyleSheet(u"QToolButton::menu-indicator { image: none; }")
        self.configurationToolButton.setPopupMode(QToolButton.InstantPopup)
        self.configurationToolButton.setAutoRaise(False)
        self.configurationToolButton.setArrowType(Qt.NoArrow)

        self.gridLayout_7.addWidget(self.configurationToolButton, 0, 1, 1, 1)

        self.alwaysOnTopCB = QCheckBox(self.gridFrameConf)
        self.alwaysOnTopCB.setObjectName(u"alwaysOnTopCB")

        self.gridLayout_7.addWidget(self.alwaysOnTopCB, 2, 0, 1, 1)

        self.configurationFilePath = QLineEdit(self.gridFrameConf)
        self.configurationFilePath.setObjectName(u"configurationFilePath")
        self.configurationFilePath.setReadOnly(False)
        self.configurationFilePath.setClearButtonEnabled(True)

        self.gridLayout_7.addWidget(self.configurationFilePath, 0, 0, 1, 1)


        self.horizontalLayout_2.addWidget(self.gridFrameConf)


        self.gridLayout_2.addWidget(self.confGroupBox, 0, 0, 1, 1)

        self.gridLayout_2.setRowStretch(0, 7)
        self.gridLayout_2.setRowStretch(1, 31)
        self.gridLayout_2.setRowStretch(2, 31)
        self.gridLayout_2.setRowStretch(3, 31)
        EmuSync.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(EmuSync)
        self.statusbar.setObjectName(u"statusbar")
        EmuSync.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(EmuSync)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 455, 22))
        self.menuOptions = QMenu(self.menuBar)
        self.menuOptions.setObjectName(u"menuOptions")
        self.menuOptions.setEnabled(True)
        self.menuOptions.setSeparatorsCollapsible(False)
        self.menuOptions.setToolTipsVisible(False)
        self.menuLogging = QMenu(self.menuBar)
        self.menuLogging.setObjectName(u"menuLogging")
        self.menuLoggingLevel = QMenu(self.menuLogging)
        self.menuLoggingLevel.setObjectName(u"menuLoggingLevel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.menuLoggingLevel.sizePolicy().hasHeightForWidth())
        self.menuLoggingLevel.setSizePolicy(sizePolicy2)
        EmuSync.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuOptions.menuAction())
        self.menuBar.addAction(self.menuLogging.menuAction())
        self.menuOptions.addAction(self.actionUseDemoMode)
        self.menuOptions.addAction(self.actionModuleData)
        self.menuLogging.addAction(self.actionOpenLogFolder)
        self.menuLogging.addAction(self.menuLoggingLevel.menuAction())
        self.menuLoggingLevel.addAction(self.actionLogging1)
        self.menuLoggingLevel.addAction(self.actionLogging2)
        self.menuLoggingLevel.addAction(self.actionLogging3)
        self.menuLoggingLevel.addAction(self.actionOff)

        self.retranslateUi(EmuSync)

        QMetaObject.connectSlotsByName(EmuSync)
    # setupUi

    def retranslateUi(self, EmuSync):
        self.useDemoModeAction.setText(QCoreApplication.translate("EmuSync", u"Use demo mode", None))
        self.actionUseDemoMode.setText(QCoreApplication.translate("EmuSync", u"Use demo mode", None))
        self.actionOpenLogFile.setText(QCoreApplication.translate("EmuSync", u"Open log directory", None))
        self.actionOpenLogFolder.setText(QCoreApplication.translate("EmuSync", u"Open log directory", None))
        self.actionLevel_1.setText(QCoreApplication.translate("EmuSync", u"Level 1", None))
        self.actionLevel_2.setText(QCoreApplication.translate("EmuSync", u"Level 2", None))
        self.actionLogging1.setText(QCoreApplication.translate("EmuSync", u"High", None))
        self.actionLogging2.setText(QCoreApplication.translate("EmuSync", u"Medium", None))
        self.actionLogging3.setText(QCoreApplication.translate("EmuSync", u"Low", None))
        self.actionModuleData.setText(QCoreApplication.translate("EmuSync", u"Module data", None))
        self.actionOff.setText(QCoreApplication.translate("EmuSync", u"Off", None))
        self.allGroupBox.setTitle(QCoreApplication.translate("EmuSync", u"All Instances", None))
        self.closeAllButton.setText(QCoreApplication.translate("EmuSync", u"Close all", None))
        self.resetAllButton.setText(QCoreApplication.translate("EmuSync", u"Reset all", None))
        self.closeAllCB.setText(QCoreApplication.translate("EmuSync", u"Close all on exit", None))
        self.attachAllButton.setText(QCoreApplication.translate("EmuSync", u"Attach all", None))
        self.detachAllButton.setText(QCoreApplication.translate("EmuSync", u"Detach all", None))
        self.downloadAllButton.setText(QCoreApplication.translate("EmuSync", u"Download all", None))
        self.runAllButton.setText(QCoreApplication.translate("EmuSync", u"Run all", None))
        self.runSlavesCB.setText(QCoreApplication.translate("EmuSync", u"Run slaves when master runs", None))
        self.launchAllButton.setText(QCoreApplication.translate("EmuSync", u"Launch all", None))
        self.stopAllButton.setText(QCoreApplication.translate("EmuSync", u"Stop all", None))
        self.instGroupBox.setTitle(QCoreApplication.translate("EmuSync", u"Instance workspaces", None))
        ___qtablewidgetitem = self.instancesTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("EmuSync", u"Mode", None));
        ___qtablewidgetitem1 = self.instancesTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("EmuSync", u"Status", None));
        ___qtablewidgetitem2 = self.instancesTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("EmuSync", u"Workspace", None));
        self.addButton.setText(QCoreApplication.translate("EmuSync", u"Add", None))
        self.removeButton.setText(QCoreApplication.translate("EmuSync", u"Remove", None))
        self.selectedGroupBox.setTitle(QCoreApplication.translate("EmuSync", u"Selected Instance", None))
        self.closeButton.setText(QCoreApplication.translate("EmuSync", u"Close", None))
        self.detachButton.setText(QCoreApplication.translate("EmuSync", u"Detach", None))
        self.runButton.setText(QCoreApplication.translate("EmuSync", u"Run", None))
        self.resetButton.setText(QCoreApplication.translate("EmuSync", u"Reset", None))
        self.launchButton.setText(QCoreApplication.translate("EmuSync", u"Launch", None))
        self.downloadButton.setText(QCoreApplication.translate("EmuSync", u"Download", None))
        self.stopButton.setText(QCoreApplication.translate("EmuSync", u"Stop", None))
        self.attachButton.setText(QCoreApplication.translate("EmuSync", u"Attach", None))
        self.slaveRB.setText(QCoreApplication.translate("EmuSync", u"Slave", None))
        self.masterRB.setText(QCoreApplication.translate("EmuSync", u"Master", None))
        self.confGroupBox.setTitle(QCoreApplication.translate("EmuSync", u"Configuration", None))
        self.configurationToolButton.setText(QCoreApplication.translate("EmuSync", u"...", None))
        self.alwaysOnTopCB.setText(QCoreApplication.translate("EmuSync", u"Always on top", None))
        self.configurationFilePath.setText("")
        self.configurationFilePath.setPlaceholderText(QCoreApplication.translate("EmuSync", u"Select configuration file (.yaml) here...", None))
        self.menuOptions.setTitle(QCoreApplication.translate("EmuSync", u"Options", None))
        self.menuLogging.setTitle(QCoreApplication.translate("EmuSync", u"Logging", None))
        self.menuLoggingLevel.setTitle(QCoreApplication.translate("EmuSync", u"Select logging level", None))
        pass
    # retranslateUi

