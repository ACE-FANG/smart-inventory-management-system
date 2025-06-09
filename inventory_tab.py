import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QComboBox, QHeaderView, QGroupBox)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from inventory_manager import InventoryManager
from config import Config

class InventoryTab(QWidget):
    def __init__(self, operator_id):
        super().__init__()
        self.operator_id = operator_id
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # 搜索区域
        search_group = QGroupBox("搜索条件")
        search_layout = QFormLayout()
        
        # 获取所有类别
        with InventoryManager() as manager:
            categories = manager.get_all_categories()
        
        # 搜索输入
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入商品名称或条形码")
        
        # 类别下拉框
        self.category_combo = QComboBox()
        self.category_combo.addItem("所有类别", "")
        self.category_combo.addItems(categories)
        
        # 搜索按钮
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.load_products)
        
        search_layout.addRow("关键字:", self.search_input)
        search_layout.addRow("类别:", self.category_combo)
        search_layout.addRow(search_btn)
        search_group.setLayout(search_layout)
        
        # 商品表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "商品名称", "类别", "库存位置", "当前库存", "最低库存", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellClicked.connect(self.product_selected)
        
        # 库存操作区域
        operation_group = QGroupBox("库存操作")
        operation_layout = QFormLayout()
        
        self.product_name_label = QLabel("未选择商品")
        self.current_stock_label = QLabel("-")
        
        self.operation_combo = QComboBox()
        self.operation_combo.addItem("入库", "in")
        self.operation_combo.addItem("出库", "out")
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(1, 9999))
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("输入备注信息（可选）")
        
        self.operate_btn = QPushButton("执行操作")
        self.operate_btn.setEnabled(False)
        self.operate_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.operate_btn.clicked.connect(self.perform_operation)
        
        operation_layout.addRow("商品:", self.product_name_label)
        operation_layout.addRow("当前库存:", self.current_stock_label)
        operation_layout.addRow("操作类型:", self.operation_combo)
        operation_layout.addRow("数量*:", self.quantity_input)
        operation_layout.addRow("备注:", self.notes_input)
        operation_layout.addRow(self.operate_btn)
        
        operation_group.setLayout(operation_layout)
        
        main_layout.addWidget(search_group)
        main_layout.addWidget(self.table, 3)
        main_layout.addWidget(operation_group, 1)
        
        self.setLayout(main_layout)
        
        # 加载初始数据
        self.load_products()
    
    def load_products(self):
        search_term = self.search_input.text().strip()
        category = self.category_combo.currentText() if self.category_combo.currentIndex() > 0 else ""
        
        with InventoryManager() as manager:
            products = manager.search_products(
                search_term=search_term,
                category=category
            )
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # 状态判断
                status = "正常" if product['stock'] > product['min_stock'] else "低库存"
                status_color = Config.NORMAL_STOCK_COLOR if status == "正常" else Config.LOW_STOCK_COLOR
                
                # 填充数据
                self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(product['name']))
                self.table.setItem(row, 2, QTableWidgetItem(product['category']))
                self.table.setItem(row, 3, QTableWidgetItem(product['location']))
                self.table.setItem(row, 4, QTableWidgetItem(str(product['stock'])))
                self.table.setItem(row, 5, QTableWidgetItem(str(product['min_stock'])))
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                self.table.setItem(row, 6, status_item)
    
    def product_selected(self, row, column):
        product_id = int(self.table.item(row, 0).text())
        product_name = self.table.item(row, 1).text()
        current_stock = self.table.item(row, 4).text()
        
        self.selected_product_id = product_id
        self.product_name_label.setText(product_name)
        self.current_stock_label.setText(current_stock)
        self.operate_btn.setEnabled(True)
    
    def perform_operation(self):
        if not hasattr(self, 'selected_product_id'):
            QMessageBox.warning(self, "错误", "请先选择一个商品")
            return
        
        try:
            quantity = int(self.quantity_input.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数量（大于0的整数）")
            return
        
        operation_type = self.operation_combo.currentData()
        notes = self.notes_input.text().strip()
        
        with InventoryManager() as manager:
            success = manager.update_stock(
                self.operator_id,
                self.selected_product_id,
                quantity,
                operation_type,
                notes
            )
            
            if success:
                QMessageBox.information(self, "成功", "库存操作已记录")
                self.load_products()
                self.reset_operation_form()
            else:
                QMessageBox.warning(self, "失败", "执行库存操作时出错")
    
    def reset_operation_form(self):
        self.product_name_label.setText("未选择商品")
        self.current_stock_label.setText("-")
        self.operation_combo.setCurrentIndex(0)
        self.quantity_input.clear()
        self.notes_input.clear()
        self.operate_btn.setEnabled(False)
        delattr(self, 'selected_product_id')