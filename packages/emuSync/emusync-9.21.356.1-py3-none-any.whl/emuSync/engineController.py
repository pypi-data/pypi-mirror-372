import multiprocessing as mp
import time
import logging as log

from emuSync.configurationController import ConfigurationController, LogLevel
from emuSync.workerClass import WorkerClass
from emuSync.workspaceController import CPUCommand, CPUState


class EngineController():
    def __init__(self):
        self.processList = list()
        self.confCtrl = ConfigurationController()
        self.isRunSlaves = False
        self.isDemoMode = False
        self.loggingLevel = 0

    # Log level 0 is 'OFF', the rest are different 'ON' levels
    def setLoggingLevel(self, logLevel):
        if logLevel.value >= LogLevel.OFF.value and logLevel.value <= LogLevel.UNKNOWN.value:
            self.loggingLevel = logLevel.value
            self.confCtrl.setLoggingLevel(logLevel=logLevel)
            self.setWorkerLoggingLevel(newLogLevel=logLevel.value)

    def setWorkerLoggingLevel(self, newLogLevel):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending log level change command to " + str(self.getNumberOfProcesses()) + " workers.")
        for process in self.processList:
            process.commandQueue.put("LOG_" + str(newLogLevel))

    def logExtraInfo(self, logLevel, logMessage):
        logger = log.getLogger("EngineController")
        if self.loggingLevel:
            if logLevel == LogLevel.HIGH:
                if self.loggingLevel == 2:
                    logger.info(logMessage)
                elif self.loggingLevel == 1:
                    logger.info(logMessage)
                    logger.info("Process List: " + str(self.processList))
            elif logLevel == LogLevel.MEDIUM:
                logger.warning(logMessage)
            elif logLevel == LogLevel.LOW:
                logger.error(logMessage)

    def toggleRunSlaves(self):
        if self.isRunSlaves is True:
            self.isRunSlaves = False
        else:
            self.isRunSlaves = True

    def _toggleWSDemoModeOne(self, listIndex):
        if self.isDemoMode:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending demo mode enable command to workspace: " +
                              str(self.processList[listIndex].workspaceName))
            self.processList[listIndex].commandQueue.put(CPUCommand.ENABLE_DEMO.value)
        else:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending demo mode disable command to workspace: " +
                              str(self.processList[listIndex].workspaceName))
            self.processList[listIndex].commandQueue.put(CPUCommand.DISABLE_DEMO.value)

    def _toggleWSDemoMode(self):
        if self.isDemoMode:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending demo mode enable commands to " + str(self.getNumberOfProcesses()) + " workspaces.")
            for process in self.processList:
                process.commandQueue.put(CPUCommand.ENABLE_DEMO.value)
        else:
            self.logExtraInfo(logLevel=LogLevel.HIGH,
                              logMessage="Sending demo mode disable commands to " + str(self.getNumberOfProcesses()) + " workspaces.")
            for process in self.processList:
                process.commandQueue.put(CPUCommand.DISABLE_DEMO.value)

    def toggleDemoMode(self, isDemoEnabled):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Demo mode isEnabled: " + str(isDemoEnabled))
        self.isDemoMode = isDemoEnabled
        self._toggleWSDemoMode()

    def commandAll(self, command):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending " + command.value + " command to " + str(self.getNumberOfProcesses()) + " workspaces.")
        for process in self.processList:
            process.commandQueue.put(command.value)

    def commandOne(self, command, listIndex):
        try:
            self.logExtraInfo(
                logLevel=LogLevel.HIGH, logMessage="Sending " + command.value + " command to workspace: " + self.processList[listIndex].workspaceName)
            self.processList[listIndex].commandQueue.put(command.value)
            if command.value == CPUCommand.LAUNCH.value:
                self._toggleWSDemoModeOne(listIndex=listIndex)
        except IndexError as exception:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Index out of bounds: " + str(exception))

    def _runAllSlaves(self):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending Run command to all slaves.")
        for process in self.processList:
            if not process.isMaster:
                process.commandQueue.put(CPUCommand.RUN_SLAVE.value)

    def _stopAllSlaves(self):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending Stop command to all slaves.")
        for process in self.processList:
            if not process.isMaster:
                process.commandQueue.put(CPUCommand.STOP_SLAVE.value)

    def _addProcess(self, workspacePath, opMode):
        commandQueue = mp.Queue()
        resultQueue = mp.Queue()

        if opMode == "master":
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Creating " + str(workspacePath) + " (master) process.")
            self.processList.append(WorkerClass(workspaceName=workspacePath, commandQueue=commandQueue, resultQueue=resultQueue,
                                                isMasterOperationMode=True, moduleData=self.confCtrl.getModuleData(), configurationPath=self.confCtrl.fileName))
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Starting new process.")
            self.processList[-1].start()
            time.sleep(0.05)
        else:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Creating " + str(workspacePath) + " (slave) process.")
            self.processList.append(WorkerClass(workspaceName=workspacePath, commandQueue=commandQueue, resultQueue=resultQueue,
                                                isMasterOperationMode=False, moduleData=self.confCtrl.getModuleData(), configurationPath=self.confCtrl.fileName))
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Starting new process.")
            self.processList[-1].start()
            time.sleep(0.05)

        self.setWorkerLoggingLevel(newLogLevel=self.loggingLevel)
        self.toggleDemoMode(isDemoEnabled=self.isDemoMode)

    def addFileConfigurations(self, filePath) -> bool:
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Adding configurations file workspaces.")
        self.confCtrl.loadConfiguration(filePath=filePath)
        data = self.confCtrl.getData()
        numOfWs = self.confCtrl.getNrOfConfigurationsFromYaml()

        if numOfWs >= 0:
            for i in range(numOfWs):
                workspacePath = data['configuration'][i]['wsPath']
                workspaceMode = data['configuration'][i]['opMode']
                self._addProcess(workspacePath=workspacePath, opMode=workspaceMode)
            return True
        self.confCtrl = ConfigurationController()
        return False

    def addWorkspace(self, wsPath):
        if self.confCtrl.getData() == None:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="No previous configuration data found.")
            self.confCtrl.createNewConfiguration()
        self.confCtrl.addConfiguration(mode="slave", workspacePath=wsPath)
        self._addProcess(workspacePath=wsPath, opMode="slave")

    def removeWorkspace(self, index):
        self.confCtrl.removeConfiguration(position=index)
        self._removeItem(listIndex=index, isCloseChecked=True)

    def getWorkspacesList(self) -> list:
        numOfProcesses = self.getNumberOfProcesses()
        workspacesList = list()

        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Creating list of workspace names.")
        if numOfProcesses:
            for i in range(numOfProcesses):
                workspacesList.append(self.processList[i].workspaceName)
        return workspacesList

    def setMaster(self, listIndex):
        if self._masterExists:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Setting old master to slave.")
            self._setOldMasterToSlave()
        try:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Setting " + self.processList[listIndex].workspaceName + " to master.")
            self.processList[listIndex].isMaster = True
            self.confCtrl.editMode(newMode="master", position=listIndex)
        except IndexError as exception:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Index out of bounds: " + str(exception))

    def isMasterProcess(self, listIndex) -> bool:
        if self.processList[listIndex].isMaster is True:
            return True
        return False

    def setSlave(self, listIndex):
        try:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Setting " + self.processList[listIndex].workspaceName + " to slave.")
            self.processList[listIndex].isMaster = False
            self.confCtrl.editMode(newMode="slave", position=listIndex)
        except IndexError as exception:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Index out of bounds: " + str(exception))

    def _masterExists(self) -> bool:
        for process in self.processList:
            if process.isMaster:
                self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Existing master workspace found.")
                return True
        return False

    def _setOldMasterToSlave(self):
        for i in range(self.getNumberOfProcesses()):
            if self.processList[i].isMaster:
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Setting " + self.processList[i].workspaceName + " to slave.")
                self.processList[i].isMaster = False
                self.confCtrl.editMode(newMode="slave", position=i)

    def isInstanceConnected(self, listIndex) -> bool:
        if self.processList[listIndex].lastState == CPUState.NOTATTACHED.value:
            return False
        return True

    def isInstanceListConnected(self) -> bool:
        for process in self.processList:
            if process.lastState == CPUState.NOTATTACHED.value:
                return False
        return True

    def getNumberOfProcesses(self):
        return len(self.processList)

    def printItemizedWorkspaceList(self):
        numOfProcesses = self.getNumberOfProcesses()
        if numOfProcesses:
            for i in range(numOfProcesses):
                print(" ", i, ". ", self.processList[i].workspaceName, sep='')
        else:
            print("No active workspace processes found.")

    def _removeItem(self, listIndex, isCloseChecked):
        wsName = self.processList[listIndex].workspaceName
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Removing " + wsName + ".")
        if isCloseChecked:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Sending close command to " + wsName + "process.")
            self.processList[listIndex].commandQueue.put(CPUCommand.CLOSE.value)

        time.sleep(0.1)

        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Terminating " + wsName + " process.")
        self.processList[listIndex].terminate()
        self.processList[listIndex].join()
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Removing " + wsName + " from process list.")
        self.processList.pop(listIndex)

    def terminateAll(self, isCloseChecked):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Terminating all processes.")
        # Sleep for 0.1s so workerClass thread has the time to close winIDEA before the thread itself gets terminated.
        time.sleep(0.1)
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Removing workspaces from process list.")
        for i in range(len(self.processList) - 1, -1, -1):
            self._removeItem(listIndex=i, isCloseChecked=isCloseChecked)
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="All processes terminated.")

    def checkAndPrintStatusUpdates(self):
        for process in self.processList:
            if not process.resultQueue.empty():
                newStatus = process.resultQueue.get()
                if process.isMaster:
                    if newStatus == CPUState.STOPPED.value:
                        self._stopAllSlaves()
                    elif newStatus == CPUState.RUNNING.value:
                        self._runAllSlaves()
                currentWorkspace = process.workspaceName
                process.lastState = newStatus
                print(currentWorkspace, " now in ", newStatus, " state.", sep="")

    def checkForStatusUpdates(self):
        for process in self.processList:
            if not process.resultQueue.empty():
                newStatus = process.resultQueue.get()
                if process.isMaster:
                    if newStatus == CPUState.STOPPED.value:
                        self._stopAllSlaves()
                    elif newStatus == CPUState.RUNNING.value and self.isRunSlaves == True:
                        self._runAllSlaves()
                process.lastState = newStatus

    def getWorkspaceStatus(self, processIndex) -> str:
        return self.processList[processIndex].lastState

    def getInstanceDataList(self) -> list:
        numOfProcesses = self.getNumberOfProcesses()
        processDataList = list()

        if numOfProcesses:
            for i in range(numOfProcesses):
                processDataList.append([])
                if self.processList[i].isMaster:
                    processDataList[i].append("Master")
                else:
                    processDataList[i].append("Slave")
                processDataList[i].append(self.processList[i].lastState)
                processDataList[i].append(self.processList[i].workspaceName)

        return processDataList

    def printStatus(self):
        for process in self.processList:
            if process.isMaster:
                print("MASTER: ", process.workspaceName, " status: ", process.lastState, sep="")
            else:
                print(process.workspaceName, " status: ", process.lastState, sep="")

    def resetConfigurationCtrl(self):
        self.confCtrl = ConfigurationController()

    def isConfigurationFilePathSet(self) -> bool:
        if self.confCtrl.fileName:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Configuration file path is set to " + self.confCtrl.fileName)
            return True
        else:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="No configuration file path found.")
            return False

    def setConfigurationFilePath(self, filePath):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Setting configuration file path to " + filePath)
        self.confCtrl.fileName = filePath

    commandDict = {
        "launch": CPUCommand.LAUNCH,
        "download": CPUCommand.DOWNLOAD,
        "run": CPUCommand.RUN,
        "stop": CPUCommand.STOP,
        "detach": CPUCommand.DETACH,
        "attach": CPUCommand.ATTACH,
        "reset": CPUCommand.RESET,
        "close": CPUCommand.CLOSE
    }
