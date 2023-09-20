import os
import json
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse as parsedate
from time import sleep

OUTPUT_FILE = "guest_accounts.json"
LAST_ATTEMPT_FILE = "last_guest_attempt"
CREATE_INTERVAL = timedelta(hours=24, minutes=5)
WAIT_INTERVAL = timedelta(minutes=55)
PRUNE_INTERVAL = timedelta(days=30)

BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F"
BASIC_HEADERS = {
    "Authorization": BEARER_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "TwitterAndroid/9.95.0-release.0 (29950000-r-0) ONEPLUS+A3010/9 (OnePlus;ONEPLUS+A3010;OnePlus;OnePlus3;0;;1;2016)",
    "X-Twitter-API-Version": "5",
    "X-Twitter-Client": "TwitterAndroid",
    "X-Twitter-Client-Version": "9.95.0-release.0",
    "OS-Version": "28",
    "System-User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ONEPLUS A3010 Build/PKQ1.181203.001)",
    "X-Twitter-Active-User": "yes",
}
SUBTASK_VERSIONS = {
    "generic_urt": 3,
    "standard": 1,
    "open_home_timeline": 1,
    "app_locale_update": 1,
    "enter_date": 1,
    "email_verification": 3,
    "enter_password": 5,
    "enter_text": 5,
    "one_tap": 2,
    "cta": 7,
    "single_sign_on": 1,
    "fetch_persisted_data": 1,
    "enter_username": 3,
    "web_modal": 2,
    "fetch_temporary_password": 1,
    "menu_dialog": 1,
    "sign_up_review": 5,
    "interest_picker": 4,
    "user_recommendations_urt": 3,
    "in_app_notification": 1,
    "sign_up": 2,
    "typeahead_search": 1,
    "user_recommendations_list": 4,
    "cta_inline": 1,
    "contacts_live_sync_permission_prompt": 3,
    "choice_selection": 5,
    "js_instrumentation": 1,
    "alert_dialog_suppress_client_events": 1,
    "privacy_options": 1,
    "topics_selector": 1,
    "wait_spinner": 3,
    "tweet_selection_urt": 1,
    "end_flow": 1,
    "settings_list": 7,
    "open_external_link": 1,
    "phone_verification": 5,
    "security_key": 3,
    "select_banner": 2,
    "upload_media": 1,
    "web": 2,
    "alert_dialog": 1,
    "open_account": 2,
    "action_list": 2,
    "enter_phone": 2,
    "open_link": 1,
    "show_code": 1,
    "update_users": 1,
    "check_logged_in_account": 1,
    "enter_email": 2,
    "select_avatar": 4,
    "location_permission_prompt": 2,
    "notifications_permission_prompt": 4,
}


def make_request():
    with requests.Session() as session:
        guest_token = session.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={
                "Authorization": BEARER_TOKEN,
            },
        ).json()["guest_token"]
        flow_token = session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?flow_name=welcome&api_version=1&known_device_token=&sim_country_code=us",
            headers={
                **BASIC_HEADERS,
                "X-Guest-Token": guest_token,
            },
            data=json.dumps(
                {
                    "flow_token": None,
                    "input_flow_data": {
                        "country_code": None,
                        "flow_context": {
                            "start_location": {"location": "splash_screen"}
                        },
                        "requested_variant": None,
                        "target_user_id": 0,
                    },
                    "subtask_versions": SUBTASK_VERSIONS,
                }
            ),
        ).json()["flow_token"]
        response = session.post(
            "https://api.twitter.com/1.1/onboarding/task.json",
            headers={
                **BASIC_HEADERS,
                "X-Guest-Token": guest_token,
            },
            data=json.dumps(
                {
                    "flow_token": flow_token,
                    "subtask_inputs": [
                        {
                            "open_link": {
                                "link": "next_link",
                            },
                            "subtask_id": "NextTaskOpenLink",
                        }
                    ],
                    "subtask_versions": SUBTASK_VERSIONS,
                }
            ),
        )
    return response


def main():
    #last_attempt_time = None
    #if os.path.exists(LAST_ATTEMPT_FILE):
    #    with open(LAST_ATTEMPT_FILE) as last_attempt_file:
    #        last_attempt_time = json.load(last_attempt_file)["Time"]
    #if (
    #    last_attempt_time
    #    and (time_diff := datetime.now() - parsedate(last_attempt_time))
    #    <= CREATE_INTERVAL
    #):
    #    if CREATE_INTERVAL - time_diff <= WAIT_INTERVAL:
    #        sleep(int((CREATE_INTERVAL - time_diff).total_seconds()))
    #    else:
    #        return
    response = make_request()
    if new_account := response.json().get("subtasks", [{}])[0].get("open_account"):
        new_account["creation_time"] = f"{datetime.now()}"
        account_list = []
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE) as accounts_file:
                account_list = json.load(accounts_file)
        if PRUNE_INTERVAL:
            to_prune = 0
            for account in account_list:
                if (
                    creation_time := account.get("creation_time")
                ) and datetime.now() - parsedate(creation_time) < PRUNE_INTERVAL:
                    break
                to_prune += 1
            account_list = account_list[to_prune:]
        account_list.append(new_account)
        with open(OUTPUT_FILE, "w") as accounts_file:
            json.dump(account_list, accounts_file, indent=4)
    #with open(LAST_ATTEMPT_FILE, "w") as last_attempt_file:
    #    json.dump(
    #        {"Success": bool(new_account), "Time": f"{datetime.now()}"},
    #        last_attempt_file,
    #    )


if __name__ == "__main__":
    main()
