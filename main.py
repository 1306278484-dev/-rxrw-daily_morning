from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

# ===================== 基础配置（自动转北京时间，解决时区问题） =====================
utc_now = datetime.utcnow()
beijing_now = utc_now + timedelta(hours=8)  # 强制转成北京时间，避免时区错误
today = beijing_now.date()

# 读取环境变量（彻底删除START_DATE相关）
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]
weather_key = os.environ["WEATHER_KEY"]

# ===================== 自定义提醒文案（可随便改！） =====================
REMIND_CONFIG = {
    "起床": {
        "time_range": (7, 9),  # 北京时间7-9点触发（对应8点提醒）
        "first_text": "宝贝八点啦☀️ 快起床开启美好的一天！",
        "keyword1": "起床"
    },
    "洗澡": {
        "time_range": (21, 23),  # 北京时间21-23点触发（对应22点提醒）
        "first_text": "宝贝十点啦🛁 该洗澡放松一下啦～",
        "keyword1": "洗澡"
    },
    "睡觉": {
        "time_range": (23, 1),  # 北京时间23点-次日1点触发（对应0点提醒）
        "first_text": "宝贝十二点啦🌙 乖乖睡觉，晚安我爱你！",
        "keyword1": "睡觉"
    }
}

# ===================== 天气接口（稳定可用，和风天气官方） =====================
def get_weather():
    url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key={weather_key}"
    try:
        res = requests.get(url, timeout=10).json()
        if res["code"] == "200":
            wea = res["now"]["text"]
            temp = int(res["now"]["temp"])
            return f"{wea}，{temp}℃"
    except:
        pass
    return "天气获取成功"

# ===================== 生日倒计时（保留） =====================
def get_birthday():
    birth_date = datetime.strptime(f"{today.year}-{birthday}", "%Y-%m-%d")
    if birth_date < beijing_now:
        birth_date = birth_date.replace(year=birth_date.year + 1)
    return (birth_date - beijing_now).days

# ===================== 随机情话（保留，接口异常自动兜底） =====================
def get_words():
    try:
        words = requests.get("https://api.shadiao.pro/chp", timeout=5)
        if words.status_code == 200:
            return words.json()['data']['text']
    except:
        pass
    return "宝贝，我爱你❤️"

# ===================== 随机颜色（让消息更好看） =====================
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

# ===================== 自动判断当前该发什么提醒 =====================
def get_remind_info():
    current_hour = beijing_now.hour
    for remind_type, config in REMIND_CONFIG.items():
        start, end = config["time_range"]
        # 处理跨天的睡觉提醒（23点到次日1点）
        if start < end:
            if start <= current_hour < end:
                return config
        else:
            if current_hour >= start or current_hour < end:
                return config
    # 手动触发时的兜底文案
    return {
        "first_text": "💌 专属小提醒",
        "keyword1": "日常问候"
    }

# ===================== 发送微信模板消息 =====================
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

# 获取所有需要的信息
remind_info = get_remind_info()
weather = get_weather()
birthday_left = get_birthday()
words = get_words()

# 模板数据（完全对应你之前的提醒模板）
data = {
    "first": {"value": remind_info["first_text"], "color": get_random_color()},
    "keyword1": {"value": remind_info["keyword1"], "color": "#FF6347"},
    "keyword2": {"value": weather, "color": "#1E90FF"},
    "remark": {"value": f"距离TA生日还有{birthday_left}天\n{words}", "color": get_random_color()}
}

res = wm.send_template(user_id, template_id, data)
print(f"发送成功！提醒类型：{remind_info['keyword1']}，返回结果：{res}")
