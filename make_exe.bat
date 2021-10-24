rmdir /s /q __pycache__
del QBRssManager.exe
pyinstaller -F -w QBRssManager.py
move dist\QBRssManager.exe QBRssManager.exe
del QBRssManager.spec
rmdir /s /q __pycache__
rmdir /s /q build
rmdir /s /q dist
rem pause()