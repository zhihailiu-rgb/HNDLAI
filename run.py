# -*- coding: utf-8 -*-
from app import create_app
app = create_app("development")
if __name__ == "__main__":
    print("=" * 60)
    print("  海南省建设工程定额人工费调整指数管理系统")
    print("=" * 60)
    print("  启动地址: http://127.0.0.1:5000")
    print("  数据库: SQLite (开发模式)")
    print("  切换 MySQL: 设置环境变量 DB_TYPE=mysql")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
