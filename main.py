import cityinfo
import config
import time
from time import localtime
from requests import get, post
from datetime import datetime, date


# 微信获取token
def get_access_token():
    # appId
    app_id = config.app_id
    # appSecret
    app_secret = config.app_secret
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    print(get(post_url).json())
    access_token = get(post_url).json()['access_token']
    # print(access_token)
    return access_token


# 获取城市天气
def get_weather(province, city):
    # 城市id
    city_id = cityinfo.cityInfo[province][city]["AREAID"]
    # city_id = 101280101
    # 毫秒级时间戳
    t = (int(round(time.time() * 1000)))
    headers = {
        "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]
    return weather, temp, tempn


# 获取今天是第几周，返回字符串
def get_Today_Week():
    y = config.year
    m = config.month
    d = config.day
    startWeek = datetime(y, m, d)
    today = datetime.today()
    d_days = today - startWeek
    trueWeek = (d_days.days // 7) + 1
    return str(trueWeek)


# 获取本周课程
def get_Week_Classes(w):
    if w is not None:
        week_Class = config.classes.get(w)
    else:
        week = get_Today_Week()
        week_Class = config.classes.get(week)
    return week_Class


# 获取今日课程
def get_Today_Class():
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    todayClasses = get_Week_Classes("1")[today.weekday()]
    return todayClasses


# 获取指定星期几的课程
def get_Class(day):
    theClasses = get_Week_Classes(None)[day]
    return theClasses


# # 发送本周所有课程，周一的时候发
# def send_Week_Classes(to_user, access_token, week):
#     url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
#     theuser = to_user[0]
#     data = {
#         "touser": theuser,
#         "template_id": config.template_id2,
#         "url": "http://weixin.qq.com/download",
#         "topcolor": "#FF0000",
#         "data": {
#             "weeks": {
#                 "value": classInfo,
#                 "color": "#FF8000"
#             }
#         }
#     }
#     headers = {
#         'Content-Type': 'application/json',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
#     }
#     response = post(url, headers=headers, json=data)
#     print(response.text)


# 发送每日信息
def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    # 星期几
    week = week_list[today.weekday()]
    # 开学的第几周
    weeks = get_Today_Week()
    # # 获取在一起的日子的日期格式
    # love_year = int(config.love_date.split("-")[0])
    # love_month = int(config.love_date.split("-")[1])
    # love_day = int(config.love_date.split("-")[2])
    # love_date = date(love_year, love_month, love_day)
    # # 获取在一起的日期差
    # love_days = str(today.__sub__(love_date)).split(" ")[0]
    # # 获取生日的月和日
    # birthday_month = int(config.birthday.split("-")[1])
    # birthday_day = int(config.birthday.split("-")[2])
    # # 今年生日
    # year_date = date(year, birthday_month, birthday_day)
    # # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    # if today > year_date:
    #     birth_date = date((year + 1), birthday_month, birthday_day)
    #     birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    # elif today == year_date:
    #     birth_day = 0
    # else:
    #     birth_date = year_date
    #     birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    #增加问候语
    if "雪" in weather or "雨" in weather or "雷" in weather:
        notes = "有雨雪天气，宝要记得带伞哦！"
    elif "雾" in weather or "尘" in weather:
        notes = "看不太清路呢，宝谨慎出行……"
    elif "霾" in weather:
        notes = "空气质量不好，宝要记得戴口罩！"
    elif "阴" in weather:
        notes = "向日葵是不行了，今天得用阳光菇（x"
    elif "云" in weather:
        notes = "欢迎来到云难"
    elif "晴" in weather:
        notes = "🌻🌻🌻"
    else :
        notes = "WARNING:什么怎么还有我没考虑到的天气，请私聊客服debug"
    if int(max_temperature[:-1]) - int(min_temperature[:-1]) >= 10:
        notes2 = "昼夜温差好大，注意及时增减衣物，要不然……会变甜！"
    elif int(min_temperature[:-1]) <= 3:
        notes2 = "今天最低温度比较低，也要记得穿暖和点~"
    elif int(max_temperature[:-1]) >= 30:
        notes2 = "热……要热成小狗了！"
    else :
        notes2 = "  ღ( ´･ᴗ･` )"
    theClass = get_Today_Class()
    theuser = to_user[0]
    data = {
        "touser": theuser,
        "template_id": config.template_id1,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "weeks": {
                "value": weeks,
                "color": "#00FFFF"
            },
            "date": {
                "value": "{} {}".format(today, week),
                "color": "#00FFFF"
            },
            "city": {
                "value": city_name,
                "color": "#808A87"
            },
            "weather": {
                "value": weather,
                "color": "#ED9121"
            },
            "notes":{
                "value": notes,
                "color": "#87CEEB"
            },
            "notes2":{
                "value": notes2,
                "color": "#87CEEB"
            },
            "min_temperature": {
                "value": min_temperature,
                "color": "#00FF00"
            },
            "max_temperature": {
                "value": max_temperature,
                "color": "#FF6100"
            },
            # "love_day": {
            #     "value": love_days,
            #     "color": "#87CEEB"
            # },
            # "birthday": {
            #     "value": birth_day,
            #     "color": "#FF8000"
            # },
            "firstClass": {
                "value": theClass[0],
                "color": "#FF8000"
            },
            "secondClass": {
                "value": theClass[1],
                "color": "#FF8000"
            },
            "thirdClass": {
                "value": theClass[2],
                "color": "#FF8000"
            },
            "fourthClass": {
                "value": theClass[3],
                "color": "#FF8000"
            },
            "fifthClass": {
                "value": theClass[4],
                "color": "#FF8000"
            },
            "sixthClass": {
                "value": theClass[5],
                "color": "#FF8000"
            }
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data)
    print(response.text)


# 发送课程消息
def send_Class_Message(to_user, access_token, classInfo):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    theuser = to_user[0]
    data = {
        "touser": theuser,
        "template_id": config.template_id2,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "classInfo": {
                "value": classInfo,
                "color": "#FF8000"
            }
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data)
    print(response.text)


# 发送晚安心语及第二天课程
def send_Good_Night(to_user, access_token):
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    # 获取天行数据晚安心语
    txUrl = "http://api.tianapi.com/wanan/index"
    key = config.good_Night_Key
    pre_data = {"key": key}
    # param = json.dumps((pre_data))
    r = post(txUrl, params=pre_data, headers=headers)
    print("r:", r.text)
    good_Night = r.json()["newslist"][0]["content"]
    # good_Night = "晚安"
    # 获取第二天课表
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    weekClasses = get_Week_Classes(None)
    week = week_list[(today.weekday() + 1) % 7]
    theClass = []
    if (today.weekday() + 1) % 7 == 0:
        weekClasses = get_Week_Classes(get_Today_Week())
        theClass = weekClasses[0]
    else:
        theClass = weekClasses[today.weekday() + 1]

    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    theuser = to_user[0]
    data = {
        "touser": theuser,
        "template_id": config.template_id3,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "goodNight": {
                "value": good_Night,
                "color": "#87CEEB"
            },
            "week": {
                "value": week,
                "color": "#00FFFF"
            },
            "firstClass": {
                "value": theClass[0],
                "color": "#FF8000"
            },
            "secondClass": {
                "value": theClass[1],
                "color": "#FF8000"
            },
            "thirdClass": {
                "value": theClass[2],
                "color": "#FF8000"
            },
            "fourthClass": {
                "value": theClass[3],
                "color": "#FF8000"
            },
            "fifthClass": {
                "value": theClass[4],
                "color": "#FF8000"
            },
            "sixthClass": {
                "value": theClass[5],
                "color": "#FF8000"
            }
        }
    }
    response = post(url, headers=headers, json=data)
    print(response.text)


# 计算时间间隔
def calculate_Time_Difference(t1, t2):
    h1 = int(t1[0:2])
    h2 = int(t2[0:2])
    m1 = int(t1[3:5])
    m2 = int(t2[3:5])
    s1 = int(t1[6:8])
    s2 = int(t2[6:8])
    d1 = datetime(2022, 1, 1, h1, m1, s1)
    d2 = datetime(2022, 1, 1, h2, m2, s2)
    return (d1 - d2).seconds


if __name__ == '__main__':
    # 获取accessToken
    accessToken = get_access_token()
    print('token', accessToken)
    # 接收的用户
    user = config.user
    print('user:', user)
    # 传入省份和市获取天气信息
    province, city = config.province, config.city
    weather, max_temperature, min_temperature = get_weather(province, city)
    isPost = False
    # 公众号推送消息
    if datetime.now().strftime('%H:%M:%S') < config.post_Time:
        send_message(user, accessToken, city, weather, max_temperature, min_temperature)
        isPost = True
    # 课程提醒推送
    # todayClasses = get_Today_Class()
    # time_table = config.time_table
    # for i in range(len(time_table)):
    #     if isPost:
    #         break
    #     reminderTime = time_table[i]
    #     while True:
    #         nowTime = datetime.now().strftime('%H:%M:%S')
    #         print("当前时间:", nowTime)
    #         if reminderTime == nowTime:
    #             if len(todayClasses[i]) != 0:
    #                 classInfo = "课程信息: " + todayClasses[i] + "\n" + "上课时间: " + config.course_Time[i] + "\n"
    #                 print(classInfo)
    #                 send_Class_Message(user, accessToken, classInfo)
    #                 print("课程信息推送成功！")
    #             isPost = True
    #             break
    #         elif reminderTime < nowTime:
    #             break
    #         # 通过睡眠定时
    #         defference = calculate_Time_Difference(reminderTime, nowTime) - 3
    #         print("课程推送时间差：", defference, "秒")
    #         if defference > 0:
    #             print("开始睡眠: 等待推送第", i + 1, "讲课")
    #             time.sleep(defference)
    #             print("结束睡眠")
    # while True:
    #     goodNightTime = config.good_Night_Time
    #     nowTime = datetime.now().strftime('%H:%M:%S')
    #     if goodNightTime == nowTime:
    #         # 发送晚安心语
    #         send_Good_Night(user, accessToken)
    #         print("晚安心语推送成功！")
    #         break
    #     elif goodNightTime < nowTime:
    #         print("当前时间已过晚安心语推送设置的时间！")
    #         break
    #     elif calculate_Time_Difference(goodNightTime, nowTime) > 120:
    #         break
    #     # 通过睡眠定时
    #     defference = calculate_Time_Difference(goodNightTime, nowTime) - 3
    #     print("晚安心语推送时间差：", defference, "秒")
    #     if defference > 0:
    #         print("开始睡眠:等待推送晚安心语")
    #         time.sleep(defference)
    #         print("结束睡眠")
