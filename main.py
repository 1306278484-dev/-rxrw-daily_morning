from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

# ===================== 固定配置 =====================
today = datetime.now()
# 读取 GitHub Secrets 环境变量（无需修改代码）
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]
# 和风天气KEY（新增，免费申请）
weather_key = os.environ["WEATHER_KEY"]

# ===================== 【修复】可用的天气接口 =====================
def get_weather():
    # 替换为和风天气官方免费接口（稳定可用）
    url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key={weather_key}"
    try:
        res = requests.get(url, timeout=10).json()
        if res["code"] == "200":
            wea = res["now"]["text"]       # 天气状况
            temp = int(res["now"]["temp"]) # 温度（整数）
            return wea, temp
    except:
        pass
    # 接口异常时返回默认值
    return "晴", 20

# ===================== 以下功能完全保留，无需修改 =====================
def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days

def get_words():
    try:
        words = requests.get("https://api.shadiao.pro/chp", timeout=5)
        if words.status_code == 200:
            return words.json()['data']['text']
    except:
        pass
    return "宝贝，我爱你❤️"

def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

# ===================== 发送消息（原逻辑不变） =====================
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
wea, temperature = get_weather()

data = {
    "weather":{"value":wea},
    "temperature":{"value":temperature},
    "love_days":{"value":get_count()},
    "birthday_left":{"value":get_birthday()},
    "words":{"value":get_words(), "color":get_random_color()}
}

res = wm.send_template(user_id, template_id, data)
print("发送成功：", res)
