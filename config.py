# -*- coding: utf-8 -*-
"""
应用配置模块
开发环境使用 SQLite，生产环境切换至 MySQL
"""
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "hn-labor-index-secret-key-2026")

    # ========== 数据库配置 ==========
    # 默认使用 SQLite（立即可用，无需安装 MySQL）
    # 生产环境切换为 MySQL 只需修改下方 URI
    DB_TYPE = os.environ.get("DB_TYPE", "sqlite")  # sqlite | mysql

    if DB_TYPE == "mysql":
        # MySQL 配置（需要先安装 MySQL 并创建数据库）
        MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
        MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
        MYSQL_USER = os.environ.get("MYSQL_USER", "root")
        MYSQL_PASS = os.environ.get("MYSQL_PASS", "root")
        MYSQL_DB = os.environ.get("MYSQL_DB", "hainan_labor_index")
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
            "?charset=utf8mb4"
        )
    else:
        # SQLite 开发环境
        db_path = os.path.join(BASEDIR, "data.db")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # JSON 中文支持
    JSON_AS_ASCII = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    DB_TYPE = os.environ.get("DB_TYPE", "mysql")
    SQLALCHEMY_ECHO = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
