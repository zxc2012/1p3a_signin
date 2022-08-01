import time
import json
from raw_requests import *
import sys



def daily_login_cookie(cookie: str):
    return login_cookie(cookie)

def daily_checkin(solver) -> bool:
    print("do daily checkin...")
    form_hash, sec_hash = get_checkin_info_()
    time.sleep(2)
    if form_hash == "":
        return False
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


def do_all_cookie(solver, cookie: str):
    daily_login_cookie(cookie)
    daily_checkin(solver)
    daily_question(solver)
    return

def main(from_file: bool = False):
    users = []
    api_key = ""
    cookie_file = "../configure/cookie.json"
    if (len(sys.argv) > 1):
        cookie_file = sys.argv[1]
    if os.path.exists(cookie_file):
        fp = open(cookie_file)
        data = json.load(fp)
        users = data["users"]
        api_key = data["api_key"]
        if api_key != "replace_with_your_api_key":
            for user in users:
                do_all_cookie(api_key, user["cookie"])
            return


if __name__ == "__main__":
    main()
