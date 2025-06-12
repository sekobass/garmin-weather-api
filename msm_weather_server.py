from flask import Flask, Response
import requests
import json

app = Flask(__name__)

@app.route('/msm_weather')
def msm_weather():
    url = "https://www.jma.go.jp/bosai/forecast/data/forecast/170000.json"
    response = requests.get(url)
    data = response.json()

    result = {}

    # 天気文
    weather_ts = data[0]['timeSeries'][0]
    weather_dates = weather_ts['timeDefines']
    for area in weather_ts['areas']:
        if area['area']['name'] == "能登":
            for i, date in enumerate(weather_dates[:2]):
                day_key = f"day{i+1}"
                result[day_key] = {
                    "date": date[:10],
                    "weather": area['weathers'][i],
                    "rain_6h": []
                }

    # 降水確率（6時間ごと）
    for ts in data[0]['timeSeries']:
        if 'pops' in ts['areas'][0]:
            pop_dates = ts['timeDefines']
            for area in ts['areas']:
                if area['area']['name'] == "能登":
                    for i, dt in enumerate(pop_dates):
                        date = dt[:10]
                        hour = int(dt[11:13])
                        block = f"{hour:02d}〜{hour+6:02d}時"
                        pop = area['pops'][i]
                        for j in range(1, 3):
                            if result.get(f"day{j}") and result[f"day{j}"]["date"] == date:
                                result[f"day{j}"]["rain_6h"].append({
                                    "time_block": block,
                                    "pop": pop
                                })
                    break

    # ← 修正ポイント：Unicodeをエスケープしないようにする
    return Response(json.dumps(result, ensure_ascii=False, indent=2), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
