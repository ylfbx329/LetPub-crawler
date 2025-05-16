import json
from collections import defaultdict

import numpy as np
import pandas as pd
from flask import Blueprint, current_app, render_template

chart_bp = Blueprint('chart', __name__, url_prefix='/chart')


@chart_bp.route('/factor')
def impact_factor():
    df = current_app.config['data']

    # 按影响因子降序排序
    df = df.sort_values(by="impact_factor", ascending=False)

    # 只取前 100 个
    top_df = df.head(100)

    tmp_df = df[df["impact_factor"] > 0]
    log_if = np.log1p(tmp_df["impact_factor"])  # log1p 保证对 0 安全
    q1 = log_if.quantile(0.25)
    q3 = log_if.quantile(0.75)
    iqr = q3 - q1
    upper_log = q3 + 1.5 * iqr

    # 转回原始空间
    upper = np.expm1(upper_log)

    chart_data = {
        "factor": {
            'name': top_df["name"].tolist(),
            'impact_factors': top_df["impact_factor"].tolist(),
            'real_time_if': top_df["real_time_if"].tolist(),
            'five_year_if': top_df["five_year_if"].tolist(),
            'h_index': top_df["h_index"].tolist(),
            'iqr_upper': upper,
        },
    }

    return render_template("chart/factor.html", chart_data=json.dumps(chart_data))


@chart_bp.route('/subject')
def subject():
    df = current_app.config['data']

    major_counter = Counter()
    subfield_mapping = defaultdict(list)  # major -> list of minor

    for row in df["jif_sci_rank"]:
        if isinstance(row, dict) and "学科" in row:
            field = row["学科"]
            if ',' in field:
                major, minor = [s.strip() for s in field.split(',', 1)]
            else:
                # 无法拆分的，视为完整学科名 => 同时作为大类和小类
                major = field
                minor = field
            major_counter[major] += 1
            subfield_mapping[major].append(minor)

    # 小类统计：major -> list of {name, value}
    subfield_stats = {
        k: Counter(v) for k, v in subfield_mapping.items()
    }

    chart_data = {
        "subject": {
            "majors": [{"name": k, "value": v} for k, v in major_counter.items()],
            "minors": {
                k: [{"name": subk, "value": subv} for subk, subv in subfield_stats[k].items()]
                for k in subfield_stats
            }
        }
    }

    return render_template("chart/subject.html", chart_data=json.dumps(chart_data))


@chart_bp.route('/cite_if')
def cite_if():
    df = current_app.config['data']

    df = df[
        (df["impact_factor"].notna()) &
        (df["self_cite_rate"].notna()) &
        (df["impact_factor"] != 0) &
        (df["self_cite_rate"] != 0)
        ]

    chart_data = {
        "cite_if": [
            {"name": row["name"], "value": [row["impact_factor"], row["self_cite_rate"]]}
            for _, row in df.iterrows()
        ]
    }

    return render_template("chart/cite_if.html", chart_data=json.dumps(chart_data))


from collections import Counter


@chart_bp.route('/country')
def country():
    df = current_app.config['data']
    df = df[df["country"] != '']
    country_counts = df['country'].dropna().value_counts().to_dict()
    chart_data = [{"name": country, "value": count} for country, count in country_counts.items()]
    max_count = max(country_counts.values())
    return render_template('chart/country.html', chart_data=json.dumps(chart_data, ensure_ascii=False), max_count=max_count)


@chart_bp.route('/apc_jci')
def apc_jci():
    df = current_app.config['data']

    # 只保留有 APC 价格和 JCI 值的 OA 期刊
    df = df[df['open_access'] & df['apc_price'].notna() & df['jci'].notna()]

    # 转换为浮点数
    df = df.loc[df['apc_price'].notna() & df['jci'].notna()].copy()  # ← 添加 copy()
    df['apc_price'] = pd.to_numeric(df['apc_price'], errors='coerce')
    df['jci'] = pd.to_numeric(df['jci'], errors='coerce')
    df = df[(df['apc_price'] != 0) & (df['jci'] != 0)]

    df = df.dropna(subset=['apc_price', 'jci'])

    # 构造点数据
    points = df.apply(lambda row: {
        "name": row["name"],
        "x": row["apc_price"],
        "y": row["jci"]
    }, axis=1).tolist()

    return render_template("chart/apc_jci.html", chart_data=json.dumps(points, ensure_ascii=False))


@chart_bp.route('/review_accept')
def review_accept():
    df = current_app.config['data'].copy()

    df = df[df['speed'].notna() & df['accept'].notna() & (df['speed'] != 0) & (df['accept'] != 0)]

    # 可选：按审稿速度排序，选前 50 个（避免过长）
    df = df.sort_values(by='speed')

    chart_data = {
        "name": df['name'].tolist(),
        "speed": df['speed'].tolist(),
        "accept": df['accept'].tolist()
    }

    return render_template("chart/review_accept.html", chart_data=json.dumps(chart_data, ensure_ascii=False))


@chart_bp.route('/country_map')
def country_map():
    df = current_app.config['data']

    # 标准化国家名称（如已有映射可提前转换）
    df = df[df['country'].notna()]
    country_counts = df['country'].value_counts().to_dict()

    data = [{"name": k, "value": v} for k, v in country_counts.items()]
    max_count = max(country_counts.values())

    return render_template("chart/country_map.html", data=json.dumps(data, ensure_ascii=False), max_count=max_count)
