import time
from raw_requests import *
import os

def daily_checkin(solver) -> bool:
    print("do daily checkin...")
    form_hash, sec_hash = get_checkin_info_()
    if form_hash == "":
        return False
    time.sleep(2)
    # token = get_g_token(api_key, get_checkin_url, other_site_key)
    # if token == "":
    #     return False
    return do_daily_checkin_(solver, form_hash=form_hash, sec_hash=sec_hash)


def daily_question(solver) -> bool:
    print("do daily question...")
    answer, form_hash, sec_hash, = get_daily_task_answer()
    time.sleep(2)
    if form_hash == "" or answer == "":
        return False
    # token = get_g_token(api_key, get_checkin_url)
    # if token == "":
    #     return False
    return do_daily_question_(answer=answer, solver=solver, form_hash=form_hash, sec_hash=sec_hash)

def main():
    cookie = os.getenv("cookie")
    api_key = os.getenv("api_key")
    if cookie is not None or api_key is not None :
        login_cookie(cookie)
        daily_checkin(api_key)
        daily_question(api_key)
    else:
        print("Secrets 未配置!")


if __name__ == "__main__":
    main()
