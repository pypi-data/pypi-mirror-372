import yaml
import logging as log
from enum import Enum


class ConfigurationController():
    def __init__(self):
        self.fileName = None
        self.data = None
        self.loggingLevel = 0

    # Log level 0 is 'OFF', the rest are different 'ON' levels
    def setLoggingLevel(self, logLevel):
        if ((logLevel.value >= LogLevel.OFF.value) and (logLevel.value <= LogLevel.UNKNOWN.value)):
            self.loggingLevel = logLevel

    def logExtraInfo(self, logLevel, logMessage):
        logger = log.getLogger("ConfigurationController")
        if self.loggingLevel:
            if logLevel == LogLevel.HIGH:
                if self.loggingLevel == LogLevel.HIGH:
                    logger.info(logMessage)
                    logger.info("data: " + str(self.data))
                elif self.loggingLevel == LogLevel.MEDIUM:
                    logger.info(logMessage)
            elif logLevel == LogLevel.MEDIUM:
                logger.warning(logMessage)
            elif logLevel == LogLevel.LOW:
                logger.error(logMessage)

    def loadConfiguration(self, filePath):
        self.fileName = filePath
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Loading configuration.")
        try:
            with open(self.fileName, 'r') as stream:
                try:
                    self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Loading yaml data from stream.")
                    self.data = yaml.safe_load(stream)
                    self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Data loaded.")
                except yaml.YAMLError as exception:
                    self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Failed to load configuration: " + str(exception))
        except FileNotFoundError as fileException:
            self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Please check configuration file path. File not found: " + str(fileException))
        self.removeEmptyWsPaths()

    def removeEmptyWsPaths(self):
        nrConf = self.getNrOfConfigurationsFromYaml()
        position = 0
        while position in range(nrConf):
            if ((self.data['configuration'][position]['wsPath'] == None) or (self.data['configuration'][position]['wsPath'] == "")):
                self.removeConfiguration(position=position)
                nrConf -= 1
            else:
                position += 1

    def getData(self) -> list:
        return self.data

    def getModuleData(self) -> list:
        try:
            if ((self.data != None) and (self.data['module'] != None)):
                return self.data['module']
            else:
                self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="No module data found.")
                return None
        except KeyError as exception:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Cannot find module field in loaded data. " + str(exception))
            return None

    def saveConfiguration(self, configurationFile=None):
        if configurationFile is None:
            configurationFile = self.fileName
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Saving configuration.")
        with open(configurationFile, 'w') as file:
            try:
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Saving configuration to data.")
                yaml.safe_dump(self.data, file, default_flow_style=False)
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Data saved to " + configurationFile + ".")
            except yaml.YAMLError as exception:
                self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Failed to save configuration: " + exception)

    def editMode(self, newMode, position):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage=self.data['configuration'][position]['wsPath'] + " set to " + newMode)
        self.data['configuration'][position]['opMode'] = newMode

    def addConfiguration(self, mode, workspacePath):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Adding " + workspacePath + ", " + mode + " to data.")
        newDataItem = {
            'opMode': mode,
            'wsPath': workspacePath
        }
        # If configurations YAML only has the main 'configurations' field, then its contents are not (yet) a list, but None
        if self.data['configuration'] == None:
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Creating a list for data.")
            self.data['configuration'] = []
        self.data['configuration'].append(newDataItem)
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Configuration added.")

    def createNewConfiguration(self):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Creating new empty configuration data list.")
        newConfiguration = {
            'configuration': [],
            'module':
                {
                    'preStop': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'preStopHook',
                        'isActive': False
                    },
                    'onStop': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'onStopHook',
                        'isActive': False
                    },
                    'preDownload': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'preDownloadHook',
                        'isActive': False
                    },
                    'onDownload': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'onDownloadHook',
                        'isActive': False
                    },
                    'preReset': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'preResetHook',
                        'isActive': False
                    },
                    'onReset': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'onResetHook',
                        'isActive': False
                    },
                    'preRun': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'preRunHook',
                        'isActive': False
                    },
                    'onRun': {
                        'hookPath': 'emuSyncHooks.py',
                        'hookStart': 'onRunHook',
                        'isActive': False
                    }
            },
            'logging':
                {
                    'enable': False
            }
        }
        self.data = newConfiguration

    def removeConfiguration(self, position):
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Removing from configuration data.")
        self.data['configuration'].pop(position)

    def getNrOfConfigurationsFromYaml(self) -> int:
        try:
            if self.data['configuration'] != None:
                nrOfConfigurations = len(self.data['configuration'])
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage=str(nrOfConfigurations) + " configurations found.")
                return nrOfConfigurations
            else:
                self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="No configuration data found.")
                return -1
        except KeyError as exception:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Cannot find configuration field in loaded data." + str(exception))
            return -1

    def isModuleDataLoaded(self) -> bool:
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Checking for module data.")
        try:
            if ((self.data != None) and (len(self.data['module']))):
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Module data found.")
                return True
            return False
        except KeyError as exception:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Cannot find module field in loaded data." + str(exception))
            return False

    def isLoggingEnabled(self) -> bool:
        try:
            if ((self.data != None) and (len(self.data['logging']) == 1) and (self.data['logging']['enable'] == True)):
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Logging enabled")
                return True
            return False
        except KeyError as exception:
            self.logExtraInfo(logLevel=LogLevel.MEDIUM, logMessage="Cannot find logging field in loaded data." + str(exception))
            return False

    def isDataLoadedAndChanged(self) -> bool:
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Checking configuration data for changes.")
        if ((self.data != None) and (len(self.data['configuration']))):
            self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Data found.")
            if self.fileName != None:
                self.logExtraInfo(
                    logLevel=LogLevel.HIGH, logMessage="Comparing current configuration data to fresh load of " + self.fileName +
                    " configuration file.")
                tempData = None
                with open(self.fileName, 'r') as stream:
                    try:
                        tempData = yaml.safe_load(stream)
                        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Fresh load of configuration data successful.")
                    except yaml.YAMLError as exception:
                        self.logExtraInfo(logLevel=LogLevel.LOW, logMessage="Failed to load configuration data: " + str(exception))
                        tempData = None
                # If data is unchanged from fresh reload data, return False
                if tempData == self.data:
                    self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="No changes to configuration data found.")
                    return False
                # If data IS changed, return True
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Differences in configuration data found.")
                return True
            else:
                # If data has been changed, but filePath has not been selected.
                self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="Configuration data has been found, but file path not selected.")
                return True
        # If data is still None (as originally declared), return False
        self.logExtraInfo(logLevel=LogLevel.HIGH, logMessage="No configuration data found.")
        return False

    def isDataLoaded(self) -> bool:
        if self.data == None:
            return False
        return True


class LogLevel(Enum):
    UNKNOWN = 4
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    OFF = 0
