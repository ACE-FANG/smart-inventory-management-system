import sys
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QStatusBar, QAction, QMenuBar, 
                             QMessageBox, QToolBar, QLabel)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from ui.product_tab import ProductTab
from ui.inventory_tab import InventoryTab
from ui.report_tab import ReportTab
from ui.search_tab import SearchTab
from ui.outbound_tab import OutboundTab
from audit_logger import AuditLogger
from functools import partial
from config import Config   

class MainWindow(QMainWindow):
    def __init__(self, user_id, role):
        super().__init__()
        self.user_id = user_id
        self.role = role
        self.setWindowTitle(f"智能商品库存管理系统 - {Config.ROLES.get(role, '用户')}")
        self.setGeometry(100, 100, 1000, 700)
        
        # 初始化UI
        self.setup_ui()
        
        # 记录登录日志
        with AuditLogger() as logger:
            logger.log_action(
                user_id, 
                "用户登录", 
                f"用户 {user_id} 登录系统",
                "127.0.0.1"
            )
    
    def setup_ui(self):
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.statusBar().showMessage(f"当前用户: {self.user_id} | 角色: {Config.ROLES.get(self.role, '用户')}")
        
        # 创建主选项卡
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 根据角色添加不同标签页
        if self.role == 'admin':
            self.product_tab = ProductTab(self.user_id)
            self.inventory_tab = InventoryTab(self.user_id)
            self.tabs.addTab(self.product_tab, "商品管理")
            self.tabs.addTab(self.inventory_tab, "库存操作")
            self.tabs.addTab(ReportTab(), "报表管理")
        elif self.role == 'store_keeper':
            self.product_tab = ProductTab(self.user_id)
            self.inventory_tab = InventoryTab(self.user_id)
            self.tabs.addTab(self.product_tab, "商品管理")
            self.tabs.addTab(self.inventory_tab, "库存操作")
        else:
            self.tabs.addTab(SearchTab(), "商品查询")
            self.tabs.addTab(OutboundTab(self.user_id), "出库操作")
    
    def create_menu(self):
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 添加工具栏按钮
        refresh_action = QAction(QIcon("resources/refresh.png"), "刷新", self)
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
        if self.role == 'admin':
            report_action = QAction(QIcon("resources/report.png"), "生成报告", self)
            report_action.triggered.connect(self.generate_report)
            toolbar.addAction(report_action)
        
        logout_action = QAction(QIcon("resources/logout.png"), "退出登录", self)
        logout_action.triggered.connect(self.logout)
        toolbar.addAction(logout_action)
    
    def refresh_data(self):
        """刷新所有标签页数据"""
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'load_data'):
                tab.load_data()
        
        QMessageBox.information(self, "刷新成功", "数据已刷新")
    
    def generate_report(self):
        """生成报告"""
        if self.role == 'admin':
            # 获取报表标签页并生成报告
            report_tab = None
            for i in range(self.tabs.count()):
                if isinstance(self.tabs.widget(i), ReportTab):
                    report_tab = self.tabs.widget(i)
                    break
            
            if report_tab:
                report_tab.generate_report()
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
        <h2>智能商品库存管理系统</h2>
        <p>版本: 1.0.0</p>
        <p>开发单位: 宁波财经学院</p>
        <p>计算机科学与技术专业</p>
        <p>© 2024 智能控制应用开发课程</p>
        """
        QMessageBox.about(self, "关于", about_text)
    
    def logout(self):
        """退出登录"""
        from ui.login_window import LoginWindow  # 延迟导入避免循环依赖
        
        # 记录登出日志
        with AuditLogger() as logger:
            logger.log_action(
                self.user_id, 
                "用户登出", 
                f"用户 {self.user_id} 登出系统",
                "127.0.0.1"
            )
        
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 记录登出日志
        with AuditLogger() as logger:
            logger.log_action(
                self.user_id, 
                "用户登出", 
                f"用户 {self.user_id} 关闭系统",
                "127.0.0.1"
            )
        event.accept()