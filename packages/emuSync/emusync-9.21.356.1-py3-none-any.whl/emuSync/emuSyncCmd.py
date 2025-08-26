import time
import multiprocessing as mp
from pathlib import Path

from enum import Enum

import logging as log

from emuSync.engineController import EngineController
from emuSync.workspaceController import CPUCommand


class MainMenuInputValue(Enum):
    LOAD_WORKSPACE = "1"
    ADD_WORKSPACE = "2"
    REMOVE_WORKSPACE = "3"
    COMMAND_ALL = "4"
    COMMAND_ONE = "5"
    SET_AS_MASTER = "6"
    PRINT_STATUS = "7"
    QUIT = "quit"
    EXIT = "exit"
    BACK = "back"


class StaticCommandText(Enum):
    LOAD_WORKSPACE_PREFIX = "LOAD"
    ADD_WORKSPACE_PREFIX = "ADD1"
    REMOVE_WORKSPACE_PREFIX = "REM1"
    COMMAND_ALL_PREFIX = "COMM"
    COMMAND_ONE_PREFIX = "COM1"
    SET_AS_MASTER_PREFIX = "MAST"
    PRINT_STATUS = "PRINT_STATUS"
    PRINT_LIST = "PRINT_LIST"
    INVALID_COMMAND = "INVALID COMMAND"


MAIN_MENU_PROMPT_STRING = "\nSelect next action:\n 1. Load configuration file\n 2. Add workspace\n 3. Remove workspace\n 4. Command (all workspaces)\n 5. Command (specific workspace)\n 6. Set as master\n 7. Print CPU status\n"
INVALID_VALUE_STRING = "Error. Invalid value."
INVALID_CONFIGURATIONS_FILE_STRING = "Error during load. Invalid file specified.\n"
INVALID_WORKSPACE_STRING = "Invalid workspace file path specified.\n"
ADD_WORKSPACE_PROMPT_STRING = "Please add the path to the workspace file(.xjrf).\n"
REMOVE_WORKSPACE_PROMPT_STRING = "Please select the workspace you wish to remove:\n"
SELECT_COMMAND_PROMPT_STRING = "Input next action (launch, download, run, stop, attach, close, detach, reset):\n"
SELECT_WORKSPACE_PROMPT_STRING = "Please select the workspace you wish to address:\n"
SELECT_MASTER_PROMPT_STRING = "Please select the master workspace:\n"
LOAD_CONFIGURATIONS_FILE_STRING = "Please specify the configurations file (.yaml) path:\n"
LOAD_FILE_ERROR_STRING = "Error during load. Please check the configurations file format/data.\n"
INDEX_OUT_OF_RANGE_STRING = "Error - index out of range. Invalid workspace selected.\n"


def emuSyncMain(commandQueue):
    log.basicConfig(filename=r"log\EmuSyncCmdFileLog.txt", filemode='w', level=log.INFO)

    engineCtrl = EngineController()

    while True:
        if not commandQueue.empty():
            newCommand = commandQueue.get()
            if StaticCommandText.LOAD_WORKSPACE_PREFIX.value in newCommand:
                configurationsPath = newCommand[4:]
                isLoaded = engineCtrl.addFileConfigurations(filePath=configurationsPath)
                if not isLoaded:
                    print(LOAD_FILE_ERROR_STRING)
            elif StaticCommandText.COMMAND_ONE_PREFIX.value in newCommand:
                listPosition = int(newCommand[4:5])
                command = newCommand[6:]
                if listPosition < engineCtrl.getNumberOfProcesses():
                    engineCtrl.commandOne(command=engineCtrl.commandDict[command], listIndex=listPosition)
                else:
                    print(INDEX_OUT_OF_RANGE_STRING)
            elif StaticCommandText.COMMAND_ALL_PREFIX.value in newCommand:
                command = newCommand[4:]
                engineCtrl.commandAll(command=engineCtrl.commandDict[command])
            elif StaticCommandText.ADD_WORKSPACE_PREFIX.value in newCommand:
                engineCtrl.addWorkspace(wsPath=newCommand[4:])
            elif newCommand == StaticCommandText.PRINT_LIST.value:
                engineCtrl.printItemizedWorkspaceList()
            elif StaticCommandText.REMOVE_WORKSPACE_PREFIX.value in newCommand:
                listPosition = int(newCommand[4:5])
                if listPosition < engineCtrl.getNumberOfProcesses():
                    engineCtrl.removeWorkspace(index=listPosition)
                else:
                    print(INDEX_OUT_OF_RANGE_STRING)
            elif StaticCommandText.SET_AS_MASTER_PREFIX.value in newCommand:
                listPosition = int(newCommand[4:5])
                if listPosition < engineCtrl.getNumberOfProcesses():
                    engineCtrl.setMaster(listIndex=listPosition)
                else:
                    print(INDEX_OUT_OF_RANGE_STRING)
            elif newCommand == StaticCommandText.PRINT_STATUS.value:
                engineCtrl.printStatus()
            else:
                print(StaticCommandText.INVALID_COMMAND.value, newCommand)

        engineCtrl.checkAndPrintStatusUpdates()


def emuSyncInputProcess():
    inputCommandsQueue = mp.Queue()
    emuSyncProcess = mp.Process(target=emuSyncMain, args=(inputCommandsQueue,))
    emuSyncProcess.start()
    time.sleep(0.1)

    while True:
        firstMenuChoice = input(MAIN_MENU_PROMPT_STRING)
        if firstMenuChoice == MainMenuInputValue.LOAD_WORKSPACE.value:
            configurationFilePathText = input(LOAD_CONFIGURATIONS_FILE_STRING)
            configurationFilePath = Path(configurationFilePathText)
            if configurationFilePath.is_file() and str(configurationFilePath).endswith(".EmuSync"):
                inputCommandsQueue.put(StaticCommandText.LOAD_WORKSPACE_PREFIX.value + configurationFilePathText)
            else:
                print(INVALID_CONFIGURATIONS_FILE_STRING)
        elif firstMenuChoice == MainMenuInputValue.ADD_WORKSPACE.value:
            newWorkspacePathText = input(ADD_WORKSPACE_PROMPT_STRING)
            newWorkspacePath = Path(newWorkspacePathText)
            if newWorkspacePath.is_file() and str(newWorkspacePathText).endswith(".xjrf"):
                inputCommandsQueue.put(StaticCommandText.ADD_WORKSPACE_PREFIX.value + newWorkspacePathText)
            elif newWorkspacePathText == MainMenuInputValue.BACK.value:
                pass
            else:
                print(INVALID_WORKSPACE_STRING)
        elif firstMenuChoice == MainMenuInputValue.REMOVE_WORKSPACE.value:
            print(REMOVE_WORKSPACE_PROMPT_STRING)
            inputCommandsQueue.put(StaticCommandText.PRINT_LIST.value)
            try:
                removedWorkspaceIndex = int(input())
                inputCommandsQueue.put(StaticCommandText.REMOVE_WORKSPACE_PREFIX.value + str(removedWorkspaceIndex))
            except ValueError:
                print(INVALID_VALUE_STRING)
        elif firstMenuChoice == MainMenuInputValue.COMMAND_ALL.value:
            selectedCommand = input(SELECT_COMMAND_PROMPT_STRING)
            if any(command.value == selectedCommand for command in CPUCommand):
                inputCommandsQueue.put(StaticCommandText.COMMAND_ALL_PREFIX.value + selectedCommand)
            else:
                print(StaticCommandText.INVALID_COMMAND.value)
        elif firstMenuChoice == MainMenuInputValue.COMMAND_ONE.value:
            print(SELECT_WORKSPACE_PROMPT_STRING)
            inputCommandsQueue.put(StaticCommandText.PRINT_LIST.value)
            try:
                selectedWorkspaceIndex = int(input())
                selectedCommand = input(SELECT_COMMAND_PROMPT_STRING)
                if any(command.value == selectedCommand for command in CPUCommand):
                    inputCommandsQueue.put(StaticCommandText.COMMAND_ONE_PREFIX.value + str(selectedWorkspaceIndex) + "_" + selectedCommand)
                else:
                    print(StaticCommandText.INVALID_COMMAND.value)
            except ValueError:
                print(INVALID_VALUE_STRING)
        elif firstMenuChoice == MainMenuInputValue.SET_AS_MASTER.value:
            print(SELECT_MASTER_PROMPT_STRING)
            inputCommandsQueue.put(StaticCommandText.PRINT_LIST.value)
            try:
                selectedWorkspaceIndex = int(input())
                inputCommandsQueue.put(StaticCommandText.SET_AS_MASTER_PREFIX.value + str(selectedWorkspaceIndex))
            except ValueError:
                print(INVALID_VALUE_STRING)
        elif firstMenuChoice == MainMenuInputValue.PRINT_STATUS.value:
            inputCommandsQueue.put(StaticCommandText.PRINT_STATUS.value)
            time.sleep(0.2)
        elif firstMenuChoice == MainMenuInputValue.QUIT.value or firstMenuChoice == MainMenuInputValue.EXIT.value:
            inputCommandsQueue.put(StaticCommandText.COMMAND_ALL_PREFIX.value + CPUCommand.CLOSE.value)
            time.sleep(0.2)
            quit()


if __name__ == '__main__':
    emuSyncInputProcess()
