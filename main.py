from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

# ===================== 基础配置（已删除 START_DATE） =====================
today = datetime.now()
# 读取环境变量
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]
weather_key = os.environ["WEATHER_KEY"]

# ===================== 天气接口（修复可用） =====================
def get_weather():
    url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key={weather_key}"
    try:
        res = requests.get(url, timeout=10).json()
        if res["code"] == "200":
            wea = res["now"]["text"]
            temp = int(res["now"]["temp"])
            return wea, temp
    except:
        pass
    return "晴", 20

# ===================== 生日倒计时（保留） =====================
def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days

# ===================== 随机情话（保留） =====================
def get_words():
    try:
        words = requests.get("https://api.shadiao.pro/chp", timeout=5)
        if words.status_code == 200:
            return words.json()['data']['text']
    except:
        pass
    return "宝贝，我爱你❤️"

# ===================== 随机颜色 =====================
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

# ===================== 发送微信消息 =====================
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
wea, temperature = get_weather()

# =============== 关键：删除了 love_days 字段 ===============
data = {
    "weather":{"value":wea},
    "temperature":{"value":temperature},
    "birthday_left":{"value":get_birthday()},
    "words":{"value":get_words(), "color":get_random_color()}
}

res = wm.send_template(user_id, template_id, data)
print("发送成功：", res)
