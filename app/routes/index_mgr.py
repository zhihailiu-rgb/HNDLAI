# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request, render_template
from math import ceil
from datetime import datetime, date
from app import db
from sqlalchemy import func
from app.models import (LaborPrice, QuotaBase, IndexResult,
                         WorkerType, Project)
import calendar

index_bp = Blueprint("index_mgr", __name__, url_prefix="/index")


@index_bp.route("/")
def index_page():
    worker_types = WorkerType.query.order_by(WorkerType.name).all()
    projects = Project.query.order_by(Project.name).all()
    return render_template("index.html", worker_types=worker_types, projects=projects)


@index_bp.route("/api/results")
def list_results():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)
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

    q = q.order_by(IndexResult.year.desc(), IndexResult.quarter.desc(),
                    IndexResult.id.desc())
    total = q.count()
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [r.to_dict() for r in pagination.items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": ceil(total / per_page) if total > 0 else 1,
    })


@index_bp.route("/api/calculate", methods=["POST"])
def calculate_index():
    data = request.get_json() or {}
    year = data.get("year", datetime.utcnow().year)
    quarter = data.get("quarter", ((datetime.utcnow().month - 1) // 3) + 1)

    projects = Project.query.all()
    worker_types = WorkerType.query.all()
    count = 0

    for project in projects:
        for wt in worker_types:
            base = QuotaBase.query.filter_by(worker_type_id=wt.id).first()
            base_price = base.base_price if base else 148.0

            quarter_start = date(year, (quarter - 1) * 3 + 1, 1)
            if quarter == 4:
                quarter_end = date(year, 12, 31)
            else:
                quarter_end = date(year, quarter * 3, 1)
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
    r = IndexResult.query.get_or_404(rid)
    r.is_published = True
    r.publish_date = date.today()
    db.session.commit()
    return jsonify({"success": True})


@index_bp.route("/api/batch-publish", methods=["POST"])
def batch_publish():
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

    worker_index = db.session.query(
        WorkerType.name,
        func.avg(IndexResult.index_value).label("avg_index"),
    ).join(WorkerType, WorkerType.id == IndexResult.worker_type_id
    ).group_by(WorkerType.id, WorkerType.name).all()

    worker_list = [{"name": w.name, "avg_index": round(float(w.avg_index), 2)} for w in worker_index]

    return jsonify({"periods": period_list, "worker_indexes": worker_list})
