import sqlite3
import logging
from datetime import datetime, timedelta

class AuditLogger:
    def __init__(self, db_path='inventory.db'):
        """
        初始化审计日志记录器
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.logger = logging.getLogger('audit_logger')
        
        # 创建审计日志表（如果不存在）
        self._create_table()
    
    def _create_table(self):
        """创建审计日志表"""
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"创建审计日志表失败: {e}")
    
    def log_action(self, user_id, action, details=None, ip_address=None):
        """
        记录审计日志
        :param user_id: 用户ID
        :param action: 操作描述
        :param details: 操作详细信息
        :param ip_address: 操作IP地址
        :return: 日志记录ID，失败返回None
        """
        try:
            self.cursor.execute('''
            INSERT INTO audit_log (user_id, action, details, ip_address)
            VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, ip_address))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.logger.error(f"记录审计日志失败: {e}")
            return None
    
    def get_audit_logs(self, user_id=None, action=None, start_date=None, end_date=None, 
                      limit=100, offset=0):
        """
        获取审计日志
        :return: 日志记录列表
        """
        query = '''
        SELECT a.*, u.username 
        FROM audit_log a
        JOIN users u ON a.user_id = u.id
        WHERE 1=1
        '''
        params = []
        
        if user_id:
            query += " AND a.user_id = ?"
            params.append(user_id)
        
        if action:
            query += " AND a.action LIKE ?"
            params.append(f"%{action}%")
        
        if start_date:
            query += " AND a.timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND a.timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY a.timestamp DESC"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        try:
            self.cursor.execute(query, params)
            logs = self.cursor.fetchall()
            
            if logs:
                columns = [col[0] for col in self.cursor.description]
                return [dict(zip(columns, row)) for row in logs]
            return []
        except Exception as e:
            self.logger.error(f"获取审计日志失败: {e}")
            return []
    
    def clear_old_logs(self, days=365):
        """
        清理旧的审计日志
        :param days: 保留天数，默认365天
        :return: 删除的记录数
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            self.cursor.execute('''
            DELETE FROM audit_log 
            WHERE timestamp < ?
            ''', (cutoff_date,))
            deleted_count = self.cursor.rowcount
            self.conn.commit()
            return deleted_count
        except Exception as e:
            self.logger.error(f"清理审计日志失败: {e}")
            return 0
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    # 测试代码
    import os
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 如果数据库不存在则初始化
    if not os.path.exists('inventory.db'):
        from database import init_database
        init_database()
    
    with AuditLogger() as logger:
        # 记录测试日志
        log_id = logger.log_action(
            user_id=1,
            action="测试操作",
            details="这是测试审计日志",
            ip_address="127.0.0.1"
        )
        print(f"记录的日志ID: {log_id}")
        
        # 获取日志
        logs = logger.get_audit_logs()
        print(f"审计日志: {logs}")
        
        # 清理日志（测试环境慎用）
        # deleted_count = logger.clear_old_logs(days=0)
        # print(f"删除的日志数量: {deleted_count}")