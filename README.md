# 智能商品库存管理系统

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.x+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

智能商品库存管理系统是一款基于 Python 开发的桌面应用程序，旨在帮助企业高效管理商品库存，提供库存监控、出入库操作、报表生成和数据分析等功能。系统支持中文显示，界面友好，操作简便，适合各类中小型仓库或零售店铺使用。

## 功能特点

### 📦 商品管理
- 支持商品信息的添加、编辑、查询和删除
- 记录商品名称、类别、规格、供应商等详细信息
- 支持按多维度筛选和搜索商品

### 📊 库存操作
- 记录商品入库、出库和库存调整等操作
- 自动更新库存数量，确保数据实时准确
- 操作记录可追溯，支持历史查询

### 🔍 条形码扫描
- 通过摄像头实时扫描条形码
- 快速识别商品信息，减少手动输入错误
- 支持主流条形码格式识别

### ⚠️ 库存预警
- 自动检测低库存商品并发出预警
- 可自定义库存预警阈值
- 支持预警信息导出

### 📑 数据报表
- 生成库存报表和交易记录报表
- 支持 PDF 格式导出
- 报表支持自定义时间范围和筛选条件

### 📈 数据分析
- 提供库存统计图表可视化展示
- 包括库存 TOP 商品、类别分布、库存价值分析等
- 图表支持导出为图片格式

### 👤 用户管理
- 支持多角色用户（管理员、库管员、普通用户）
- 权限分明，细粒度控制操作权限
- 支持用户密码重置和权限修改

## 技术栈

| 类别 | 技术 |
|------|------|
| 编程语言 | Python 3.8+ |
| GUI 框架 | PyQt5 |
| 数据库 | SQLite（轻量级嵌入式数据库） |
| 报表生成 | ReportLab |
| 图表绘制 | Matplotlib |
| 条形码识别 | pyzbar、OpenCV |
| 打包工具 | PyInstaller |

## 安装与使用

### 开发环境运行

1. 克隆本仓库到本地
   ```bash
   git clone https://github.com/yourusername/inventory-management-system.git
   cd inventory-management-system
   ```

2. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```

3. 运行主程序
   ```bash
   python main.py
   ```

### 生产环境运行

1. 执行打包脚本
   ```bash
   python build.py
   ```

2. 打包完成后，在 `dist` 目录下会生成可执行文件 `InventoryManager.exe`

3. 双击可执行文件即可运行

## 目录结构

```
inventory-management-system/
├── main_window.py        # 主窗口界面
├── product_tab.py        # 商品管理模块
├── inventory_tab.py      # 库存操作模块
├── report_generator.py   # 报表生成模块
├── charts.py             # 数据图表绘制
├── barcode_scanner.py    # 条形码扫描功能
├── user_manager.py       # 用户管理功能
├── ui_improvements.py    # 仪表盘界面
├── build.py              # 打包配置脚本
├── requirements.txt      # 项目依赖
├── resources/            # 资源文件（图标、字体等）
└── database/             # 数据库文件
```

## 使用说明

1. **登录系统**：使用分配的账号密码登录，不同角色拥有不同操作权限
2. **添加商品**：在 "商品管理" 标签页中点击 "添加商品"，填写商品信息
3. **库存操作**：在 "库存操作" 标签页中进行入库、出库操作
4. **生成报表**：管理员可以在 "报表管理" 标签页生成各类统计报表
5. **查看仪表盘**：通过 "视图" 菜单打开仪表盘，查看库存统计数据和图表

## 注意事项

- 首次运行时会自动创建数据库文件
- 条形码扫描功能需要摄像头支持
- 报表生成和图表显示已支持中文显示
- 程序运行需要系统权限访问摄像头和文件系统
- 建议定期备份数据库文件（位于 `database/` 目录下）
- Windows 系统可能需要安装 [Visual C++ 运行库](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- 条形码扫描功能需要安装 OpenCV 依赖的系统库

## 常见问题

### Q1: 运行时提示缺少依赖？
A1: 请确保使用 Python 3.8+ 版本，并执行 `pip install -r requirements.txt` 安装所有依赖。

### Q2: 摄像头无法启动？
A2: 请检查系统摄像头权限设置，并确保没有其他程序占用摄像头。

### Q3: 中文显示乱码？
A3: 程序已内置中文字体支持，如仍有问题，请检查系统字体设置。

### Q4: 打包后的程序无法运行？
A4: 请确保在打包时使用与目标系统匹配的 Python 版本和依赖库版本。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。对于重大更改，请先开 Issue 讨论您想要改变的内容。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：your-email@example.com
- GitHub：[@yourusername](https://github.com/yourusername)
