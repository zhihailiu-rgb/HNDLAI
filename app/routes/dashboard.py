# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import func, extract
from app import db
from app.models import (Province, City, ProjectType, WorkerType,
                         Project, LaborPrice, QuotaBase, IndexResult)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/")


@dashboard_bp.route("/")
def index():
    """仪表盘页面"""
    return render_template("dashboard.html")


@dashboard_bp.route("/api/dashboard/stats")
def dashboard_stats():
    """仪表盘统计数据"""
    # 基本统计
    project_count = Project.query.count()
    price_count = LaborPrice.query.count()
    index_count = IndexResult.query.count()

    # 最近一期综合指数
    latest_index = IndexResult.query.order_by(
        IndexResult.year.desc(), IndexResult.quarter.desc()
    ).first()
    latest_index_val = round(latest_index.index_value, 2) if latest_index else None
    latest_period = f"{latest_index.year}年第{latest_index.quarter}季度" if latest_index else "暂无"

    # 各工种平均价格
    worker_avg = db.session.query(
        WorkerType.name, func.avg(LaborPrice.unit_price).label("avg_price")
    ).join(LaborPrice, WorkerType.id == LaborPrice.worker_type_id
    ).group_by(WorkerType.id, WorkerType.name).all()

    worker_prices = [{"name": w.name, "avg_price": round(float(w.avg_price), 2)} for w in worker_avg]

    # 各城市平均价格
    city_avg = db.session.query(
        City.name, func.avg(LaborPrice.unit_price).label("avg_price")
    ).join(Project, Project.city_id == City.id
    ).join(LaborPrice, LaborPrice.project_id == Project.id
    ).group_by(City.id, City.name).all()

    city_prices = [{"name": c.name, "avg_price": round(float(c.avg_price), 2)} for c in city_avg]

    # 按季度的综合指数趋势
    index_trend = db.session.query(
        IndexResult.year, IndexResult.quarter,
        func.avg(IndexResult.index_value).label("avg_index")
    ).group_by(IndexResult.year, IndexResult.quarter
    ).order_by(IndexResult.year, IndexResult.quarter).all()

    trend_data = []
    for t in index_trend:
        trend_data.append({
            "period": f"{t.year}Q{t.quarter}",
            "index": round(float(t.avg_index), 2),
        })

    # 各工程类型数量
    type_stats = db.session.query(
        ProjectType.name, func.count(Project.id).label("count")
    ).join(Project, Project.project_type_id == ProjectType.id
    ).group_by(ProjectType.id, ProjectType.name).all()

    project_types = [{"name": t.name, "count": t.count} for t in type_stats]

    return jsonify({
        "project_count": project_count,
        "price_count": price_count,
        "index_count": index_count,
        "latest_index": latest_index_val,
        "latest_period": latest_period,
        "worker_prices": worker_prices,
        "city_prices": city_prices,
        "index_trend": trend_data,
        "project_types": project_types,
    })
