#!/usr/bin/env python3
import requests
import re
import json
import sys
import time

# --- Configuration ---
COOKIES = {
    "datr": "qzKzaOz9fDiEPLiRbP1Fdz10",
    "ig_did": "95870518-8550-4D46-B309-EDDCDB32CD22",
    "ig_nrcb": "1",
    "ds_user_id": "46104552194",
    "ps_l": "1",
    "ps_n": "1",
    "mid": "aOVVwAALAAGPAOoe10zwPpiWGHfM",
    "csrftoken": "mzbsp7xF9esRJT5hHw7WLLpeYzxfloEK",
    "dpr": "1.25",
    "rur": '"CCO,46104552194,1793829314:01fe79f5512fee12844071f3b76a19e414d317f7c500a531c1b0377b9b6d4f3079fb49e3"',
    "sessionid": "46104552194%3A1paujJtdmO83D5%3A28%3AAYg8xsBjAihoaeJaiF4lLjuFI5hsyTwrZxjgBjNL-QM",
    "wd": "447x826"
}

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,hi;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.instagram.com",
    "priority": "u=1, i",
    "referer": "https://www.instagram.com/",
    "sec-ch-prefers-color-scheme": "dark",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="141.0.7390.125", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.125"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"19.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "x-asbd-id": "359341",
    "x-bloks-version-id": "d472af6df5cc606197723ed51adaa0886f926161310654a7c93600790814eba5",
    "x-csrftoken": "mzbsp7xF9esRJT5hHw7WLLpeYzxfloEK",
    "x-fb-friendly-name": "PolarisProfilePageContentQuery",
    "x-fb-lsd": "cQeWn0Q5h873fMiNiaB59L",
    "x-ig-app-id": "936619743392459",
    "x-root-field-name": "fetch__XDTUserDict"
}


def get_user_id(username):
    url = f"https://www.instagram.com/{username}/"
    resp = requests.get(url, headers=HEADERS, cookies=COOKIES)
    if resp.status_code != 200:
        print(f"❌ Failed to load {username}: HTTP {resp.status_code}")
        return None

    match = re.search(r'"target_id":"(\d+)"', resp.text)
    if not match:
        print(f"⚠️ Could not find user_id for {username}")
        return None

    return match.group(1)


def get_profile_info(username, user_id):
    url = "https://www.instagram.com/graphql/query"
    doc_id = "24963806849976236"

    variables = {
        "enable_integrity_filters": True,
        "id": user_id,
        "render_surface": "PROFILE",
        "__relay_internal__pv__PolarisProjectCannesEnabledrelayprovider": True,
        "__relay_internal__pv__PolarisProjectCannesLoggedInEnabledrelayprovider": True,
        "__relay_internal__pv__PolarisCannesGuardianExperienceEnabledrelayprovider": True,
        "__relay_internal__pv__PolarisCASB976ProfileEnabledrelayprovider": False,
        "__relay_internal__pv__PolarisRepostsConsumptionEnabledrelayprovider": False
    }

    data = {
        "av": "17841446085823069",
        "__d": "www",
        "__user": "0",
        "__a": "1",
        "__req": "2",
        "__hs": "20396.HYP:instagram_web_pkg.2.1...0",
        "dpr": "1",
        "__ccg": "GOOD",
        "__rev": "1029384238",
        "__s": "nxa7io:f9zpir:ahz0jz",
        "__hsi": "7568992210495101128",
        "fb_api_req_friendly_name": "PolarisProfilePageContentQuery",
        "server_timestamps": "true",
        "doc_id": doc_id,
        "variables": json.dumps(variables)
    }

    headers = HEADERS.copy()
    headers["referer"] = f"https://www.instagram.com/{username}/"
    headers["x-csrftoken"] = COOKIES["csrftoken"]

    resp = requests.post(url, headers=headers, cookies=COOKIES, data=data)
    if resp.status_code != 200:
        print(f"❌ GraphQL failed for {username}: HTTP {resp.status_code}")
        return None

    try:
        js = resp.json()
        user = js["data"]["user"]
        return {
            "username": user.get("username"),
            "full_name": user.get("full_name"),
            "is_private": user.get("is_private"),
            "biography": user.get("biography"),
            "follower_count": user.get("follower_count"),
            "following_count": user.get("following_count")
        }
    except Exception as e:
        print(f"⚠️ Parse error for {username}: {e}")
        return None


if __name__ == "__main__":
    input_file = "usernames.txt"
    output_file = "output.json"

    try:
        usernames = [u.strip().lower() for u in open(input_file) if u.strip()]
    except FileNotFoundError:
        print(f"❌ Input file '{input_file}' not found.")
        sys.exit(1)

    results = []

    for username in usernames:
        print(f"\n🔍 Processing @{username}...")
        user_id = get_user_id(username)
        if not user_id:
            continue

        info = get_profile_info(username, user_id)
        if info:
            results.append(info)
            print(f"✅ Done: {info['username']} — Followers: {info['follower_count']}")
        else:
            print(f"⚠️ Skipped {username}")

        time.sleep(2)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n📁 Saved {len(results)} profiles to '{output_file}' successfully!")

