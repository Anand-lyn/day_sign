import requests
import os
import logging

# 组要变量
TOKEN = os.getenv("TOKEN").strip() if os.getenv("TOKEN") is not None else ''
SESSION = os.getenv("SESSION").strip() if os.getenv("SESSION") is not None else ''
ADDRESS = os.getenv("ADDRESS").strip() if os.getenv("ADDRESS") is not None else ''
PUBLISH_KEY = os.getenv("PUBLISH_KEY").strip() if os.getenv("PUBLISH_KEY") is not None else ''

host = "https://student.wozaixiaoyuan.com"
# 请求头部信息
headers = {
    "Host": "student.wozaixiaoyuan.com",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 "
                  "Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
    "Referer": "https://servicewechat.com/wxce6d08f781975d91/147/page-frame.html",
    "Cookie": f"SESSION={SESSION}; path=/; HttpOnly",
    "token": f"{TOKEN}"
}

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    filename='current.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def getAddr(addr):
    keys = ['latitude', 'longitude', 'country', 'province', 'city', 'district']
    return dict(zip(keys, addr.split('|')))

def healthy():
    url = "/health/getToday.json"
    res = requests.post(host + url, headers=headers).json()
    if res['code'] != 0:
        logger.error(f'异常错误:{res}')
        return False
    country = res['data'].get('country')
    if country == '' or country is None:
        logger.info(f'开始健康打卡')
        return saveHealth()
    else:
        logger.error(f'已打卡,跳过健康打卡')
        return True


def saveHealth():
    url = "/health/save.json"
    headers["content-type"] = "application/x-www-form-urlencoded"
    data = {
        "answers": '["0","0","2"]',
        "latitude": addressData['latitude'],
        "longitude": addressData['longitude'],
        "country": addressData['country'],
        "city": addressData['city'],
        "district": addressData['district'],
        "province": addressData['province']
    }
    res = requests.post(host + url, headers=headers, data=data).json()
    if res['code'] == 0:
        logger.info(f"健康打卡成功")
        return True
    else:
        logger.error(f"健康打卡失败:{res}")
        return False


def getUserInfo():
    url = '/my/getUserInfo.json'
    res = requests.post(host + url, headers=headers).json()
    data = res.get('data')
    return res['code'] == 0 and data is not None, data


def notify(content, title="我在校园打卡信息"):
    if PUBLISH_KEY is not None or PUBLISH_KEY != '':
        url = f'https://sc.ftqq.com/{PUBLISH_KEY}.send'
        requests.get(url, params={"text": title, "desp": content})
    else:
        print("请输入提醒KEY,开启提醒!!", content)


def funcToStr(b, title=''):
    return f'{title}:成功' if b() else f'{title}:失败'


def main():
    infoOk, userInfo = getUserInfo()
    if infoOk:
        title = f'我在校园 {funcToStr(healthy,"打卡")}'
        with open('./current.txt', 'r') as f:
            result = f"```\n姓名: {userInfo['name']}\n{f.read()}\n```"
    else:
        title = '我在校园打卡信息已过期!'
        result = f'打卡失败,信息过期或错误\n{userInfo}'
    #     发送提醒
    notify(result, title)


if __name__ == "__main__":
    # 格式化地址信息
    addressData = getAddr(ADDRESS)
    main()
