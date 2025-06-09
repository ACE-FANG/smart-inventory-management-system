# build.py
import os
from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = [
        'main.py',
        '--name=InventoryManager',
        '--windowed',
        '--onefile',
        '--add-data=images;images',
        '--add-data=reports;reports',
        '--add-data=resources;resources',
        '--add-data=inventory.db;.',  # 如果有初始数据库文件
        '--hidden-import=sqlite3',
        '--hidden-import=cv2',
        '--hidden-import=pyzbar',
        '--hidden-import=reportlab',
        '--hidden-import=matplotlib',
        '--icon=resources/icon.png',
        '--debug=all'  # 启用调试模式，方便排查问题
    ]
    run(opts)