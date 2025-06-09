import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy
from inventory_manager import InventoryManager
import numpy as np
import logging

# 设置支持中文的字体，例如SimHei（黑体）
plt.rcParams['font.family'] = 'SimHei'
# 解决负号显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False

class InventoryChart(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        """
        初始化库存图表
        :param parent: 父组件
        :param width: 图表宽度
        :param height: 图表高度
        :param dpi: 分辨率
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logger = logging.getLogger('inventory_chart')
        
        # 默认图表
        self.ax = self.fig.add_subplot(111)
        self.plot_stock_levels()
    
    def plot_stock_levels(self, top_n=10):
        """
        绘制库存TOP N商品
        :param top_n: 显示前N个商品
        """
        try:
            self.ax.clear()
            
            with InventoryManager() as manager:
                products = manager.search_products()
                if not products:
                    self.ax.text(0.5, 0.5, '没有商品数据', 
                                horizontalalignment='center', 
                                verticalalignment='center', 
                                transform=self.ax.transAxes)
                    self.draw()
                    return
                
                # 按库存排序
                sorted_products = sorted(products, key=lambda x: x['stock'], reverse=True)[:top_n]
                
                names = [p['name'] for p in sorted_products]
                stocks = [p['stock'] for p in sorted_products]
                
                # 创建水平条形图
                y_pos = np.arange(len(names))
                bars = self.ax.barh(y_pos, stocks, align='center', color='skyblue')
                self.ax.set_yticks(y_pos)
                self.ax.set_yticklabels(names)
                self.ax.invert_yaxis()  # 从上到下显示
                self.ax.set_xlabel('库存数量')
                self.ax.set_title(f'商品库存TOP {top_n}')
                
                # 在条形图上添加数值标签
                for bar in bars:
                    width = bar.get_width()
                    self.ax.text(width + max(stocks)*0.01, bar.get_y() + bar.get_height()/2, 
                                f'{int(width)}', 
                                va='center', ha='left')
            
            self.fig.tight_layout()
            self.draw()
        except Exception as e:
            self.logger.error(f"绘制库存水平图失败: {e}")
    
    def plot_category_distribution(self):
        """
        绘制商品类别分布图
        """
        try:
            self.ax.clear()
            
            with InventoryManager() as manager:
                categories = manager.get_all_categories()
                if not categories:
                    self.ax.text(0.5, 0.5, '没有类别数据', 
                                horizontalalignment='center', 
                                verticalalignment='center', 
                                transform=self.ax.transAxes)
                    self.draw()
                    return
                
                # 获取每个类别的商品数量
                category_counts = {}
                for category in categories:
                    products = manager.search_products(category=category)
                    category_counts[category] = len(products)
                
                # 排序
                sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
                
                labels = [item[0] for item in sorted_categories]
                counts = [item[1] for item in sorted_categories]
                
                # 创建饼图
                wedges, texts, autotexts = self.ax.pie(
                    counts, 
                    labels=labels, 
                    autopct=lambda p: f'{p:.1f}% ({int(p * sum(counts) / 100)})',
                    startangle=90,
                    wedgeprops={'edgecolor': 'w', 'linewidth': 1}
                )
                
                self.ax.set_title('商品类别分布')
                self.ax.axis('equal')  # 确保饼图是圆的
                
                # 调整标签位置
                for text in texts:
                    text.set_fontsize(8)
                for autotext in autotexts:
                    autotext.set_fontsize(8)
            
            self.fig.tight_layout()
            self.draw()
        except Exception as e:
            self.logger.error(f"绘制类别分布图失败: {e}")
    
    def plot_stock_value_by_category(self):
        """
        绘制按类别分组的库存价值图（假设每个商品价值相同）
        """
        try:
            self.ax.clear()
            
            with InventoryManager() as manager:
                categories = manager.get_all_categories()
                if not categories:
                    self.ax.text(0.5, 0.5, '没有类别数据', 
                                horizontalalignment='center', 
                                verticalalignment='center', 
                                transform=self.ax.transAxes)
                    self.draw()
                    return
                
                # 获取每个类别的总库存
                category_stock = {}
                for category in categories:
                    products = manager.search_products(category=category)
                    total_stock = sum(p['stock'] for p in products)
                    category_stock[category] = total_stock
                
                # 排序
                sorted_categories = sorted(category_stock.items(), key=lambda x: x[1], reverse=True)
                
                labels = [item[0] for item in sorted_categories]
                stocks = [item[1] for item in sorted_categories]
                
                # 创建条形图
                x_pos = np.arange(len(labels))
                bars = self.ax.bar(x_pos, stocks, align='center', color='lightgreen')
                self.ax.set_xticks(x_pos)
                self.ax.set_xticklabels(labels, rotation=45, ha='right')
                self.ax.set_ylabel('库存总量')
                self.ax.set_title('按类别分组的库存总量')
                
                # 在条形图上添加数值标签
                for bar in bars:
                    height = bar.get_height()
                    self.ax.text(bar.get_x() + bar.get_width()/2, height + max(stocks)*0.01, 
                                f'{int(height)}', 
                                ha='center', va='bottom')
            
            self.fig.tight_layout()
            self.draw()
        except Exception as e:
            self.logger.error(f"绘制类别库存图失败: {e}")
    
    def plot_in_out_trend(self, days=30):
        """
        绘制近期的出入库趋势图
        :param days: 天数范围
        """
        try:
            self.ax.clear()
            
            with InventoryManager() as manager:
                # 获取最近days天的出入库数据
                # 注意：这里简化处理，实际应用中需要更复杂的日期处理
                history = manager.get_inventory_history()
                
                if not history:
                    self.ax.text(0.5, 0.5, '没有历史数据', 
                                horizontalalignment='center', 
                                verticalalignment='center', 
                                transform=self.ax.transAxes)
                    self.draw()
                    return
                
                # 按日期分组
                from collections import defaultdict
                daily_data = defaultdict(lambda: {'in': 0, 'out': 0})
                
                for record in history:
                    date = record['operation_time'].split()[0]  # 只取日期部分
                    if record['operation_type'] == 'in':
                        daily_data[date]['in'] += record['change_amount']
                    else:
                        daily_data[date]['out'] += record['change_amount']
                
                # 排序日期
                sorted_dates = sorted(daily_data.keys())[-days:]
                
                in_values = [daily_data[date]['in'] for date in sorted_dates]
                out_values = [daily_data[date]['out'] for date in sorted_dates]
                
                # 创建折线图
                x_pos = np.arange(len(sorted_dates))
                line_in, = self.ax.plot(x_pos, in_values, 'g-o', label='入库')
                line_out, = self.ax.plot(x_pos, out_values, 'r--s', label='出库')
                
                self.ax.set_xticks(x_pos)
                self.ax.set_xticklabels(sorted_dates, rotation=45, ha='right')
                self.ax.set_ylabel('数量')
                self.ax.set_title(f'近{days}天出入库趋势')
                self.ax.legend()
                self.ax.grid(True, linestyle='--', alpha=0.7)
                
                # 添加数据标签
                for i, v in enumerate(in_values):
                    self.ax.text(i, v + max(in_values + out_values) * 0.02, 
                                str(v), color='green', ha='center')
                
                for i, v in enumerate(out_values):
                    self.ax.text(i, v + max(in_values + out_values) * 0.02, 
                                str(v), color='red', ha='center')
            
            self.fig.tight_layout()
            self.draw()
        except Exception as e:
            self.logger.error(f"绘制出入库趋势图失败: {e}")

if __name__ == "__main__":
    # 测试代码（需要PyQt环境）
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("库存图表测试")
            self.setGeometry(100, 100, 1000, 800)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            self.chart = InventoryChart(self, width=10, height=8)
            layout.addWidget(self.chart)
            
            btn_layout = QVBoxLayout()
            
            btn1 = QPushButton("显示库存TOP10")
            btn1.clicked.connect(lambda: self.chart.plot_stock_levels(10))
            
            btn2 = QPushButton("显示类别分布")
            btn2.clicked.connect(self.chart.plot_category_distribution)
            
            btn3 = QPushButton("显示类别库存")
            btn3.clicked.connect(self.chart.plot_stock_value_by_category)
            
            btn4 = QPushButton("显示出入库趋势")
            btn4.clicked.connect(lambda: self.chart.plot_in_out_trend(14))
            
            btn_layout.addWidget(btn1)
            btn_layout.addWidget(btn2)
            btn_layout.addWidget(btn3)
            btn_layout.addWidget(btn4)
            
            layout.addLayout(btn_layout)
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())