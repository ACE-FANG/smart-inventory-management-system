智能商品库存管理系统

项目简介

智能商品库存管理系统是一款基于 Python 开发的桌面应用程序，旨在帮助企业高效管理商品库存，提供库存监控、出入库操作、报表生成和数据分析等功能。系统支持中文显示，界面友好，操作简便，适合各类中小型仓库或零售店铺使用。

功能特点

商品管理：支持商品信息的添加、编辑、查询和删除，包括名称、类别、规格、供应商等详细信息

库存操作：记录商品入库、出库和库存调整等操作，自动更新库存数量

条形码扫描：通过摄像头实时扫描条形码，快速识别商品信息

库存预警：自动检测低库存商品并发出预警，避免缺货情况

数据报表：生成库存报表和交易记录报表，支持 PDF 格式导出

数据分析：提供库存统计图表，包括库存 TOP 商品、类别分布、库存价值分析等

用户管理：支持多角色用户（管理员、库管员、普通用户），权限分明

技术栈

类别	技术

编程语言	Python 3.8+

GUI 框架	PyQt5

数据库	SQLite（轻量级嵌入式数据库）

报表生成	ReportLab

图表绘制	Matplotlib

条形码识别	pyzbar、OpenCV

打包工具	PyInstaller

安装与使用

开发环境运行

克隆本仓库到本地

bash

git clone https://github.com/yourusername/inventory-management-system.git
cd inventory-management-system

安装依赖包

bash

pip install -r requirements.txt


运行主程序

bash

python main.py

生产环境运行

执行打包脚本

bash
python build.py

打包完成后，在 dist 目录下会生成可执行文件 InventoryManager.exe

双击可执行文件即可运行

目录结构

inventory-management-system/

├── main_window.py          # 主窗口界面

├── product_tab.py          # 商品管理模块

├── inventory_tab.py        # 库存操作模块

├── report_generator.py     # 报表生成模块

├── charts.py               # 数据图表绘制

├── barcode_scanner.py      # 条形码扫描功能

├── user_manager.py         # 用户管理功能

├── ui_improvements.py      # 仪表盘界面

├── build.py                # 打包配置脚本

├── requirements.txt        # 项目依赖

├── resources/              # 资源文件（图标、字体等）

└── database/               # 数据库文件
使用说明

登录系统：使用分配的账号密码登录，不同角色拥有不同操作权限

添加商品：在 "商品管理" 标签页中点击 "添加商品"，填写商品信息

库存操作：在 "库存操作" 标签页中进行入库、出库操作

生成报表：管理员可以在 "报表管理" 标签页生成各类统计报表

查看仪表盘：通过 "视图" 菜单打开仪表盘，查看库存统计数据和图表

注意事项

首次运行时会自动创建数据库文件

条形码扫描功能需要摄像头支持

报表生成和图表显示已支持中文显示

程序运行需要系统权限访问摄像头和文件系统
