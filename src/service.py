import time
from tokenize import cookie_re
from raw_requests import *
import os

def daily_checkin(solver) -> bool:
    print("do daily checkin...")
    checkin_status = get_checkin_info_()
    if checkin_status == False:
        return False
    time.sleep(2)
    # token = get_g_token(api_key, get_checkin_url, other_site_key)
    # if token == "":
    #     return False
    return do_daily_checkin_(solver)


def daily_question(solver) -> bool:
	print("do daily question...")
	r = get_daily_task_answer()
	if r == None:
		return False
	time.sleep(2)
	return do_daily_question_(question=r[0], answer=r[1], solver=solver)

def main():
    fp = open("./configure/cookie.json")
    data = json.load(fp)
    users = data["users"]
    api_key = data["api_key"]
    cookie = users[0]["cookie"]
    if cookie is not None or api_key is not None :
        login_cookie(cookie)
        daily_checkin(api_key)
        daily_question(api_key)
    else:
        print("Secrets 未配置!")


if __name__ == "__main__":
    main()
