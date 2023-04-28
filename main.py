from flask import Flask, render_template

from pyecharts import options as opts
from pyecharts.charts import Bar, Tab

from src.libraries import get

app = Flask(__name__, static_folder="templates")


async def b40bar_base(qq_id) -> Bar:
    resp = await get.get(f'http://127.0.0.1:8000/b40/{qq_id}')
    resp = eval(resp.text)
    if resp == str:
        return resp
    best25 = resp[0]
    best15 = resp[1]
    rating = str(resp[2])
    username = str(resp[3])
    b25xaxis_name_list = list()
    b25xaxis_ra_list = list()
    b15xaxis_name_list = list()
    b15xaxis_ra_list = list()
    for key in best25:
        b15xaxis_ra_list.append(0)
        b25xaxis_name_list.append(best25[key][0])
        b25xaxis_ra_list.append(best25[key][2])
    for key in best15:
        b25xaxis_ra_list.append(0)
        b15xaxis_name_list.append(best15[key][0])
        b15xaxis_ra_list.append(best15[key][2])
    all_list = b25xaxis_name_list + b15xaxis_name_list
    c = (
        Bar()
        .set_global_opts(title_opts=opts.TitleOpts(title=username, subtitle="B40Rating:"+rating),xaxis_opts = opts.AxisOpts(axislabel_opts={"rotate":25,"interval":"0"}))
        .add_xaxis(all_list)
        #.extend_axis(xaxis_data = b25xaxis_name_list, xaxis=opts.AxisOpts(type_="category", position='bottom', ))

        .add_yaxis("经典谱面最佳 b25", b25xaxis_ra_list,)
        .add_yaxis("DX谱面最佳 b15", b15xaxis_ra_list,)
    )
    return c


@app.route("/b40/<int:qq_id>")
def index(qq_id):
    qq_id = qq_id
    return render_template('maib40.html')


@app.route("/barChart/<int:qq_id>")
async def get_bar_chart(qq_id):
    c = await b40bar_base(qq_id)
    return c.dump_options_with_quotes()


if __name__ == "__main__":
    app.run()