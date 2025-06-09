import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from user_manager import UserManager

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("库存管理系统 - 登录")
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        
        # 添加Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logo.png").scaled(100, 100, Qt.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        
        # 添加标题
        title_label = QLabel("智能商品库存管理系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("用户名:", self.username_input)
        form_layout.addRow("密码:", self.password_input)
        
        main_layout.addLayout(form_layout)
        
        # 登录按钮
        login_btn = QPushButton("登 录")
        login_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        login_btn.clicked.connect(self.authenticate)
        main_layout.addWidget(login_btn)
        
        # 底部信息
        footer_label = QLabel("© 2024 宁波财经学院 - 智能控制应用开发")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: gray; font-size: 10px; margin-top: 20px;")
        main_layout.addWidget(footer_label)
        
        self.setLayout(main_layout)
    
    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
            return
        
        with UserManager() as manager:
            user = manager.authenticate(username, password)
            
            if user:
                from ui.main_window import MainWindow  # 延迟导入避免循环依赖
                self.main_window = MainWindow(user[0], user[1])
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "登录失败", "用户名或密码错误")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())