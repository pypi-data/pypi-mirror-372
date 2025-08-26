import isystem.connect as ic
import time

# The connection manager is passed to the hook from EmuSync so that you can manipulate winIDEA inside the hook.


def onStopHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)
    executionMgr.stop()


def onDownloadHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)


def onResetHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)


def onRunHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)


def preStopHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)


def preDownloadHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)


def preResetHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)


def preRunHook(connMgr):
    loaderMgr = ic.CLoaderController(connMgr)
    loaderMgr.download()
    executionMgr = ic.CExecutionController(connMgr)
    executionMgr.run()
    time.sleep(5)
