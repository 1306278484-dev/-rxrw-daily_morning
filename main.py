from datetime import date, datetime, timedelta
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

# 自动切换北京时间
utc_now = datetime.utcnow()
beijing_now = utc_now + timedelta(hours=8)
today = beijing_now.date()

# 配置读取
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id_list = [os.environ["USER_ID"], os.environ["USER_ID_2"]]
template_id = os.environ["TEMPLATE_ID"]
weather_key = os.environ["WEATHER_KEY"]

# 4个提醒配置（新增吃饭）
REMIND_CONFIG = {
    "起床": {
        "time_range": (7, 9),
        "first_text": "宝贝八点啦☀️ 快起床开启美好的一天！",
        "keyword1": "起床"
    },
    "吃饭": {
        "time_range": (11, 13),  # 11-13点触发（12点吃饭）
        "first_text": "干饭时间到🍚 宝贝记得好好吃饭，不许饿肚子！",
        "keyword1": "吃饭"
    },
    "洗澡": {
        "time_range": (21, 23),
        "first_text": "宝贝十点啦🛁 该洗澡放松一下啦～",
        "keyword1": "洗澡"
    },
    "睡觉": {
        "time_range": (23, 1),
        "first_text": "宝贝十二点啦🌙 乖乖睡觉，晚安我爱你！",
        "keyword1": "睡觉"
    }
}

# 天气接口
def get_weather():
    url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key={weather_key}"
    try:
        res = requests.get(url, timeout=10).json()
        if res["code"] == "200":
            return f"{res['now']['text']}，{res['now']['temp']}℃"
    except: pass
    return "天气获取成功"

# 生日倒计时
def get_birthday():
    birth = datetime.strptime(f"{today.year}-{birthday}", "%Y-%m-%d")
    if birth < beijing_now: birth = birth.replace(year=birth.year+1)
    return (birth - beijing_now).days

# 随机情话
def get_words():
    try:
        w = requests.get("https://api.shadiao.pro/chp", timeout=5)
        if w.status_code == 200: return w.json()['data']['text']
    except: pass
    return "宝贝，我爱你❤️"

# 随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

# 自动判断提醒
def get_remind_info():
    h = beijing_now.hour
    for k, v in REMIND_CONFIG.items():
        s, e = v["time_range"]
        if (s < e and s <= h < e) or (s > e and (h >= s or h < e)):
            return v
    return {"first_text":"💌 专属小提醒","keyword1":"日常问候"}

# 发送消息
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
remind = get_remind_info()
data = {
    "first": {"value": remind["first_text"], "color": get_random_color()},
    "keyword1": {"value": remind["keyword1"], "color": "#FF6347"},
    "keyword2": {"value": get_weather(), "color": "#1E90FF"},
    "remark": {"value": f"距离生日还有{get_birthday()}天\n{get_words()}", "color": get_random_color()}
}

# 双人发送
for uid in user_id_list:
    res = wm.send_template(uid, template_id, data)
    print(f"发送成功：{remind['keyword1']} | {res}")
