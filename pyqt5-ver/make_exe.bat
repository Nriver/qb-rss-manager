rmdir /s /q __pycache__
del QBRssManager.exe
rem pyinstaller --icon=QBRssManager.ico -F -w QBRssManager.py
pyinstaller QBRssManager.spec
move dist\QBRssManager.exe QBRssManager.exe
rem del QBRssManager.spec
rmdir /s /q __pycache__
rmdir /s /q build
rmdir /s /q dist
rem pause()