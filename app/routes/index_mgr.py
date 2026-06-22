# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime, date
from app import db
from sqlalchemy import func
from app.models import (LaborPrice, QuotaBase, IndexResult,
                         WorkerType, Project, ProjectType, City)

index_bp = Blueprint("index_mgr", __name__, url_prefix="/index")


@index_bp.route("/")
def index_page():
    """指数管理页面"""
    worker_types = WorkerType.query.all()
    projects = Project.query.all()
    return render_template("index.html", worker_types=worker_types, projects=projects)


@index_bp.route("/api/results")
def list_results():
    """查询指数计算结果"""
    year = request.args.get("year", type=int)
    quarter = request.args.get("quarter", type=int)
    project_id = request.args.get("project_id", type=int)
    worker_type_id = request.args.get("worker_type_id", type=int)
    published_only = request.args.get("published_only", type=bool, default=False)

    q = IndexResult.query
    if year:
        q = q.filter_by(year=year)
    if quarter:
        q = q.filter_by(quarter=quarter)
    if project_id:
        q = q.filter_by(project_id=project_id)
    if worker_type_id:
        q = q.filter_by(worker_type_id=worker_type_id)
    if published_only:
        q = q.filter_by(is_published=True)

    results = q.order_by(IndexResult.year.desc(), IndexResult.quarter.desc()).all()
    return jsonify([r.to_dict() for r in results])


@index_bp.route("/api/calculate", methods=["POST"])
def calculate_index():
    """
    计算人工费调整指数
    公式：A = (Pa / Pj) x 100
    Pa = 报告期平均人工单价（市场数据）
    Pj = 基期人工单价（定额基期价格）
    """
    data = request.get_json() or {}
    year = data.get("year", datetime.utcnow().year)
    quarter = data.get("quarter", ((datetime.utcnow().month - 1) // 3) + 1)

    projects = Project.query.all()
    worker_types = WorkerType.query.all()
    count = 0

    for project in projects:
        for wt in worker_types:
            # 获取该工种基期价格（统一为148）
            base = QuotaBase.query.filter_by(worker_type_id=wt.id).first()
            base_price = base.base_price if base else 148.0

            # 计算该工种在该项目该季度的市场平均价格
            # 确定季度日期范围
            quarter_start = date(year, (quarter - 1) * 3 + 1, 1)
            if quarter == 4:
                quarter_end = date(year, 12, 31)
            else:
                quarter_end = date(year, quarter * 3, 1)
                import calendar
                _, last_day = calendar.monthrange(quarter_end.year, quarter_end.month)
                quarter_end = date(quarter_end.year, quarter_end.month, last_day)

            avg_price = db.session.query(
                func.avg(LaborPrice.unit_price)
            ).filter(
                LaborPrice.project_id == project.id,
                LaborPrice.worker_type_id == wt.id,
                LaborPrice.data_date >= quarter_start,
                LaborPrice.data_date <= quarter_end,
            ).scalar()

            if avg_price is None or avg_price == 0:
                continue

            avg_price = float(avg_price)
            index_value = round((avg_price / base_price) * 100, 2)

            # 检查是否已有记录
            existing = IndexResult.query.filter_by(
                project_id=project.id,
                worker_type_id=wt.id,
                year=year,
                quarter=quarter,
            ).first()

            if existing:
                existing.base_price = base_price
                existing.report_price = avg_price
                existing.index_value = index_value
            else:
                result = IndexResult(
                    project_id=project.id,
                    worker_type_id=wt.id,
                    base_price=base_price,
                    report_price=avg_price,
                    index_value=index_value,
                    year=year,
                    quarter=quarter,
                )
                db.session.add(result)
            count += 1

    db.session.commit()
    return jsonify({"success": True, "count": count, "year": year, "quarter": quarter})


@index_bp.route("/api/publish/<int:rid>", methods=["POST"])
def publish_index(rid):
    """发布单条指数"""
    r = IndexResult.query.get_or_404(rid)
    r.is_published = True
    r.publish_date = date.today()
    db.session.commit()
    return jsonify({"success": True})


@index_bp.route("/api/batch-publish", methods=["POST"])
def batch_publish():
    """批量发布指定年季的指数"""
    data = request.get_json()
    year = data["year"]
    quarter = data["quarter"]
    results = IndexResult.query.filter_by(year=year, quarter=quarter).all()
    for r in results:
        r.is_published = True
        r.publish_date = date.today()
    db.session.commit()
    return jsonify({"success": True, "count": len(results)})


@index_bp.route("/api/summary")
def index_summary():
    """指数综合概览"""
    # 所有年份季度
    periods = db.session.query(
        IndexResult.year, IndexResult.quarter,
        func.avg(IndexResult.index_value).label("avg_index"),
        func.count(IndexResult.id).label("count"),
    ).group_by(IndexResult.year, IndexResult.quarter
    ).order_by(IndexResult.year.desc(), IndexResult.quarter.desc()).all()

    period_list = [{
        "year": p.year, "quarter": p.quarter,
        "avg_index": round(float(p.avg_index), 2),
        "count": p.count,
    } for p in periods]

    # 各工种平均指数
    worker_index = db.session.query(
        WorkerType.name,
        func.avg(IndexResult.index_value).label("avg_index"),
    ).join(WorkerType, WorkerType.id == IndexResult.worker_type_id
    ).group_by(WorkerType.id, WorkerType.name).all()

    worker_list = [{"name": w.name, "avg_index": round(float(w.avg_index), 2)} for w in worker_index]

    return jsonify({"periods": period_list, "worker_indexes": worker_list})
