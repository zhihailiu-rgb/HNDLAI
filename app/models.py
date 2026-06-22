# -*- coding: utf-8 -*-
from datetime import datetime
from app import db


class Province(db.Model):
    __tablename__ = "province"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    cities = db.relationship("City", backref="province", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class City(db.Model):
    __tablename__ = "city"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey("province.id"), nullable=False)
    projects = db.relationship("Project", backref="city", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "province_id": self.province_id}


class ProjectType(db.Model):
    __tablename__ = "project_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    projects = db.relationship("Project", backref="project_type", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class WorkerType(db.Model):
    __tablename__ = "worker_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))
    prices = db.relationship("LaborPrice", backref="worker_type", lazy=True)
    index_results = db.relationship("IndexResult", backref="worker_type", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "category": self.category,
                "description": self.description}


class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    project_type_id = db.Column(db.Integer, db.ForeignKey("project_type.id"), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"), nullable=False)
    building_area = db.Column(db.Float)
    total_workers = db.Column(db.Integer)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prices = db.relationship("LaborPrice", backref="project", lazy=True)
    index_results = db.relationship("IndexResult", backref="project", lazy=True)

    def to_dict(self):
        ct = self.city
        pt = self.project_type
        return {
            "id": self.id, "name": self.name,
            "project_type_id": self.project_type_id,
            "project_type_name": pt.name if pt else "",
            "city_id": self.city_id,
            "city_name": ct.name if ct else "",
            "building_area": self.building_area,
            "total_workers": self.total_workers,
            "description": self.description,
            "start_date": str(self.start_date) if self.start_date else "",
            "end_date": str(self.end_date) if self.end_date else "",
            "created_at": str(self.created_at)[:19] if self.created_at else "",
        }


class LaborPrice(db.Model):
    __tablename__ = "labor_price"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    worker_type_id = db.Column(db.Integer, db.ForeignKey("worker_type.id"), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    data_date = db.Column(db.Date, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(100))
    remark = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else "",
            "worker_type_id": self.worker_type_id,
            "worker_type_name": self.worker_type.name if self.worker_type else "",
            "unit_price": self.unit_price,
            "data_date": str(self.data_date) if self.data_date else "",
            "is_verified": self.is_verified,
            "source": self.source,
            "remark": self.remark,
        }


class QuotaBase(db.Model):
    __tablename__ = "quota_base"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    worker_type_id = db.Column(db.Integer, db.ForeignKey("worker_type.id"), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    regulation_number = db.Column(db.String(100))
    effective_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        wt = self.worker_type
        return {
            "id": self.id,
            "worker_type_id": self.worker_type_id,
            "worker_type_name": wt.name if wt else "",
            "base_price": self.base_price,
            "regulation_number": self.regulation_number,
            "effective_date": str(self.effective_date) if self.effective_date else "",
        }


class IndexResult(db.Model):
    __tablename__ = "index_result"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    worker_type_id = db.Column(db.Integer, db.ForeignKey("worker_type.id"), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    report_price = db.Column(db.Float, nullable=False)
    index_value = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    publish_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else "",
            "worker_type_id": self.worker_type_id,
            "worker_type_name": self.worker_type.name if self.worker_type else "",
            "base_price": self.base_price,
            "report_price": self.report_price,
            "index_value": self.index_value,
            "year": self.year,
            "quarter": self.quarter,
            "is_published": self.is_published,
            "publish_date": str(self.publish_date) if self.publish_date else "",
        }
