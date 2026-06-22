# 海南省建设工程定额人工费调整指数管理系统

## 快速开始

### 环境要求
- Python 3.8+
- pip（Python 包管理器）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/zhihailiu-rgb/HNDLAI.git
cd HNDLAI

# 2. 安装依赖
pip install flask flask-sqlalchemy pymysql flask-cors

# 3. 启动系统
python run.py
```

### 访问系统
打开浏览器访问 **http://127.0.0.1:5000**

系统已预置海南省的模拟数据（12个项目、3240条价格记录、1080条指数结果），可直接体验。

## 功能模块

| 模块 | 功能 |
|------|------|
| 仪表盘 | 综合指数趋势图、各工种/城市均价对比、工程类型分布 |
| 项目管理 | 工程项目的新增、编辑、删除 |
| 数据管理 | 劳务市场价格录入、审核、趋势分析 |
| 指数管理 | 一键计算指数（A = Pa/Pj × 100）、指数发布 |

## 切换 MySQL 数据库

```bash
# 设置环境变量
set DB_TYPE=mysql
set MYSQL_USER=root
set MYSQL_PASS=your_password

# 启动
python run.py
```

## 技术栈

- 后端：Flask + SQLAlchemy
- 前端：Bootstrap 5 + ECharts
- 数据库：SQLite（开发）/ MySQL（生产）
