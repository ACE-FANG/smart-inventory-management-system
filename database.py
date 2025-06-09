# database.py
import os
import sys
import sqlite3

def get_db_path():
    """获取数据库路径（兼容打包后的环境）"""
    # 打包后，使用临时目录（_MEIPASS）
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        # 开发环境下，使用当前脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'inventory.db')

def init_database():
    """初始化数据库结构"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # 创建产品表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        category TEXT,
        barcode TEXT UNIQUE,
        image_path TEXT
    )
    ''')
    
    # 创建订单表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        order_date TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 创建订单明细表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    # 创建审计日志表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY,
        timestamp TEXT NOT NULL,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 添加默认管理员用户（仅当用户表为空时）
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ('admin', 'admin123', 'admin'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ('sales', 'sales123', 'sales'))
    
    conn.commit()
    conn.close()
    print(f"数据库初始化成功: {db_path}")

# 确保直接运行 database.py 时也能初始化数据库
if __name__ == "__main__":
    init_database()