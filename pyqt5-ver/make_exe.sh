rm -rf __pycache__
rm -f QBRssManager
# pyinstaller --icon=QBRssManager.ico -F -w QBRssManager.py
pyinstaller QBRssManager.spec
mv dist/QBRssManager QBRssManager
# del QBRssManager.spec
rm -rf __pycache__
rm -rf build
rm -rf dist
