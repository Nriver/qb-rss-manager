from loguru import logger


def refresh_tray():
    """
    Windows系统 刷新任务栏托盘图标, 去掉强制关闭进程后的残留图标
    """
    try:
        import win32gui
        from win32con import WM_MOUSEMOVE
    except:
        return
    logger.info('刷新任务栏托盘图标')
    hShellTrayWnd = win32gui.FindWindow("Shell_trayWnd", "")
    hTrayNotifyWnd = win32gui.FindWindowEx(hShellTrayWnd, 0, "TrayNotifyWnd", None)
    hSysPager = win32gui.FindWindowEx(hTrayNotifyWnd, 0, 'SysPager', None)
    if hSysPager:
        hToolbarWindow32 = win32gui.FindWindowEx(hSysPager, 0, 'ToolbarWindow32', None)
    else:
        hToolbarWindow32 = win32gui.FindWindowEx(hTrayNotifyWnd, 0, 'ToolbarWindow32', None)
    logger.info(f'hToolbarWindow32 {hToolbarWindow32}')
    if hToolbarWindow32:
        rect = win32gui.GetWindowRect(hToolbarWindow32)
        logger.info(rect)
        # 窗口宽度 // 图标宽度 = 图标个数?
        for x in range((rect[2] - rect[0]) // 24):
            win32gui.SendMessage(hToolbarWindow32, WM_MOUSEMOVE, 0, 1)
