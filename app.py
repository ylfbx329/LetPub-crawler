from flask import Flask, render_template, current_app

from utils import data_load
from views.chart import chart_bp
from views.detail import detail_bp

app = Flask(__name__)
app.register_blueprint(chart_bp)
app.register_blueprint(detail_bp)
app.config['data'] = data_load()


@app.route('/')
def index():
    df = current_app.config['data']

    # 只保留需要的字段
    subset = df[[
        "id", "name", "impact_factor", "sci_part",
        "open_access", "country_trans", "publisher", "letpub_link"
    ]].copy()

    # 处理布尔字段
    subset["open_access"] = subset["open_access"].apply(lambda x: "是" if x else "否")

    # 转成字典列表用于表格渲染
    journals = subset.to_dict(orient='records')
    return render_template("index.html", journals=journals)


if __name__ == '__main__':
    app.run(debug=True)
