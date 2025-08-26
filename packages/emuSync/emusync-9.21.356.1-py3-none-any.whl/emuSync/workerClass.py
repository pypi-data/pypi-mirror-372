import multiprocessing as mp
import importlib
import os
import sys

from enum import Enum
import logging as log

from emuSync.workspaceController import WorkspaceController
from emuSync.workspaceController import CPUState, CPUCommand
from emuSync.configurationController import LogLevel

SET_LOGGING_LEVEL_CMD = "LOG_"


class HookEvent(Enum):
    onStop = "onStop"
    onDownload = "onDownload"
    onReset = "onReset"
    onRun = "onRun"
    preStop = "preStop"
    preDownload = "preDownload"
    preReset = "preReset"
    preRun = "preRun"


class WorkerClass(mp.Process):
    def __init__(self, workspaceName, commandQueue, resultQueue, isMasterOperationMode, moduleData=None, configurationPath=None):
        mp.Process.__init__(self)
        self.workspaceName = workspaceName
        self.commandQueue = commandQueue
        self.resultQueue = resultQueue
        self.lastState = CPUState.NOTATTACHED.value
        self.isMaster = isMasterOperationMode
        self.moduleData = moduleData
        self.configPath = configurationPath
        self.loggingLevel = 0

    def run(self):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Workspace: " + self.workspaceName)
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="isMaster: " + str(self.isMaster))

        self.workspaceCtrl = WorkspaceController(os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(self.configPath)), self.workspaceName)))
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Entering loop and waiting for commands.")

        while True:
            if not self.commandQueue.empty():
                nextAction = self.commandQueue.get()

                if nextAction in self.workspaceCtrl.commandWSDict:
                    # Module "Pre(before)" events hooks check and execute
                    if nextAction == CPUCommand.DOWNLOAD.value and self.isHookActive(eventType=HookEvent.preDownload):
                        self.executeHook(hookEvent=HookEvent.preDownload)
                    elif nextAction == CPUCommand.RUN.value and self.isHookActive(eventType=HookEvent.preRun):
                        self.executeHook(hookEvent=HookEvent.preRun)
                    elif nextAction == CPUCommand.RESET.value and self.isHookActive(eventType=HookEvent.preReset):
                        self.executeHook(hookEvent=HookEvent.preReset)
                    elif nextAction == CPUCommand.STOP.value and self.isHookActive(eventType=HookEvent.preStop):
                        self.executeHook(hookEvent=HookEvent.preStop)

                    # Execute command
                    self.workspaceCtrl.commandWSDict[nextAction](self.workspaceCtrl)

                    # Module "After" events hooks check and execute
                    if nextAction == CPUCommand.DOWNLOAD.value and self.isHookActive(eventType=HookEvent.onDownload):
                        self.executeHook(hookEvent=HookEvent.onDownload)
                    elif nextAction == CPUCommand.RESET.value and self.isHookActive(eventType=HookEvent.onReset):
                        self.executeHook(hookEvent=HookEvent.onReset)
                    elif nextAction == CPUCommand.STOP.value and self.isHookActive(eventType=HookEvent.onStop):
                        self.executeHook(hookEvent=HookEvent.onStop)
                    elif nextAction == CPUCommand.RUN.value and self.isHookActive(eventType=HookEvent.onRun):
                        self.executeHook(hookEvent=HookEvent.onRun)

                elif nextAction.startswith(SET_LOGGING_LEVEL_CMD):
                    newLogLevel = int(nextAction[-1])
                    if (self.loggingLevel == LogLevel.OFF.value) and (newLogLevel > LogLevel.OFF.value):
                        self.createLogFile()
                    self.loggingLevel = newLogLevel
                    self.workspaceCtrl.loggingLevel = self.loggingLevel

                else:
                    responseUnknownCommand = "Unknown command: " + nextAction
                    self.resultQueue.put(responseUnknownCommand)
                    self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Unknown command: " + str(nextAction))

            if self.workspaceCtrl.isConnectionMgrConnected():
                currentState = self.workspaceCtrl.getCurrentStatusString()
                if self.lastState is not currentState:
                    self.lastState = currentState
                    self.resultQueue.put(self.lastState)
                    self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="New current status: " + str(self.lastState))
            else:
                currentState = CPUState.NOTATTACHED.value
                if self.lastState is not currentState:
                    self.lastState = currentState
                    self.resultQueue.put(self.lastState)
                    self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="New current status: " + str(self.lastState))

    def logExtraInfo(self, logLevel, logMessage):
        logger = log.getLogger("WorkerClass")
        if self.loggingLevel > LogLevel.OFF.value:
            if logLevel == LogLevel.HIGH:
                if self.loggingLevel == LogLevel.HIGH.value:
                    logger.info(logMessage)
                    logger.info("last state: " + (self.lastState))
                elif self.loggingLevel == LogLevel.MEDIUM.value:
                    logger.info(logMessage)
            elif logLevel == LogLevel.MEDIUM:
                logger.warning(logMessage)
            elif logLevel == LogLevel.LOW:
                logger.error(logMessage)

    def createLogFile(self):
        procName = mp.current_process().name
        logDirectory = os.path.expanduser('~') + "\\emuSyncLog\\"
        if not os.path.isdir(logDirectory):
            os.makedirs(logDirectory)
        logFilePath = os.path.join(logDirectory, procName + ".log")
        log.basicConfig(filename=logFilePath, filemode='w', level=log.INFO)
        log.getLogger("WorkerClass").info(procName + " logging file created.")

    def getHookPath(self, eventType) -> str:
        if self.moduleData != None:
            try:
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Returning hook path for event " + eventType.value + ".")
                return self.moduleData[eventType.value]['hookPath']
            except KeyError as exception:
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Cannot find hookPath key for " + str(eventType.value) + ". " + str(exception))
            except TypeError as exception:
                self.logExtraInfo(logLevel=LogLevel.LOW,
                                  logMessage="Wrong hookPath field data type for " + str(eventType.value) + ". " + str(exception))
        self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Hook path for " + str(eventType.value) + " not found.")

    def getHookStart(self, eventType) -> str:
        if self.moduleData != None:
            try:
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Returning hook start method for event " + eventType.value + ".")
                return self.moduleData[eventType.value]['hookStart']
            except KeyError as exception:
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Cannot find hookStart key for " + str(eventType.value) + ". " + str(exception))
            except TypeError as exception:
                self.logExtraInfo(logLevel=LogLevel.LOW,
                                  logMessage="Wrong hookStart field data type for " + str(eventType.value) + ". " + str(exception))
        self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Hook start method for " + str(eventType.value) + " not found.")

    def isHookActive(self, eventType) -> bool:
        if self.moduleData != None:
            try:
                if self.moduleData[eventType.value]['isActive'] == True:
                    return True
            except KeyError as exception:
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Cannot find isActive key for " + str(eventType.value) + ". " + str(exception))
                return False
            except TypeError as exception:
                self.logExtraInfo(logLevel=LogLevel.LOW,
                                  logMessage="Wrong isActive field data type for " + str(eventType.value) + ". " + str(exception))
                return False
        return False

    def executeHook(self, hookEvent):
        # Get path and start method name for selected event type.
        hookPath = self.getHookPath(hookEvent)
        hookStartMethod = self.getHookStart(hookEvent)
        hookAbsPath = os.path.abspath(os.path.join(os.path.dirname(self.configPath), hookPath))

        if hookAbsPath != None and hookStartMethod != None:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Hook path: " + hookAbsPath)
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Hook start method: " + hookStartMethod)
            # Add file path to path
            sys.path.append(hookAbsPath)
            # Extract raw file name from path (no type extension)
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Importing module: " + hookAbsPath)

            try:
                spec = importlib.util.spec_from_file_location(hookStartMethod, hookAbsPath)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)

                # Change working directory to allow relative paths in hooks
                curWd = os.getcwd()
                os.chdir(os.path.dirname(hookAbsPath))

                # Start hook method
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Entering user hook.")
                getattr(module, hookStartMethod)(self.workspaceCtrl.connectionMgr)

                # Change working directory back
                os.chdir(curWd)

            except AttributeError as exMsg0:
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage=str(exMsg0))
            except ImportError as exMsg1:
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage=str(exMsg1))
            except Exception as exMsg2:
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Unexpected exception occured: " + str(exMsg2))

            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="User hook exited.")
