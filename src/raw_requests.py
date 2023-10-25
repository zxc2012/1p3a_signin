import json
import random
import time
import requests
import re
import xml.dom.minidom as xml
import lxml.html as html
import questions
from sys import exit
import http.cookies

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77"
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

referer = "https://www.1point3acres.com/bbs/"

default_site_key = "6LeCeskbAAAAAE-5ns6vBXkLrcly-kgyq6uAriBR"
get_login_url_v2 = "https://auth.1point3acres.com/"
login_site_key_v2 = "6LewCc8ZAAAAAOu08V7c-IYrzICepKEQFFX401py"

get_login_url = "https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login"
# login_url = "https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
# login_url = "https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
login_url = "https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login&loginhash=%s&inajax=1"

cf_capcha_site_key = "0x4AAAAAAAA6iSaNNPWafmlz"

checkin_page = "https://www.1point3acres.com/next/daily-checkin"
post_checkin_url = "https://api.1point3acres.com/api/users/checkin"

question_page = "https://www.1point3acres.com/next/daily-question"
post_answer_url = "https://api.1point3acres.com/api/daily_questions"

session = requests.Session()

def getcaptcha(sitekey: str = "",url: str = "",clientKey: str = ""):
    try:
        # 发送JSON格式的数据
        result = requests.post('https://api.yescaptcha.com/createTask', json={
            "clientKey": clientKey,
            "task": {
                "websiteURL": url,
                "websiteKey": sitekey,
                "type": 'TurnstileTaskProxyless'
            }
        }, verify=False).json()
        taskId = result.get('taskId')
        if taskId is not None:
            times = 0
            while times < 120:
                data = {
                    "clientKey": clientKey,
                    "taskId": taskId
                }
                result = requests.post('https://api.yescaptcha.com/getTaskResult', json=data, verify=False).json()
                solution = result.get('solution', {})
                if solution:
                    response = solution.get('token')
                    if response:
                        return response

                times += 15
                time.sleep(15)
        else:
            print("No taskID")
        
    except Exception as e:
        print(e)
        exit(-1)


def save_error(response: requests.Response, error_desc: str = ""):
    print(f"{error_desc} 未知错误，查看tmp.html，了解详情")
    # content 是字节
    # text 是字符串
    # f = open("tmp.html", "w", encoding="utf-8")
    # f.write(response.text)
    f = open("tmp.html", "wb")
    f.write(response.content)
    f.close()


def check_status_code(response: requests.Response, error_desc: str = ""):
    if response.status_code != 200:
        print(f"{error_desc} error: status code is {response.status_code}")
        print(response.content)
        exit(-1)


def login_cookie(cookie: str) -> bool:
    global session
    session = requests.session()
    session.cookies.update(http.cookies.SimpleCookie(cookie))
    return True


def get_login_info_() -> (str, str):
    global session
    header = {
        "User-Agent": user_agent,
        "Referer": referer,
    }
    session = requests.session()
    response = session.get("https://www.1point3acres.com/bbs/", headers=header)
    if (response.status_code == 503):
        print("stop by cloudflare", response.status_code)
        exit(-1)
    if (response.status_code != 200):
        print("wrong status code: ", response.status_code)
        exit(-1)

    response = session.get(get_login_url_v2, headers=header)
    check_status_code(response, "get login info")
    pattern = re.compile('input id="csrf_token" name="csrf_token" type="hidden" value="([^"]+)"')
    csrf_tokens = pattern.findall(response.text)
    csrf_token = ""
    if len(csrf_tokens) >= 1:
        csrf_token = csrf_tokens[0]
    else:
        save_error(response, "csrf_token not found")
        exit(-1)
    return csrf_token

def get_checkin_info_() -> (bool):
	header = {
		"User-Agent": user_agent,
	}
	response = session.get(checkin_page, headers=header)
	check_status_code(response, "get checkin info")
	if "今日已签到" in response.text:
		print("已签到")
		return False
	if "请登录后进行签到" in response.text:
		print("cookie无效 或者用户名密码错误")
		exit(-1)
		return True
	return True

def do_daily_checkin_(solver) -> bool:
    header = {
        "User-Agent": user_agent,
        "Content-Type": "application/json",
        "Referer": referer
    }
        
    captcha = getcaptcha(
        sitekey=cf_capcha_site_key,
        url=checkin_page,
        clientKey=solver
    )

    emoji_list = ['kx', 'ng', 'ym', 'wl', 'nu', 'ch', 'fd', 'yl', 'shuai']

    if captcha is not None:
        body = {
            "qdxq": random.choice(emoji_list),
            "todaysay": "你好啊",
            "captcha_response": captcha,
            "hashkey": "",
            "version": 2
        }

        response = session.post(post_checkin_url, headers=header, data=json.dumps(body))
        #print(response.status_code)
        #print(response.text)
        check_status_code(response, "daily checkin")
        if "人机验证出错，请重试" in response.text:
            print("验证码错误")
            return False

        result = json.loads(response.text)
        print(result["msg"])
        if (result["errno"] == 0):  # 成功
            return True
        elif (result["msg"] == "您今天已经签到过了"):
            return True
        else:
            print(result)
            return False
    else:
        print("验证码失误")
        exit(-1)



# 需要登录
def get_daily_task_answer() -> (int, int):
    print("get question...")
    header = {
        "User-Agent": user_agent,
        "Referer": referer
    }
    response = session.get(post_answer_url, headers=header)
    check_status_code(response, "get daily question")
    resp_json = json.loads(response.text)
    if resp_json["errno"] != 0 or resp_json["msg"] != "OK":
        print(response.text)
        return None
    

    question_id = resp_json["question"]["id"]
    question = resp_json["question"]["qc"]
    question = question.strip()
    print(f"question: {question}")
    answers = {}
    answers[1] = resp_json["question"]["a1"]
    answers[2] = resp_json["question"]["a2"]
    answers[3] = resp_json["question"]["a3"]
    answers[4] = resp_json["question"]["a4"]
    print(f"answers: {answers}")
    answer = ""
    answer_id = 0
    if question in questions.questions.keys():
        answer = questions.questions[question]
        if type(answer) == list:
            for k in answers:
                if answers[k] in answer:
                    print(f"find answer: {answers[k]} option value: {k} ")
                    answer_id = k
        else:
            for k in answers:
                if answers[k] == answer:
                    print(f"find answer: {answers[k]} option value: {k} ")
                    answer_id = k
        if answer_id == "":
            print(f"answer not found: {answer}")
    else:
        print("question not found")
        return None
    return (question_id, answer_id)



def do_daily_question_(question: int, answer: int, solver) -> bool:
    header = {
        "User-Agent": user_agent,
        "Referer": referer,
		"Content-Type": "application/json",
    }

    captcha = getcaptcha(
        sitekey=cf_capcha_site_key,
        url=question_page,
        clientKey= solver
    )
    if captcha is not None: 
        body = {
            "qid": question,
            "answer": answer,
            "captcha_response": captcha,
            "hashkey": "",
            "version": 2
        }
        # 网站的原版请求是 multipart/form-data ，但是我发现用 application/x-www-form-urlencoded 也是可以的
        # response = scraper.post(post_answer_url, files=body, headers=header, cookies=cookie_jar)
        # response = requests.post(post_answer_url, data=body, headers=header, cookies=cookie_jar)
        response = session.post(post_answer_url, data=json.dumps(body), headers=header)
        check_status_code(response, "post answer")

        if "人机验证出错，请重试" in response.text:
            print("验证码错误")
            return False

        result = json.loads(response.text)
        print(result["msg"])
        if (result["errno"] == 0):  # 成功
            return True
        elif (result["msg"] == "您今天已经答过题了"):
            return True
        else:
            print(response.text)
            return False