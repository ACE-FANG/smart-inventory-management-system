from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QLabel, QDateEdit, QGroupBox, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate, Qt
from report_generator import ReportGenerator
from charts import InventoryChart
from config import Config

class ReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # 报表选项区域
        report_group = QGroupBox("生成报表")
        report_layout = QVBoxLayout()
        
        # 报表类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("报表类型:"))
        
        self.report_combo = QComboBox()
        self.report_combo.addItem("库存总览报告", "inventory")
        self.report_combo.addItem("库存历史报告", "history")
        self.report_combo.currentIndexChanged.connect(self.toggle_date_range)
        
        type_layout.addWidget(self.report_combo)
        type_layout.addStretch()
        
        # 日期范围选择
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日期范围:"))
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("至"))
        date_layout.addWidget(self.end_date)
        date_layout.addStretch()
        
        # 默认隐藏日期范围
        self.date_range_container = QWidget()
        self.date_range_container.setLayout(date_layout)
        self.date_range_container.hide()
        
        # 生成按钮
        generate_btn = QPushButton("生成报表")
        generate_btn.setIcon(QIcon("resources/report.png"))
        generate_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        generate_btn.clicked.connect(self.generate_report)
        
        report_layout.addLayout(type_layout)
        report_layout.addWidget(self.date_range_container)
        report_layout.addWidget(generate_btn, alignment=Qt.AlignRight)
        report_group.setLayout(report_layout)
        
        # 图表区域
        chart_group = QGroupBox("数据可视化")
        chart_layout = QVBoxLayout()
        
        # 图表类型选择
        chart_type_layout = QHBoxLayout()
        chart_type_layout.addWidget(QLabel("图表类型:"))
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItem("库存TOP10", "stock_levels")
        self.chart_combo.addItem("类别分布", "category_distribution")
        self.chart_combo.addItem("库存总量分布", "stock_by_category")
        self.chart_combo.addItem("出入库趋势", "in_out_trend")
        
        refresh_btn = QPushButton("刷新图表")
        refresh_btn.clicked.connect(self.refresh_chart)
        
        chart_type_layout.addWidget(self.chart_combo)
        chart_type_layout.addWidget(refresh_btn)
        chart_type_layout.addStretch()
        
        # 图表显示区域
        self.chart = InventoryChart(self, width=10, height=6)
        
        chart_layout.addLayout(chart_type_layout)
        chart_layout.addWidget(self.chart)
        chart_group.setLayout(chart_layout)
        
        main_layout.addWidget(report_group)
        main_layout.addWidget(chart_group)
        
        self.setLayout(main_layout)
        
        # 初始加载图表
        self.refresh_chart()
    
    def toggle_date_range(self):
        report_type = self.report_combo.currentData()
        self.date_range_container.setVisible(report_type == "history")
    
    def generate_report(self):
        report_type = self.report_combo.currentData()
        generator = ReportGenerator(Config.REPORT_DIR)
        
        if report_type == "inventory":
            # 使用当前操作员ID（这里假设从Config获取）
            operator_id = getattr(Config, 'CURRENT_USER', 'admin')
            file_path = generator.generate_inventory_report(
                operator_id=operator_id
            )
            QMessageBox.information(self, "成功", f"库存总览报告已生成: {file_path}")
        elif report_type == "history":
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            # 使用当前操作员ID（这里假设从Config获取）
            operator_id = getattr(Config, 'CURRENT_USER', 'admin')
            file_path = generator.generate_transaction_report(
                operator_id=operator_id,
                start_date=start_date,
                end_date=end_date
            )
            QMessageBox.information(self, "成功", f"库存历史报告已生成: {file_path}")
    
    def refresh_chart(self):
        chart_type = self.chart_combo.currentData()
        
        if chart_type == "stock_levels":
            self.chart.plot_stock_levels()
        elif chart_type == "category_distribution":
            self.chart.plot_category_distribution()
        elif chart_type == "stock_by_category":
            self.chart.plot_stock_value_by_category()
        elif chart_type == "in_out_trend":
            self.chart.plot_in_out_trend()