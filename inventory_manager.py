import sqlite3
import logging
from datetime import datetime
from audit_logger import AuditLogger

class InventoryManager:
    def __init__(self, db_path='inventory.db'):
        """
        初始化库存管理器
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.logger = logging.getLogger('inventory_manager')
        self.audit_logger = AuditLogger(db_path)
        
        # 启用外键约束
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
    
    def add_product(self, operator_id, name, category, specification, supplier, location, 
                   barcode=None, image_path=None, min_stock=5):
        """
        添加新商品
        :return: 添加成功返回商品ID，失败返回None
        """
        try:
            self.cursor.execute('''
            INSERT INTO products (name, category, specification, supplier, location, 
                                barcode, image_path, min_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, specification, supplier, location, 
                 barcode, image_path, min_stock))
            self.conn.commit()
            product_id = self.cursor.lastrowid
            self.audit_logger.log_action(operator_id, f"添加商品，商品ID: {product_id}", 
                                         details=f"商品名称: {name}, 类别: {category}", 
                                         ip_address="N/A")
            return product_id
        except sqlite3.IntegrityError as e:
            self.logger.error(f"添加商品失败: {e}")
            if "UNIQUE constraint failed: products.barcode" in str(e):
                return "barcode_exists"
            return None
        except Exception as e:
            self.logger.error(f"添加商品失败: {e}")
            return None
    
    def update_product(self, operator_id, product_id, **kwargs):
        """
        更新商品信息
        :param product_id: 商品ID
        :param kwargs: 需要更新的字段和值
        :return: 更新成功返回True，失败返回False
        """
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(product_id)
        
        try:
            # 获取更新前的商品信息用于审计日志
            old_product = self.get_product_by_id(product_id)
            
            self.cursor.execute(f'''
            UPDATE products 
            SET {set_clause}
            WHERE id = ?
            ''', values)
            self.conn.commit()
            success = self.cursor.rowcount > 0
            
            if success:
                # 获取更新后的商品信息
                new_product = self.get_product_by_id(product_id)
                
                # 生成变更详情
                changes = []
                for key, new_value in kwargs.items():
                    old_value = old_product.get(key)
                    if old_value != new_value:
                        changes.append(f"{key}: {old_value} → {new_value}")
                
                if changes:
                    details = " | ".join(changes)
                    self.audit_logger.log_action(operator_id, f"更新商品，商品ID: {product_id}", 
                                                details=details, ip_address="N/A")
            return success
        except Exception as e:
            self.logger.error(f"更新商品失败: {e}")
            return False
    
    def delete_product(self, operator_id, product_id):
        """
        删除商品
        :param product_id: 商品ID
        :return: 删除成功返回True，失败返回False
        """
        try:
            # 先删除相关库存历史记录
            self.cursor.execute('''
            DELETE FROM inventory_history 
            WHERE product_id = ?
            ''', (product_id,))
            
            # 再删除商品
            self.cursor.execute('''
            DELETE FROM products 
            WHERE id = ?
            ''', (product_id,))
            self.conn.commit()
            success = self.cursor.rowcount > 0
            if success:
                self.audit_logger.log_action(operator_id, f"删除商品，商品ID: {product_id}", 
                                             ip_address="N/A")
            return success
        except Exception as e:
            self.logger.error(f"删除商品失败: {e}")
            self.conn.rollback()
            return False
    
    def get_product_by_id(self, product_id):
        """
        根据ID获取商品信息
        :return: 商品信息字典，未找到返回None
        """
        try:
            self.cursor.execute('''
            SELECT * FROM products 
            WHERE id = ?
            ''', (product_id,))
            product = self.cursor.fetchone()
            
            if product:
                columns = [col[0] for col in self.cursor.description]
                return dict(zip(columns, product))
            return None
        except Exception as e:
            self.logger.error(f"获取商品信息失败: {e}")
            return None
    
    def search_products(self, search_term=None, category=None, barcode=None, 
                       supplier=None, location=None, min_stock=None):
        """
        搜索商品
        :return: 匹配的商品列表
        """
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR specification LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if barcode:
            query += " AND barcode = ?"
            params.append(barcode)
        
        if supplier:
            query += " AND supplier LIKE ?"
            params.append(f"%{supplier}%")
        
        if location:
            query += " AND location = ?"
            params.append(location)
        
        if min_stock is not None:
            query += " AND stock <= min_stock"
        
        try:
            self.cursor.execute(query, params)
            products = self.cursor.fetchall()
            
            if products:
                columns = [col[0] for col in self.cursor.description]
                return [dict(zip(columns, row)) for row in products]
            return []
        except Exception as e:
            self.logger.error(f"搜索商品失败: {e}")
            return []
    
    def update_stock(self, operator_id, product_id, change_amount, operation_type, notes=None):
        """
        更新库存数量
        :param product_id: 商品ID
        :param change_amount: 变动数量
        :param operation_type: 操作类型 ('in'入库 / 'out'出库)
        :param operator_id: 操作员ID
        :param notes: 备注信息
        :return: 操作成功返回True，失败返回False
        """
        if operation_type not in ('in', 'out'):
            self.logger.error(f"无效的操作类型: {operation_type}")
            return False
        
        if change_amount <= 0:
            self.logger.error("变动数量必须大于0")
            return False
        
        try:
            # 更新库存数量
            self.cursor.execute('''
            UPDATE products 
            SET stock = stock + ? 
            WHERE id = ?
            ''', (change_amount if operation_type == 'in' else -change_amount, product_id))
            
            # 检查库存是否变为负数
            self.cursor.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
            current_stock = self.cursor.fetchone()[0]
            
            if current_stock < 0:
                self.conn.rollback()
                self.logger.error("库存数量不能为负数")
                return False
            
            # 记录库存历史
            self.cursor.execute('''
            INSERT INTO inventory_history (product_id, change_amount, operation_type, 
                                          operator_id, operation_time, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (product_id, change_amount, operation_type, operator_id, 
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notes))
            
            self.conn.commit()
            action = f"{'入库' if operation_type == 'in' else '出库'} 商品，商品ID: {product_id}, 变动数量: {change_amount}"
            self.audit_logger.log_action(operator_id, action, details=notes, ip_address="N/A")
            return True
        except Exception as e:
            self.logger.error(f"更新库存失败: {e}")
            self.conn.rollback()
            return False
    
    def get_inventory_history(self, product_id=None, operator_id=None, 
                             start_date=None, end_date=None, operation_type=None):
        """
        获取库存历史记录
        :return: 库存历史记录列表
        """
        query = '''
        SELECT h.*, p.name as product_name, u.username as operator_name 
        FROM inventory_history h
        JOIN products p ON h.product_id = p.id
        JOIN users u ON h.operator_id = u.id
        WHERE 1=1
        '''
        params = []
        
        if product_id:
            query += " AND h.product_id = ?"
            params.append(product_id)
        
        if operator_id:
            query += " AND h.operator_id = ?"
            params.append(operator_id)
        
        if operation_type:
            query += " AND h.operation_type = ?"
            params.append(operation_type)
        
        if start_date:
            query += " AND h.operation_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND h.operation_time <= ?"
            params.append(end_date)
        
        query += " ORDER BY h.operation_time DESC"
        
        try:
            self.cursor.execute(query, params)
            history = self.cursor.fetchall()
            
            if history:
                columns = [col[0] for col in self.cursor.description]
                return [dict(zip(columns, row)) for row in history]
            return []
        except Exception as e:
            self.logger.error(f"获取库存历史失败: {e}")
            return []
    
    def get_low_stock_products(self):
        """
        获取低库存商品
        :return: 低库存商品列表
        """
        try:
            self.cursor.execute('''
            SELECT * FROM products 
            WHERE stock <= min_stock
            ''')
            products = self.cursor.fetchall()
            
            if products:
                columns = [col[0] for col in self.cursor.description]
                return [dict(zip(columns, row)) for row in products]
            return []
        except Exception as e:
            self.logger.error(f"获取低库存商品失败: {e}")
            return []
    
    def get_all_categories(self):
        """
        获取所有商品类别
        :return: 类别列表
        """
        try:
            self.cursor.execute('''
            SELECT DISTINCT category FROM products
            ''')
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取商品类别失败: {e}")
            return []
    
    def get_all_locations(self):
        """
        获取所有库存位置
        :return: 位置列表
        """
        try:
            self.cursor.execute('''
            SELECT DISTINCT location FROM products
            ''')
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取库存位置失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
        self.audit_logger.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    # 测试代码
    import os
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 如果数据库不存在则初始化
    if not os.path.exists('inventory.db'):
        from database import init_database
        init_database()
    
    with InventoryManager() as manager:
        # 添加测试商品
        product_id = manager.add_product(
            operator_id=1,
            name="测试商品",
            category="测试类别",
            specification="规格说明",
            supplier="测试供应商",
            location="A-001",
            barcode="123456789012",
            min_stock=10
        )
        
        print(f"添加的商品ID: {product_id}")
        
        # 更新库存
        manager.update_stock(1, product_id, 100, 'in', "初始入库")
        
        # 查询商品
        product = manager.get_product_by_id(product_id)
        print(f"商品信息: {product}")
        
        # 搜索商品
        products = manager.search_products(search_term="测试")
        print(f"搜索结果: {products}")
        
        # 获取库存历史
        history = manager.get_inventory_history(product_id=product_id)
        print(f"库存历史: {history}")
        
        # 获取低库存商品
        low_stock = manager.get_low_stock_products()
        print(f"低库存商品: {low_stock}")