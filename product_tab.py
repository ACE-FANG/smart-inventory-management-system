import os
import sys
from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QFileDialog, QComboBox, QHeaderView, QTabWidget)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor
from PyQt5.QtCore import Qt, QSize
from inventory_manager import InventoryManager
from barcode_scanner import BarcodeScanner
from config import Config

class ProductTab(QWidget):
    def __init__(self, operator_id):
        super().__init__()
        self.operator_id = operator_id
        self.current_image_path = None
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # 创建选项卡
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 添加商品标签页
        self.add_tab = QWidget()
        self.setup_add_tab()
        self.tabs.addTab(self.add_tab, "添加商品")
        
        # 管理商品标签页
        self.manage_tab = QWidget()
        self.setup_manage_tab()
        self.tabs.addTab(self.manage_tab, "管理商品")
        
        self.setLayout(main_layout)
        
        # 加载数据
        self.load_data()
    
    def setup_add_tab(self):
        layout = QVBoxLayout()
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.spec_input = QLineEdit()
        self.supplier_input = QLineEdit()
        self.location_input = QLineEdit()
        self.barcode_input = QLineEdit()
        self.min_stock_input = QLineEdit("5")
        
        # 获取所有类别和位置
        with InventoryManager() as manager:
            categories = manager.get_all_categories()
            locations = manager.get_all_locations()
        
        # 使用下拉框选择类别和位置
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(categories)
        
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.addItems(locations)
        
        form_layout.addRow("商品名称*:", self.name_input)
        form_layout.addRow("类别*:", self.category_combo)
        form_layout.addRow("规格:", self.spec_input)
        form_layout.addRow("供应商:", self.supplier_input)
        form_layout.addRow("库存位置*:", self.location_combo)
        form_layout.addRow("条形码:", self.barcode_input)
        form_layout.addRow("最低库存:", self.min_stock_input)
        
        # 图片上传
        self.image_label = QLabel("无图片")
        self.image_label.setFixedSize(200, 200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        
        upload_btn = QPushButton("上传图片")
        upload_btn.setIcon(QIcon("resources/upload.png"))
        upload_btn.clicked.connect(self.upload_image)
        
        scan_btn = QPushButton("扫描条形码")
        scan_btn.setIcon(QIcon("resources/barcode.png"))
        scan_btn.clicked.connect(self.scan_barcode)
        
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.image_label)
        img_layout.addWidget(upload_btn)
        img_layout.addWidget(scan_btn)
        
        # 提交按钮
        submit_btn = QPushButton("添加商品")
        submit_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        submit_btn.clicked.connect(self.add_product)
        
        layout.addLayout(form_layout)
        layout.addLayout(img_layout)
        layout.addWidget(submit_btn)
        
        self.add_tab.setLayout(layout)
    
    def setup_manage_tab(self):
        layout = QVBoxLayout()
        
        # 搜索区域
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入商品名称或规格")
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.load_data)
        
        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        
        # 商品表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "商品名称", "类别", "库存位置", "当前库存", "最低库存", "状态", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        
        self.manage_tab.setLayout(layout)
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择商品图片", "", "图片文件 (*.png *.jpg *.jpeg)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            self.current_image_path = file_path
    
    def scan_barcode(self):
        scanner = BarcodeScanner()
        barcode = scanner.scan_barcode()
        if barcode:
            self.barcode_input.setText(barcode)
    
    def add_product(self):
        # 获取表单数据
        name = self.name_input.text().strip()
        category = self.category_combo.currentText().strip()
        spec = self.spec_input.text().strip()
        supplier = self.supplier_input.text().strip()
        location = self.location_combo.currentText().strip()
        barcode = self.barcode_input.text().strip()
        min_stock = self.min_stock_input.text().strip()
        
        # 验证必填字段
        if not name or not category or not location:
            QMessageBox.warning(self, "输入错误", "商品名称、类别和库存位置是必填项")
            return
        
        try:
            min_stock = int(min_stock) if min_stock else 5
        except ValueError:
            min_stock = 5
        
        # 处理图片路径
        image_path = None
        if self.current_image_path:
            # 保存图片到images目录
            os.makedirs(Config.IMAGE_DIR, exist_ok=True)
            filename = f"{name}_{barcode if barcode else 'no_barcode'}.png"
            image_path = os.path.join(Config.IMAGE_DIR, filename)
            
            # 复制图片到目标路径
            pixmap = QPixmap(self.current_image_path)
            pixmap.save(image_path)
        
        # 添加商品到数据库
        with InventoryManager() as manager:
            result = manager.add_product(
                self.operator_id, name, category, spec, supplier, location, 
                barcode, image_path, min_stock
            )
            
            if result == "barcode_exists":
                QMessageBox.warning(self, "添加失败", "该条形码已存在")
            elif result:
                QMessageBox.information(self, "成功", "商品添加成功")
                self.clear_form()
                self.load_data()
            else:
                QMessageBox.warning(self, "添加失败", "添加商品时出错")
    
    def clear_form(self):
        self.name_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.spec_input.clear()
        self.supplier_input.clear()
        self.location_combo.setCurrentIndex(0)
        self.barcode_input.clear()
        self.min_stock_input.setText("5")
        self.image_label.clear()
        self.image_label.setText("无图片")
        self.current_image_path = None
    
    def load_data(self):
        search_term = self.search_input.text().strip()
        
        with InventoryManager() as manager:
            products = manager.search_products(search_term=search_term)
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # 状态判断
                status = "正常" if product['stock'] > product['min_stock'] else "低库存"
                status_color = QColor(Config.NORMAL_STOCK_COLOR if status == "正常" else Config.LOW_STOCK_COLOR)
                
                # 填充数据
                self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(product['name']))
                self.table.setItem(row, 2, QTableWidgetItem(product['category']))
                self.table.setItem(row, 3, QTableWidgetItem(product['location']))
                self.table.setItem(row, 4, QTableWidgetItem(str(product['stock'])))
                self.table.setItem(row, 5, QTableWidgetItem(str(product['min_stock'])))
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(status_color)
                self.table.setItem(row, 6, status_item)
                
                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                
                edit_btn = QPushButton("编辑")
                edit_btn.setIcon(QIcon("resources/edit.png"))
                edit_btn.clicked.connect(partial(self.edit_product, product))
                
                delete_btn = QPushButton("删除")
                delete_btn.setIcon(QIcon("resources/delete.png"))
                delete_btn.setStyleSheet("background-color: #f44336; color: white;")
                delete_btn.clicked.connect(partial(self.delete_product, product))
                
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table.setCellWidget(row, 7, btn_widget)
    
    def edit_product(self, product):
        # 创建编辑对话框
        dialog = QWidget()
        dialog.setWindowTitle("编辑商品信息")
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        name_input = QLineEdit(product['name'])
        category_input = QLineEdit(product['category'])
        spec_input = QLineEdit(product['specification'])
        supplier_input = QLineEdit(product['supplier'])
        location_input = QLineEdit(product['location'])
        barcode_input = QLineEdit(product['barcode'])
        min_stock_input = QLineEdit(str(product['min_stock']))
        
        form_layout.addRow("商品名称*:", name_input)
        form_layout.addRow("类别*:", category_input)
        form_layout.addRow("规格:", spec_input)
        form_layout.addRow("供应商:", supplier_input)
        form_layout.addRow("库存位置*:", location_input)
        form_layout.addRow("条形码:", barcode_input)
        form_layout.addRow("最低库存:", min_stock_input)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(lambda: self.save_edited_product(
            product['id'],
            name_input.text().strip(),
            category_input.text().strip(),
            spec_input.text().strip(),
            supplier_input.text().strip(),
            location_input.text().strip(),
            barcode_input.text().strip(),
            min_stock_input.text().strip(),
            dialog
        ))
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.close)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.show()
    
    def save_edited_product(self, product_id, name, category, spec, supplier, location, barcode, min_stock, dialog):
        # 验证必填字段
        if not name or not category or not location:
            QMessageBox.warning(self, "输入错误", "商品名称、类别和库存位置是必填项")
            return
        
        try:
            min_stock = int(min_stock) if min_stock else 5
        except ValueError:
            min_stock = 5
        
        # 更新商品信息到数据库
        with InventoryManager() as manager:
            # 创建更新字段字典
            update_fields = {
                'name': name,
                'category': category,
                'specification': spec,
                'supplier': supplier,
                'location': location,
                'barcode': barcode,
                'min_stock': min_stock
            }
            
            # 移除未更改的字段
            current_product = manager.get_product_by_id(product_id)
            for field in list(update_fields.keys()):
                if update_fields[field] == current_product.get(field):
                    del update_fields[field]
            
            # 如果有实际变更才更新
            if update_fields:
                result = manager.update_product(
                    self.operator_id,
                    product_id,
                    **update_fields
                )
            else:
                result = True  # 没有变更也视为成功
            
            if result:
                QMessageBox.information(self, "成功", "商品信息更新成功")
                dialog.close()
                self.load_data()
            else:
                QMessageBox.warning(self, "失败", "更新商品信息时出错")
    
    def delete_product(self, product):
        with InventoryManager() as manager:
            if manager.delete_product(self.operator_id, product['id']):
                QMessageBox.information(self, "成功", "商品删除成功")
                self.load_data()
            else:
                QMessageBox.warning(self, "失败", "删除商品时出错")