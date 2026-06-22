# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request, render_template
from math import ceil
from datetime import datetime
from app import db
from app.models import (Project, ProjectType, City,
                         LaborPrice, IndexResult)

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


@projects_bp.route("/")
def projects_page():
    types = ProjectType.query.order_by(ProjectType.name).all()
    cities = City.query.all()
    return render_template("projects.html", types=types, cities=cities)


@projects_bp.route("/api/list")
def list_projects():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)

    q = Project.query.order_by(Project.created_at.desc())
    total = q.count()
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [p.to_dict() for p in pagination.items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": ceil(total / per_page) if total > 0 else 1,
    })


@projects_bp.route("/api/get/<int:pid>")
def get_project(pid):
    p = Project.query.get_or_404(pid)
    return jsonify(p.to_dict())


@projects_bp.route("/api/add", methods=["POST"])
def add_project():
    data = request.get_json()
    p = Project(
        name=data["name"],
        project_type_id=data["project_type_id"],
        city_id=data["city_id"],
        building_area=data.get("building_area"),
        total_workers=data.get("total_workers"),
        description=data.get("description", ""),
    )
    if data.get("start_date"):
        p.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if data.get("end_date"):
        p.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    db.session.add(p)
    db.session.commit()
    return jsonify({"success": True, "project": p.to_dict()})


@projects_bp.route("/api/update/<int:pid>", methods=["POST"])
def update_project(pid):
    p = Project.query.get_or_404(pid)
    data = request.get_json()
    p.name = data.get("name", p.name)
    p.project_type_id = data.get("project_type_id", p.project_type_id)
    p.city_id = data.get("city_id", p.city_id)
    p.building_area = data.get("building_area", p.building_area)
    p.total_workers = data.get("total_workers", p.total_workers)
    p.description = data.get("description", p.description)
    if "start_date" in data and data["start_date"]:
        p.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if "end_date" in data and data["end_date"]:
        p.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    db.session.commit()
    return jsonify({"success": True, "project": p.to_dict()})


@projects_bp.route("/api/delete/<int:pid>", methods=["POST"])
def delete_project(pid):
    p = Project.query.get_or_404(pid)
    LaborPrice.query.filter_by(project_id=pid).delete()
    IndexResult.query.filter_by(project_id=pid).delete()
    db.session.delete(p)
    db.session.commit()
    return jsonify({"success": True})
