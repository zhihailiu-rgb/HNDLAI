# -*- coding: utf-8 -*-
"""种子数据生成器 — 海南省建设工程人工费调整指数模拟数据"""
from datetime import date, timedelta
import random, calendar
from app import create_app, db
from app.models import (Province, City, ProjectType, WorkerType,
                         Project, LaborPrice, QuotaBase, IndexResult)

random.seed(42)

app = create_app("development")

def seed():
    with app.app_context():
        # 清空旧数据
        db.drop_all()
        db.create_all()
        print("数据库已重置")

        # ========== 1. 省份 ==========
        hn = Province(id=1, name="海南省")
        db.session.add(hn)
        db.session.flush()

        # ========== 2. 城市 ==========
        cities_data = [
            ("海口市", 1.00), ("三亚市", 1.06), ("儋州市", 0.95),
            ("文昌市", 0.92), ("琼中黎族苗族自治县", 0.85), ("乐东黎族自治县", 0.88),
        ]
        cities = {}
        for i, (name, mult) in enumerate(cities_data, 1):
            c = City(id=i, name=name, province_id=hn.id)
            db.session.add(c)
            cities[name] = c
        db.session.flush()
        print(f"已创建 {len(cities_data)} 个城市")

        # ========== 3. 工程类型 ==========
        types_data = [
            ("住宅", "住宅建筑工程"),
            ("医院", "医院建筑工程"),
            ("学校", "学校建筑工程"),
            ("市政", "市政道路及管网工程"),
        ]
        ptypes = {}
        for i, (name, desc) in enumerate(types_data, 1):
            t = ProjectType(id=i, name=name, description=desc)
            db.session.add(t)
            ptypes[name] = t
        db.session.flush()
        print(f"已创建 {len(types_data)} 个工程类型")

        # ========== 4. 工种 ==========
        workers_data = [
            ("建筑普工", "建筑", "施工现场普通劳务工人"),
            ("木工(模板工)", "建筑", "模板制作与安装"),
            ("钢筋工", "建筑", "钢筋加工与绑扎"),
            ("混凝土工", "建筑", "混凝土浇筑与养护"),
            ("砌筑抹灰工", "建筑", "砌体与抹灰工程"),
            ("架子工", "建筑", "脚手架搭设与拆除"),
            ("防水防腐工", "装饰", "防水与防腐工程施工"),
            ("装饰机电综合工", "装饰", "装饰装修与机电安装"),
            ("市政道路管网工", "市政", "市政道路与管网施工"),
        ]
        worker_types = {}
        for i, (name, cat, desc) in enumerate(workers_data, 1):
            wt = WorkerType(id=i, name=name, category=cat, description=desc)
            db.session.add(wt)
            worker_types[name] = wt
        db.session.flush()
        print(f"已创建 {len(workers_data)} 个工种")

        # ========== 5. 工程项目 ==========
        projects_data = [
            ("海口江东新区碧桂园中央半岛住宅项目", "住宅", "海口市", 120000, 85000),
            ("海口国兴大道大英山片区某住宅项目", "住宅", "海口市", 88000, 62000),
            ("海口市人民医院综合楼项目", "医院", "海口市", 65000, 48000),
            ("三亚市崖州湾科技城中学项目", "学校", "三亚市", 42000, 32000),
            ("三亚市海棠湾某度假酒店项目", "住宅", "三亚市", 78000, 55000),
            ("儋州市滨海新区滨河路市政工程", "市政", "儋州市", None, 28000),
            ("儋州市那大镇城北住宅小区项目", "住宅", "儋州市", 95000, 68000),
            ("文昌市国际航天城学校项目", "学校", "文昌市", 38000, 29000),
            ("文昌市某市政道路及排水工程", "市政", "文昌市", None, 22000),
            ("琼中县人民医院门诊综合楼项目", "医院", "琼中黎族苗族自治县", 28000, 21000),
            ("乐东县九所新区市政道路管网工程", "市政", "乐东黎族自治县", None, 18000),
            ("海口市江东新区某学校项目", "学校", "海口市", 45000, 35000),
        ]
        projects_list = []
        city_map = {c.name: c for c in cities.values()}
        for i, (name, ptype_name, city_name, area, workers) in enumerate(projects_data, 1):
            p = Project(
                id=i, name=name,
                project_type_id=ptypes[ptype_name].id,
                city_id=city_map[city_name].id,
                building_area=area,
                total_workers=workers,
                description=f"{city_name}的{ptype_name}类建设工程项目",
                start_date=date(2023, random.randint(1, 6), 1),
                end_date=date(2026, random.randint(6, 12), 1),
            )
            db.session.add(p)
            projects_list.append(p)
        db.session.flush()
        print(f"已创建 {len(projects_data)} 个工程项目")

        # ========== 6. 定额基期价格 ==========
        # 依据：琼建规〔2022〕3号，基期价格148元/工日
        for i, (wname, _, _) in enumerate(workers_data, 1):
            qb = QuotaBase(
                worker_type_id=worker_types[wname].id,
                base_price=148.0,
                regulation_number="琼建规〔2022〕3号",
                effective_date=date(2022, 4, 1),
            )
            db.session.add(qb)
        db.session.flush()
        print("已创建定额基期价格（148元/工日）")

        # ========== 7. 劳务市场价格数据 ==========
        # 各工种在2024Q1~2026Q2的市场价格
        # 基础价格（海口、基准区域）
        base_prices = {
            "建筑普工": 210, "木工(模板工)": 320, "钢筋工": 290,
            "混凝土工": 260, "砌筑抹灰工": 280, "架子工": 340,
            "防水防腐工": 300, "装饰机电综合工": 320, "市政道路管网工": 290,
        }

        # 城市价格系数
        city_mult = {
            "海口市": 1.0, "三亚市": 1.05, "儋州市": 0.95,
            "文昌市": 0.92, "琼中黎族苗族自治县": 0.85, "乐东黎族自治县": 0.88,
        }

        # 季节性波动：4-10月旺季加价，11-3月淡季减价
        def seasonal_factor(month):
            if 4 <= month <= 10:
                return 1.0 + random.uniform(0.02, 0.06)
            else:
                return 1.0 - random.uniform(0.02, 0.05)

        # 年度上涨趋势：每年约上涨3-5%
        def year_factor(year, base_year=2024):
            return 1.0 + (year - base_year) * 0.04

        price_records = []
        price_id = 1
        sources = ["劳务分包结算", "市场询价", "广联达计价"]

        for project in projects_list:
            project_city = db.session.get(City, project.city_id)
            city_name = project_city.name
            cm = city_mult.get(city_name, 1.0)

            for year in [2024, 2025, 2026]:
                yf = year_factor(year)
                for quarter in [1, 2, 3, 4]:
                    if year == 2026 and quarter > 2:
                        continue  # 只到2026Q2

                    # 季度起始月份
                    q_start_month = (quarter - 1) * 3 + 1

                    # 每月生成一条记录
                    for m_offset in range(3):
                        month = q_start_month + m_offset
                        if month > 12:
                            continue

                        sf = seasonal_factor(month)
                        day = min(28, random.randint(1, 28))

                        for wname, base_p in base_prices.items():
                            wt = worker_types[wname]
                            # 随机波动 ±5%
                            noise = random.uniform(0.95, 1.05)
                            unit_price = round(base_p * cm * yf * sf * noise, 2)

                            lp = LaborPrice(
                                id=price_id,
                                project_id=project.id,
                                worker_type_id=wt.id,
                                unit_price=unit_price,
                                data_date=date(year, month, day),
                                source=random.choice(sources),
                                is_verified=random.random() > 0.3,
                                remark=f"{city_name}{wname}{year}年{month}月市场价",
                            )
                            db.session.add(lp)
                            price_id += 1

                            # 每100条flush一次以保持内存可控
                            if price_id % 100 == 0:
                                db.session.flush()

        db.session.flush()
        print(f"已创建 {price_id - 1} 条劳务价格记录")

        # ========== 8. 预计算部分指数 ==========
        # 为2024Q1~2026Q2自动计算指数
        base_p = 148.0
        index_id = 1
        for project in projects_list:
            for year in [2024, 2025, 2026]:
                for quarter in [1, 2, 3, 4]:
                    if year == 2026 and quarter > 2:
                        continue

                    q_start = date(year, (quarter - 1) * 3 + 1, 1)
                    if quarter == 4:
                        q_end = date(year, 12, 31)
                    else:
                        q_end = date(year, quarter * 3, 1)
                        import calendar
                        _, ld = calendar.monthrange(q_end.year, q_end.month)
                        q_end = date(q_end.year, q_end.month, ld)

                    for wname, base_p in base_prices.items():
                        wt = worker_types[wname]

                        from sqlalchemy import func
                        avg_p = db.session.query(
                            func.avg(LaborPrice.unit_price)
                        ).filter(
                            LaborPrice.project_id == project.id,
                            LaborPrice.worker_type_id == wt.id,
                            LaborPrice.data_date >= q_start,
                            LaborPrice.data_date <= q_end,
                        ).scalar()

                        if avg_p is None:
                            continue

                        avg_p = float(avg_p)
                        idx_val = round((avg_p / 148.0) * 100, 2)

                        ir = IndexResult(
                            id=index_id,
                            project_id=project.id,
                            worker_type_id=wt.id,
                            base_price=148.0,
                            report_price=avg_p,
                            index_value=idx_val,
                            year=year,
                            quarter=quarter,
                            is_published=(year < 2026 or (year == 2026 and quarter <= 1)),
                            publish_date=date(year, quarter * 3, 15) if year < 2026 or (year == 2026 and quarter <= 1) else None,
                        )
                        db.session.add(ir)
                        index_id += 1

        db.session.commit()
        print(f"已创建 {index_id - 1} 条指数结果")
        print("\n" + "=" * 50)
        print("  种子数据生成完成！")
        print(f"  - 城市: {len(cities_data)} 个")
        print(f"  - 工程类型: {len(types_data)} 种")
        print(f"  - 工种: {len(workers_data)} 类")
        print(f"  - 项目: {len(projects_data)} 个")
        print(f"  - 价格记录: {price_id - 1} 条")
        print(f"  - 指数结果: {index_id - 1} 条")
        print("=" * 50)


if __name__ == "__main__":
    seed()

