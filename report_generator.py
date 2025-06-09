import os
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from inventory_manager import InventoryManager
from audit_logger import AuditLogger

class ReportGenerator:
    def __init__(self, output_dir):
        """
        初始化报表生成器
        :param output_dir: 报表输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 创建样式表
        self.styles = getSampleStyleSheet()

        # 注册中文字体（必须在创建样式前调用）
        self._register_chinese_fonts()

        # 添加自定义样式，避免KeyError
        self._add_style_safe('TableHeader', ParagraphStyle(
            name='TableHeader',
            fontName='ChineseFont',
            fontSize=10,
            alignment=1,
            textColor=colors.white,
            spaceBefore=6,
            spaceAfter=6
        ))
        self._add_style_safe('TableCell', ParagraphStyle(
            name='TableCell',
            fontName='ChineseFont',
            fontSize=9,
            spaceBefore=3,
            spaceAfter=3
        ))
        self._add_style_safe('ChineseTitle', ParagraphStyle(
            name='ChineseTitle',
            fontName='ChineseFont',
            fontSize=18,
            alignment=1,  # 居中
            spaceAfter=12
        ))
        self._add_style_safe('ChineseHeading1', ParagraphStyle(
            name='ChineseHeading1',
            fontName='ChineseFont',
            fontSize=14,
            alignment=0,  # 左对齐
            spaceBefore=12,
            spaceAfter=6
        ))
        self._add_style_safe('ChineseNormal', ParagraphStyle(
            name='ChineseNormal',
            fontName='ChineseFont',
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6
        ))
        # 覆盖默认样式
        self._override_default_styles()

    def _register_chinese_fonts(self):
        """确保中文字体100%生效的终极方案"""
        try:
            # 使用相对路径确保字体文件位置正确
            base_dir = os.path.dirname(os.path.abspath(__file__))
            font_dir = os.path.join(base_dir, 'resources', 'fonts')
            font_path = os.path.join(font_dir, 'SimHei.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                print(f"使用黑体字体: {font_path}")
                return
            font_path = os.path.join(font_dir, 'simsun.ttc')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                print(f"使用宋体字体: {font_path} (索引0)")
                return
            linux_font = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
            if os.path.exists(linux_font):
                pdfmetrics.registerFont(TTFont('ChineseFont', linux_font))
                print(f"使用Linux系统字体: {linux_font}")
                return
            raise FileNotFoundError("无可用中文字体文件")
        except Exception as e:
            print(f"字体注册失败: {str(e)}")
            # 最终回退（可能显示方块）
            pdfmetrics.registerFont(TTFont('ChineseFont', 'Helvetica'))
            print("警告: 使用Helvetica字体，中文可能显示为方块")

    def _add_style_safe(self, style_name, style_obj):
        """安全地添加样式，避免重复"""
        if style_name not in self.styles:
            self.styles.add(style_obj)

    def _override_default_styles(self):
        """显式覆盖默认样式的中文字体设置"""
        base_styles = ['Title', 'Heading1', 'Normal', 'Heading2', 'Heading3']
        for style in base_styles:
            if style in self.styles:
                self.styles[style].fontName = 'ChineseFont'

    def generate_inventory_report(self, operator_id, products=None, start_date=None, end_date=None):
        """
        生成库存报表（已支持中文）
        :param operator_id: 操作员ID
        :param products: 商品列表
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 生成的报表文件路径
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inventory_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        # 标题
        story.append(Paragraph("库存管理系统 - 库存报表", self.styles['Title']))

        # 报表信息
        report_info = [
            f"生成日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"生成人: {operator_id}"
        ]
        if start_date:
            report_info.append(f"开始日期: {start_date}")
        if end_date:
            report_info.append(f"结束日期: {end_date}")
        for info in report_info:
            story.append(Paragraph(info, self.styles['Normal']))
        story.append(Spacer(1, 0.25*inch))

        with InventoryManager() as manager:
            if products is None:
                products = manager.search_products()
            table_data = [
                [
                    Paragraph("商品ID", self.styles['TableHeader']),
                    Paragraph("商品名称", self.styles['TableHeader']),
                    Paragraph("类别", self.styles['TableHeader']),
                    Paragraph("库存位置", self.styles['TableHeader']),
                    Paragraph("当前库存", self.styles['TableHeader']),
                    Paragraph("最低库存", self.styles['TableHeader']),
                    Paragraph("状态", self.styles['TableHeader'])
                ]
            ]
            for product in products:
                status = "正常" if product['stock'] > product['min_stock'] else "低库存"
                table_data.append([
                    Paragraph(str(product['id']), self.styles['TableCell']),
                    Paragraph(product['name'], self.styles['TableCell']),
                    Paragraph(product['category'], self.styles['TableCell']),
                    Paragraph(product['location'], self.styles['TableCell']),
                    Paragraph(str(product['stock']), self.styles['TableCell']),
                    Paragraph(str(product['min_stock']), self.styles['TableCell']),
                    Paragraph(status, self.styles['TableCell'])
                ])
            table = Table(table_data, colWidths=[0.7*inch, 2*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)

            story.append(Spacer(1, 0.25*inch))
            story.append(Paragraph("库存统计信息", self.styles['Heading1']))

            total_products = len(products)
            low_stock_products = sum(1 for p in products if p['stock'] <= p['min_stock'])

            stats_data = [
                [Paragraph("商品总数", self.styles['TableCell']), Paragraph(str(total_products), self.styles['TableCell'])],
                [Paragraph("低库存商品数", self.styles['TableCell']), Paragraph(str(low_stock_products), self.styles['TableCell'])],
                [Paragraph("低库存比例", self.styles['TableCell']), Paragraph(f"{(low_stock_products/total_products)*100:.2f}%" if total_products > 0 else "0%", self.styles['TableCell'])]
            ]
            stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(stats_table)

        doc.build(story)

        # 记录审计日志
        logger = AuditLogger()
        logger.log_action(
            operator_id,
            "生成库存报表",
            details=f"报表文件: {filename}",
            ip_address="N/A"
        )

        return filepath

    def generate_transaction_report(self, operator_id, transactions=None, start_date=None, end_date=None):
        """
        生成交易记录报表（已支持中文）
        :param operator_id: 操作员ID
        :param transactions: 交易记录列表
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 生成的报表文件路径
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transaction_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        story.append(Paragraph("库存管理系统 - 交易记录报表", self.styles['Title']))

        report_info = [
            f"生成日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"生成人: {operator_id}"
        ]
        if start_date:
            report_info.append(f"开始日期: {start_date}")
        if end_date:
            report_info.append(f"结束日期: {end_date}")
        for info in report_info:
            story.append(Paragraph(info, self.styles['Normal']))
        story.append(Spacer(1, 0.25*inch))

        with InventoryManager() as manager:
            if transactions is None:
                transactions = manager.get_inventory_history(
                    start_date=start_date,
                    end_date=end_date
                )
            table_data = [
                [
                    Paragraph("交易ID", self.styles['TableHeader']),
                    Paragraph("商品ID", self.styles['TableHeader']),
                    Paragraph("商品名称", self.styles['TableHeader']),
                    Paragraph("操作类型", self.styles['TableHeader']),
                    Paragraph("变动数量", self.styles['TableHeader']),
                    Paragraph("操作员", self.styles['TableHeader']),
                    Paragraph("操作时间", self.styles['TableHeader']),
                    Paragraph("备注", self.styles['TableHeader'])
                ]
            ]
            for transaction in transactions:
                op_type = "入库" if transaction['operation_type'] == 'in' else "出库"
                table_data.append([
                    Paragraph(str(transaction['id']), self.styles['TableCell']),
                    Paragraph(str(transaction['product_id']), self.styles['TableCell']),
                    Paragraph(transaction['product_name'], self.styles['TableCell']),
                    Paragraph(op_type, self.styles['TableCell']),
                    Paragraph(str(transaction['change_amount']), self.styles['TableCell']),
                    Paragraph(transaction['operator_name'], self.styles['TableCell']),
                    Paragraph(transaction['operation_time'], self.styles['TableCell']),
                    Paragraph(transaction['notes'] or "", self.styles['TableCell'])
                ])
            table = Table(table_data, colWidths=[0.7*inch, 0.7*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)

        doc.build(story)

        logger = AuditLogger()
        logger.log_action(
            operator_id,
            "生成交易记录报表",
            details=f"报表文件: {filename}",
            ip_address="N/A"
        )

        return filepath