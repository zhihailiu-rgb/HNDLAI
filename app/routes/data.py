# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from app import db
from app.models import LaborPrice, Project, WorkerType, ProjectType, City

data_bp = Blueprint("data", __name__, url_prefix="/data")


@data_bp.route("/")
def data_page():
    """数据管理页面"""
    projects = Project.query.all()
    worker_types = WorkerType.query.all()
    return render_template("data.html", projects=projects, worker_types=worker_types)


@data_bp.route("/api/list")
def list_prices():
    project_id = request.args.get("project_id")
    worker_type_id = request.args.get("worker_type_id")
    q = LaborPrice.query
    if project_id:
        q = q.filter_by(project_id=int(project_id))
    if worker_type_id:
        q = q.filter_by(worker_type_id=int(worker_type_id))
    prices = q.order_by(LaborPrice.data_date.desc()).all()
    return jsonify([p.to_dict() for p in prices])


@data_bp.route("/api/add", methods=["POST"])
def add_price():
    data = request.get_json()
    lp = LaborPrice(
        project_id=data["project_id"],
        worker_type_id=data["worker_type_id"],
        unit_price=float(data["unit_price"]),
        data_date=datetime.strptime(data["data_date"], "%Y-%m-%d").date(),
        source=data.get("source", ""),
        remark=data.get("remark", ""),
        is_verified=data.get("is_verified", False),
    )
    db.session.add(lp)
    db.session.commit()
    return jsonify({"success": True, "price": lp.to_dict()})


@data_bp.route("/api/delete/<int:pid>", methods=["POST"])
def delete_price(pid):
    lp = LaborPrice.query.get_or_404(pid)
    db.session.delete(lp)
    db.session.commit()
    return jsonify({"success": True})


@data_bp.route("/api/verify/<int:pid>", methods=["POST"])
def verify_price(pid):
    lp = LaborPrice.query.get_or_404(pid)
    lp.is_verified = not lp.is_verified
    db.session.commit()
    return jsonify({"success": True, "is_verified": lp.is_verified})


@data_bp.route("/api/trend")
def price_trend():
    """按工种的各季度均价趋势"""
    worker_type_id = request.args.get("worker_type_id", type=int)
    q = db.session.query(
        LaborPrice.data_date, WorkerType.name,
        func.avg(LaborPrice.unit_price).label("avg_price")
    ).join(WorkerType, WorkerType.id == LaborPrice.worker_type_id
    ).group_by(LaborPrice.data_date, WorkerType.name)
    if worker_type_id:
        q = q.filter(LaborPrice.worker_type_id == worker_type_id)
    rows = q.order_by(LaborPrice.data_date).all()

    from collections import defaultdict
    series = defaultdict(list)
    for r in rows:
        series[r.name].append({
            "date": str(r.data_date),
            "price": round(float(r.avg_price), 2),
        })
    result = [{"name": k, "data": v} for k, v in series.items()]
    return jsonify(result)
