# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from database import init_database, get_db_path  # 导入初始化函数和路径获取函数

if __name__ == "__main__":
    # 获取数据库路径
    db_path = get_db_path()
    
    # 检查数据库是否存在，不存在则初始化
    if not os.path.exists(db_path):
        print(f"数据库不存在，正在初始化: {db_path}")
        init_database()
    else:
        print(f"数据库已存在: {db_path}")
    
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())