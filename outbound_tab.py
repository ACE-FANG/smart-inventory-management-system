from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QHeaderView, QGroupBox, QMessageBox)
from PyQt5.QtGui import QColor, QIcon, QIntValidator
from PyQt5.QtCore import Qt
from inventory_manager import InventoryManager
from config import Config

class OutboundTab(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # 搜索区域
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入商品名称或条形码")
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.load_data)
        
        search_layout.addWidget(QLabel("搜索商品:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        
        # 商品表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "商品名称", "类别", "库存位置", "当前库存", "最低库存", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellClicked.connect(self.product_selected)
        
        # 出库操作区域
        operation_group = QGroupBox("出库操作")
        operation_layout = QFormLayout()
        
        self.product_name_label = QLabel("未选择商品")
        self.current_stock_label = QLabel("-")
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(1, 9999))
        
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("输入客户信息（可选）")
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("输入备注信息（可选）")
        
        self.outbound_btn = QPushButton("确认出库")
        self.outbound_btn.setEnabled(False)
        self.outbound_btn.setIcon(QIcon("resources/outbound.png"))
        self.outbound_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.outbound_btn.clicked.connect(self.perform_outbound)
        
        operation_layout.addRow("商品:", self.product_name_label)
        operation_layout.addRow("当前库存:", self.current_stock_label)
        operation_layout.addRow("出库数量*:", self.quantity_input)
        operation_layout.addRow("客户信息:", self.customer_input)
        operation_layout.addRow("备注:", self.notes_input)
        operation_layout.addRow(self.outbound_btn)
        
        operation_group.setLayout(operation_layout)
        
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table, 3)
        main_layout.addWidget(operation_group, 1)
        
        self.setLayout(main_layout)
    
    def load_data(self):
        search_term = self.search_input.text().strip()
        
        with InventoryManager() as manager:
            products = manager.search_products(search_term=search_term)
            
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
        self.outbound_btn.setEnabled(True)
    
    def perform_outbound(self):
        if not hasattr(self, 'selected_product_id'):
            QMessageBox.warning(self, "错误", "请先选择一个商品")
            return
        
        try:
            quantity = int(self.quantity_input.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的出库数量（大于0的整数）")
            return
        
        customer = self.customer_input.text().strip()
        notes = self.notes_input.text().strip()
        
        # 组合备注信息
        full_notes = f"出库给客户: {customer}" if customer else ""
        if notes:
            full_notes += f" | {notes}" if full_notes else notes
        
        with InventoryManager() as manager:
            # 修复参数顺序问题：正确顺序是 (operator_id, product_id, change_amount, operation_type, notes)
            success = manager.update_stock(
                self.user_id,  # 操作员ID
                self.selected_product_id,  # 商品ID
                quantity,  # 出库数量
                "out",  # 操作类型
                full_notes  # 备注
            )
            
            if success:
                QMessageBox.information(self, "成功", "出库操作已记录")
                self.load_data()
                self.reset_operation_form()
            else:
                QMessageBox.warning(self, "失败", "执行出库操作时出错")
    
    def reset_operation_form(self):
        self.product_name_label.setText("未选择商品")
        self.current_stock_label.setText("-")
        self.quantity_input.clear()
        self.customer_input.clear()
        self.notes_input.clear()
        self.outbound_btn.setEnabled(False)
        delattr(self, 'selected_product_id')