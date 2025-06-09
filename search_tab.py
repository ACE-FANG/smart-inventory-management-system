from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QHeaderView, QGroupBox, QMessageBox)
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt
from inventory_manager import InventoryManager
from config import Config

class SearchTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # 搜索区域
        search_group = QGroupBox("搜索条件")
        search_layout = QFormLayout()
        
        # 获取所有类别和位置
        with InventoryManager() as manager:
            categories = manager.get_all_categories()
            locations = manager.get_all_locations()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入商品名称")
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("所有类别", "")
        self.category_combo.addItems(categories)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("输入条形码")
        
        self.location_combo = QComboBox()
        self.location_combo.addItem("所有位置", "")
        self.location_combo.addItems(locations)
        
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("输入供应商")
        
        search_layout.addRow("商品名称:", self.name_input)
        search_layout.addRow("类别:", self.category_combo)
        search_layout.addRow("条形码:", self.barcode_input)
        search_layout.addRow("库存位置:", self.location_combo)
        search_layout.addRow("供应商:", self.supplier_input)
        
        # 搜索按钮
        search_btn = QPushButton("搜索")
        search_btn.setIcon(QIcon("resources/search.png"))
        search_btn.setStyleSheet("background-color: #2196F3; color: white;")
        search_btn.clicked.connect(self.load_data)
        
        search_layout.addRow(search_btn)
        search_group.setLayout(search_layout)
        
        # 商品表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "商品名称", "类别", "规格", "供应商", "库存位置", "当前库存"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.show_product_details)
        
        main_layout.addWidget(search_group)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def load_data(self):
        name = self.name_input.text().strip()
        category = self.category_combo.currentData()
        barcode = self.barcode_input.text().strip()
        location = self.location_combo.currentData()
        supplier = self.supplier_input.text().strip()
        
        with InventoryManager() as manager:
            products = manager.search_products(
                search_term=name,
                category=category,
                barcode=barcode,
                location=location,
                supplier=supplier
            )
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # 填充数据
                self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(product['name']))
                self.table.setItem(row, 2, QTableWidgetItem(product['category']))
                self.table.setItem(row, 3, QTableWidgetItem(product['specification'] or ""))
                self.table.setItem(row, 4, QTableWidgetItem(product['supplier'] or ""))
                self.table.setItem(row, 5, QTableWidgetItem(product['location']))
                
                # 库存状态
                stock = str(product['stock'])
                stock_item = QTableWidgetItem(stock)
                
                if product['stock'] <= product['min_stock']:
                    stock_item.setForeground(QColor(Config.LOW_STOCK_COLOR))
                
                self.table.setItem(row, 6, stock_item)
    
    def show_product_details(self, row, column):
        product_id = int(self.table.item(row, 0).text())
        
        with InventoryManager() as manager:
            product = manager.get_product_by_id(product_id)
            
            if product:
                details = (
                    f"<b>商品名称:</b> {product['name']}<br>"
                    f"<b>类别:</b> {product['category']}<br>"
                    f"<b>规格:</b> {product['specification'] or '无'}<br>"
                    f"<b>供应商:</b> {product['supplier'] or '无'}<br>"
                    f"<b>库存位置:</b> {product['location']}<br>"
                    f"<b>条形码:</b> {product['barcode'] or '无'}<br>"
                    f"<b>当前库存:</b> {product['stock']}<br>"
                    f"<b>最低库存:</b> {product['min_stock']}<br>"
                )
                
                QMessageBox.information(self, "商品详情", details)