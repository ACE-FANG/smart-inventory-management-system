import os
import sys
import sqlite3
import logging
from datetime import datetime

# 导入动态路径获取函数
from database import get_db_path

class UserManager:
    def __init__(self):
        # 使用动态路径获取数据库位置
        self.db_path = get_db_path()
        self.logger = logging.getLogger('user_manager')
        self.logger.info(f"数据库路径: {self.db_path}")
        
        # 检查数据库文件是否存在
        if not os.path.exists(self.db_path):
            self.logger.error(f"数据库文件不存在: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # 启用外键约束
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
    
    def authenticate(self, username, password):
        """用户认证"""
        try:
            self.logger.debug(f"尝试认证用户: {username}")
            self.cursor.execute(
                "SELECT id, role FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = self.cursor.fetchone()
            
            if user:
                self.logger.info(f"用户 {username} 认证成功")
            else:
                self.logger.warning(f"用户 {username} 认证失败，用户名或密码错误")
                
            return user if user else None
        except Exception as e:
            self.logger.error(f"用户认证过程发生错误: {e}", exc_info=True)
            return None
    
    def add_user(self, username, password, role):
        """添加新用户"""
        try:
            self.logger.info(f"添加新用户: {username} (角色: {role})")
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            self.logger.warning(f"用户名已存在: {username}")
            return "username_exists"
        except Exception as e:
            self.logger.error(f"添加用户失败: {e}", exc_info=True)
            return None
    
    def update_user(self, user_id, **kwargs):
        """更新用户信息"""
        if not kwargs:
            self.logger.warning(f"未提供更新字段，用户ID: {user_id}")
            return False
        
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(user_id)
        
        try:
            self.logger.info(f"更新用户ID {user_id} 的信息")
            self.cursor.execute(f'''
            UPDATE users 
            SET {set_clause}
            WHERE id = ?
            ''', values)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"更新用户失败: {e}", exc_info=True)
            return False
    
    def delete_user(self, user_id):
        """删除用户"""
        try:
            self.logger.info(f"删除用户ID: {user_id}")
            
            # 删除与该用户相关的审计日志
            self.cursor.execute("DELETE FROM audit_logs WHERE user_id = ?", (user_id,))
            
            # 假设库存历史表名为 inventory_history，确保该表存在
            # 如果表名不同，请修改此处
            self.cursor.execute("DELETE FROM inventory_history WHERE operator_id = ?", (user_id,))
            
            # 删除用户
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
            
            rows_affected = self.cursor.rowcount
            if rows_affected > 0:
                self.logger.info(f"成功删除 {rows_affected} 个用户记录")
            else:
                self.logger.warning(f"未找到用户ID: {user_id}")
                
            return rows_affected > 0
        except Exception as e:
            self.logger.error(f"删除用户失败: {e}", exc_info=True)
            return False
    
    def get_all_users(self):
        """获取所有用户"""
        try:
            self.logger.debug("获取所有用户列表")
            self.cursor.execute("SELECT id, username, role FROM users")
            users = self.cursor.fetchall()
            
            if users:
                columns = [col[0] for col in self.cursor.description]
                result = [dict(zip(columns, row)) for row in users]
                self.logger.info(f"获取到 {len(result)} 个用户")
                return result
            else:
                self.logger.warning("用户表为空")
                return []
        except Exception as e:
            self.logger.error(f"获取用户列表失败: {e}", exc_info=True)
            return []
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户信息"""
        try:
            self.logger.debug(f"获取用户ID: {user_id} 的信息")
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = self.cursor.fetchone()
            
            if user:
                columns = [col[0] for col in self.cursor.description]
                result = dict(zip(columns, user))
                self.logger.info(f"获取到用户: {result['username']}")
                return result
            else:
                self.logger.warning(f"未找到用户ID: {user_id}")
                return None
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {e}", exc_info=True)
            return None
    
    def change_user_id(self, old_id, new_id):
        """更改用户ID"""
        try:
            self.logger.info(f"将用户ID从 {old_id} 更改为 {new_id}")
            
            # 删除与该用户相关的审计日志
            self.cursor.execute("DELETE FROM audit_logs WHERE user_id = ?", (old_id,))
            
            # 删除与该用户相关的库存历史记录
            self.cursor.execute("DELETE FROM inventory_history WHERE operator_id = ?", (old_id,))
            
            # 获取用户信息
            user = self.get_user_by_id(old_id)
            if user:
                username = user['username']
                password = user['password']
                role = user['role']
                
                # 删除旧用户
                self.delete_user(old_id)
                
                # 插入新用户，指定ID
                self.cursor.execute(
                    "INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)", 
                    (new_id, username, password, role)
                )
                self.conn.commit()
                self.logger.info(f"用户ID已成功从 {old_id} 更改为 {new_id}")
                return True
            else:
                self.logger.warning(f"未找到用户ID: {old_id}")
                return False
        except Exception as e:
            self.logger.error(f"更改用户ID失败: {e}", exc_info=True)
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.logger.info("数据库连接已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    # 测试代码
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 如果数据库不存在则初始化
    from database import init_database, get_db_path
    db_path = get_db_path()
    if not os.path.exists(db_path):
        logging.info(f"数据库不存在，开始初始化: {db_path}")
        init_database()
    
    with UserManager() as manager:
        # 测试认证
        user = manager.authenticate("admin", "admin123")
        print(f"认证结果: {user}")
        
        # 添加新用户
        user_id = manager.add_user("store_keeper", "password123", "store_keeper")
        print(f"添加的仓库管理员ID: {user_id}")
        
        user_id = manager.add_user("sales_user", "sales123", "sales")
        print(f"添加的销售员ID: {user_id}")
        
        # 获取用户列表
        users = manager.get_all_users()
        print(f"用户列表: {users}")

        # 获取 sales_user 的用户ID
        sales_user = None
        for user in users:
            if user['username'] == 'sales_user':
                sales_user = user
                break

        if sales_user:
            # 更改 sales_user 的ID为2
            result = manager.change_user_id(sales_user['id'], 2)
            if result:
                print(f"成功将 sales_user 的ID改为2")
            else:
                print(f"更改 sales_user 的ID失败")
        else:
            print("未找到 sales_user 用户")

        # 获取更新后的用户列表
        users = manager.get_all_users()
        print(f"更新后的用户列表: {users}")
