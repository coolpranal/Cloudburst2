import platform

if platform.architecture()[0] != "32bit":
    raise Exception("Architecture not supported: %s" % platform.architecture()[0])

import os
import sys

libcefDll = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcef.dll')
if os.path.exists(libcefDll):  # If the libcef dll exists use that for imports
    if 0x02070000 <= sys.hexversion < 0x03000000:
        import cefpython_py27 as cefpython  # Import for python 2.7
    elif 0x03000000 <= sys.hexversion < 0x04000000:
        import cefpython_py32 as cefpython  # Import for python 3.2
    else:
        raise Exception('Unsupported python version: %s' % sys.version)
else:
    from cefpython3 import cefpython  # Import cefpython from package

import win32con
import win32gui

from cloudburst import window
from cloudburst.exceptions.exceptionHook import exceptionHook
from cloudburst.util.applicationPath import getApplicationPath

DEBUG = True


def cloudburstMain():
    sys.excepthook = exceptionHook
    applicationSettings = dict()

    if DEBUG:
        window.g_debug = True
        applicationSettings['debug'] = True
        applicationSettings['release_dcheck_enabled'] = True

    applicationSettings['log_file'] = getApplicationPath('debug.log')
    applicationSettings['log_severity'] = cefpython.LOGSEVERITY_INFO
    applicationSettings['browser_subprocess_path'] = '%s/%s' % (cefpython.GetModuleDirectory(), 'subprocess')
    cefpython.Initialize(applicationSettings)

    browserSettings = dict()
    browserSettings['file_access_from_file_urls_allowed'] = True
    browserSettings['universal_access_from_file_urls_allowed'] = True

    windowHandles = {
        win32con.WM_CLOSE: closeWindow,
        win32con.WM_DESTROY: quitApplication,
        win32con.WM_SIZE: cefpython.WindowUtils.OnSize,
        win32con.WM_SETFOCUS: cefpython.WindowUtils.OnSetFocus,
        win32con.WM_ERASEBKGND: cefpython.WindowUtils.OnEraseBackground
    }

    windowHandle = window.createWindow(title='Cloudburst', className='Cloudburst', width=800, height=700,
                                       icon=getApplicationPath('res/images/cloudburst.ico'), windowHandle=windowHandles)

    windowInfo = cefpython.WindowInfo()
    windowInfo.SetAsChild(windowHandle)
    cefpython.CreateBrowserSync(windowInfo, browserSettings, navigateUrl=getApplicationPath("res/views/vlc-test.html"))
    cefpython.MessageLoop()
    cefpython.Shutdown()


def closeWindow(windowHandle, message, wparam, lparam):
    browser = cefpython.GetBrowserByWindowHandle(windowHandle)
    browser.CloseBrowser()
    return win32gui.DefWindowProc(windowHandle, message, wparam, lparam)


def quitApplication(windowHandle, message, wparam, lparam):
    win32gui.PostQuitMessage(0)
    return 0


if __name__ == "__main__":
    cloudburstMain()
