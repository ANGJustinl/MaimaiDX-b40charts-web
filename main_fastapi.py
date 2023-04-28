from fastapi import FastAPI
from src.libraries import maimai_best_40

import json
from pyecharts import options as opts
from pyecharts.charts import Bar

app = FastAPI(debug='debug')

@app.get("/b40/{qq_id}")
async def b40_base(qq_id):
    payload = {'qq': str(qq_id)}
    list, success = await maimai_best_40.generate(payload=payload)
    if success == 400:
        return "未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。"
    if success == 403:
        return "该用户禁止了其他人获取数据。"
    #return json.dumps(list)
    return list

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)