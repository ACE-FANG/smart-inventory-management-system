# 系统配置常量
class Config:
    # 数据库配置
    DB_PATH = "inventory.db"
    
    # 路径配置
    IMAGE_DIR = "images"
    REPORT_DIR = "reports"
    
    # 默认用户角色
    ROLES = {
        "admin": "管理员",
        "store_keeper": "仓库管理员",
        "sales": "销售员"
    }
    
    # 日志配置
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "inventory_system.log"
    
    # 条形码扫描配置
    SCANNER_TIMEOUT = 30  # 秒
    
    # 库存预警配置
    LOW_STOCK_COLOR = "#FF6347"  # Tomato
    NORMAL_STOCK_COLOR = "#32CD32"  # LimeGreen
    
    # 报表配置
    REPORT_TITLE = "智能商品库存管理系统报告"
    
    @staticmethod
    def get_role_name(role_code):
        """获取角色名称"""
        return Config.ROLES.get(role_code, "未知角色")