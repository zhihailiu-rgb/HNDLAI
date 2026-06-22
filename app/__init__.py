# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app(config_name="default"):
    app = Flask(__name__)
    from config import config_map
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    CORS(app)
    db.init_app(app)

    # 注册蓝图
    from app.routes.dashboard import dashboard_bp
    from app.routes.projects import projects_bp
    from app.routes.data import data_bp
    from app.routes.index_mgr import index_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(index_bp)

    # 创建表
    with app.app_context():
        from app.models import (Province, City, ProjectType, WorkerType,
                                 Project, LaborPrice, QuotaBase, IndexResult)
        db.create_all()

    return app
