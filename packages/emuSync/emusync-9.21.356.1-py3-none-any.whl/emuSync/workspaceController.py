from enum import Enum
import isystem.connect as ic
import logging as log
from emuSync.configurationController import LogLevel


class CPUState(Enum):
    OFFLINE = "OFFLINE"
    STOPPED = "STOP"
    RUNNING = "RUN"
    RESET = "RESET"
    HALTED = "HALTED"
    WAITING = "WAITING"
    ATTACHED = "ATTACHED"
    IDLE = "IDLE"
    UNKNOWN = "SoC DETACHED"
    NOTATTACHED = "Not attached"


class CPUCommand(Enum):
    LAUNCH = "launch"
    DOWNLOAD = "download"
    RUN = "run"
    RUN_SLAVE = "runSlave"
    STOP = "stop"
    STOP_SLAVE = "stopSlave"
    RESET = "reset"
    ATTACH = "attach"
    DETACH = "detach"
    CLOSE = "close"
    ENABLE_DEMO = "enableDemo"
    DISABLE_DEMO = "disableDemo"


class WorkspaceController:
    def __init__(self, workspaceName):
        self.connectionMgr = ic.ConnectionMgr()
        self.executionMgr = ic.CExecutionController(self.connectionMgr)
        self.loaderMgr = ic.CLoaderController(self.connectionMgr)
        self.ideMgr = ic.CIDEController(self.connectionMgr)
        self.workspaceName = workspaceName
        self.isDemoEnabled = False
        self.loggingLevel = 0

    def logExtraInfo(self, logLevel, logMessage):
        logger = log.getLogger("WorkspaceController")
        if self.loggingLevel:
            if logLevel == LogLevel.HIGH:
                if self.loggingLevel == LogLevel.MEDIUM.value:
                    logger.info(logMessage)
                elif self.loggingLevel == LogLevel.HIGH.value:
                    logger.info(logMessage)
                    logger.info("Workspace: " + self.workspaceName)
                    logger.info("Current state: " + self.getCurrentStatusString())
            elif logLevel == LogLevel.MEDIUM:
                logger.warning(logMessage)
            elif logLevel == LogLevel.LOW:
                logger.error(logMessage)

    def download(self):
        if not self.connectionMgr.isAttached():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Download: Not attached to winIDEA instance.")
            return
        if not self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Download: Not connected to winIDEA instance.")
            return

        try:
            self.loaderMgr.download()
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Download successful.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during download call: " + str(exMsg))
            return

    def isConnectionMgrConnected(self) -> bool:
        return bool(self.connectionMgr.isConnected())

    def run(self):
        if not self.connectionMgr.isAttached():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Run: Not attached to winIDEA instance.")
            return
        if not self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Run: Not connected to winIDEA instance.")
            return

        try:
            self.executionMgr.run()
            cpuStatus = self.executionMgr.getCPUStatus(wantStopReason=False)
            if cpuStatus.isRunning():
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="CPU run successful.")
                return
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="CPU run successful, but not in Running state.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during run call: " + str(exMsg))
            return

    def stop(self):
        if not self.connectionMgr.isAttached():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Stop: Not attached to winIDEA instance.")
            return
        if not self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Stop: Not connected to winIDEA instance.")
            return

        try:
            self.executionMgr.stop()
            cpuStatus = self.executionMgr.getCPUStatus(wantStopReason=False)
            if cpuStatus.isStopped():
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="CPU stopped successfully.")
                return
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="CPU stopped successfully, but not in Stopped state.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during stop call: " + str(exMsg))
            return

    def reset(self):
        if not self.connectionMgr.isAttached():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Reset: Not attached to winIDEA instance.")
            return
        if not self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Reset: Not connected to winIDEA instance.")
            return

        try:
            self.executionMgr.reset()
            cpuStatus = self.executionMgr.getCPUStatus(wantStopReason=False)
            if cpuStatus.isReset():
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="CPU reset successfully.")
                return
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="CPU reset successfully, but not in Reset state.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during reset call: " + str(exMsg))
            return

    def detach(self):
        if not self.connectionMgr.isAttached():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Detach: Not attached to winIDEA instance.")
            return

        try:
            self.connectionMgr.disconnect()
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Detach finished.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during detach call: " + str(exMsg))
            return

    def attach(self):
        if not self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Attach: Not connected to winIDEA instance.")
        try:
            connConfig = ic.CConnectionConfig()
            connConfig.workspace(self.workspaceName)
            self.connectionMgr.connect(connConfig)
            if self.isDemoEnabled:
                self.enableDemoMode()
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Attach successful.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during attach call: " + str(exMsg))
            return

    def close(self):
        try:
            self.connectionMgr.disconnect(ic.IConnect.dfCloseServerUnconditional, ic.IConnect.dfCloseAutoSaveNone)
            if self.connectionMgr.isConnected():
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Close: winIDEA connection not terminated.")
                return
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Close: winIDEA disconnected.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during close: " + str(exMsg))
            return

    def launch(self):
        if self.connectionMgr.isAttached():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Launch: Already attached to winIDEA instance.")
            return
        if not self.workspaceName:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Launch: No workspace specified.")
            return
        if self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Launch: Already connected to winIDEA instance.")
            return

        try:
            # self.connectionMgr.connectMRUEx(workspacePath=self.workspaceName, isAnyWinIDEAId=False,
            #                                winIDEAId="", hostIpAddress="", isUseServerEnvVars=False)
            connConfig = ic.CConnectionConfig()
            connConfig.workspace(self.workspaceName)
            self.connectionMgr.connect(connConfig)
            if self.connectionMgr.isConnected():
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Launched and connected to winIDEA instance successfully.")

                if self.isDemoEnabled:
                    self.enableDemoMode()
                return
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Launch: Could not launch winIDEA instance.")
            return
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during launch: " + str(exMsg))
            return

    def enableDemoMode(self):
        self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Enabling demo mode.")
        self.isDemoEnabled = True
        if not self.workspaceName:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Enable demo mode: No workspace specified.")
            return
        if not self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Enable demo mode: Not connected to winIDEA instance.")
            return
        try:
            self.ideMgr.serviceCall("/IDE/Demo", "Demo: TRUE")
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Demo mode enabled.")
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during demo mode toggle: " + str(exMsg))
            return

    def disableDemoMode(self):
        self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Disabling demo mode.")
        self.isDemoEnabled = False
        if not self.workspaceName:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Disable demo mode: No workspace specified.")
            return
        if not self.connectionMgr.isConnected():
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Disable demo mode: Not connected to winIDEA instance.")
            return
        try:
            self.ideMgr.serviceCall("/IDE/Demo", "Demo: FALSE")
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Demo mode disabled.")
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during demo mode toggle: " + str(exMsg))
            return

    def getCurrentStatusString(self) -> str:
        try:
            if self.connectionMgr.isAttached():
                cpuStatus = self.executionMgr.getCPUStatus(wantStopReason=False)
                if cpuStatus.isMustInit():
                    return CPUState.OFFLINE.value
                elif cpuStatus.isReset():
                    return CPUState.RESET.value
                elif cpuStatus.isStopped():
                    return CPUState.STOPPED.value
                elif cpuStatus.isRunning():
                    return CPUState.RUNNING.value
                elif cpuStatus.isHalted():
                    return CPUState.HALTED.value
                elif cpuStatus.isWaiting():
                    return CPUState.WAITING.value
                elif cpuStatus.isIdle():
                    return CPUState.IDLE.value
            return CPUState.UNKNOWN.value
        except Exception as exMsg:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Exception during getCPUStatus: " + str(exMsg))
            return CPUState.OFFLINE.value

    def isDebugConnected(self) -> bool:
        return self.connectionMgr.isAttached()

    commandWSDict = {
        "launch": launch,
        "download": download,
        "run": run,
        "runSlave": run,
        "stop": stop,
        "stopSlave": stop,
        "detach": detach,
        "attach": attach,
        "reset": reset,
        "close": close,
        "enableDemo": enableDemoMode,
        "disableDemo": disableDemoMode
    }
