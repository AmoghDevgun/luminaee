#!/usr/bin/env python3
import requests
import json
import time
from cookies_headers import COOKIES, HEADERS  # same format as before

# --- Constants ---
URL = "https://www.instagram.com/graphql/query"
DOC_ID = "25060748103519434"  # Current Polaris Post Comments Query ID

# --- Prepare Headers ---
HEADERS = HEADERS.copy()
HEADERS["x-fb-friendly-name"] = "PolarisPostCommentsPaginationQuery"
HEADERS["x-ig-app-id"] = "936619743392459"
HEADERS["content-type"] = "application/x-www-form-urlencoded"

# --- GraphQL Query Variables ---
def make_variables(media_id, after_cursor=None):
    variables = {
        "after": after_cursor,
        "before": None,
        "first": 20,
        "last": None,
        "media_id": media_id,
        "sort_order": "popular",
        "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True
    }
    return json.dumps(variables)

# --- Fetch a single page of comments ---
def fetch_comments(media_id, after=None):
    payload = {
        "fb_api_req_friendly_name": "PolarisPostCommentsPaginationQuery",
        "variables": make_variables(media_id, after),
        "doc_id": DOC_ID,
    }

    try:
        res = requests.post(URL, headers=HEADERS, cookies=COOKIES, data=payload, timeout=15)
        if res.status_code != 200:
            print("HTTP Error:", res.status_code)
            return None
        return res.json()
    except Exception as e:
        print(f"[!] Request failed for media {media_id}: {e}")
        return None

# --- Collect all comments for one media ---
def collect_comments_for_media(media_id):
    all_comments = []
    after = None
    page = 1

    while True:
        print(f"\n[*] Fetching comments (page {page}) for media ID {media_id}...")
        data = fetch_comments(media_id, after)
        if not data:
            break

        try:
            comments_data = data["data"]["xdt_api__v1__media__media_id__comments__connection"]
            edges = comments_data.get("edges", [])
        except Exception as e:
            print(f"[!] Parse error for media {media_id}: {e}")
            break

        for edge in edges:
            node = edge["node"]
            user = node.get("user", {})
            comment = {
                "media_id": media_id,
                "username": user.get("username", ""),
                "text": node.get("text", ""),
                "likes": node.get("comment_like_count", 0),
                "created_at": node.get("created_at", 0)
            }
            all_comments.append(comment)

        page_info = comments_data.get("page_info", {})
        has_next = page_info.get("has_next_page", False)
        after = page_info.get("end_cursor")

        print(f"    → Collected {len(edges)} new comments, total {len(all_comments)} so far...")

        if not has_next or not after:
            print(f"[+] Done fetching comments for media {media_id}.\n")
            break

        page += 1
        time.sleep(2)

    return all_comments

def scrape_comments(filename, output_file="comments.json"):
    """Scrape comments from media IDs file"""
    # --- Load Media IDs File ---
    try:
        with open(filename, "r") as f:
            media_entries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

    if not media_entries:
        print("File is empty or invalid.")
        return None

    # --- Main Execution ---
    print(f"[*] Processing {len(media_entries)} media IDs...\n")
    all_comments = []

    for entry in media_entries:
        parts = entry.split(":")
        if len(parts) != 2:
            print(f"[!] Invalid line format: {entry}")
            continue

        shortcode, media_id = parts
        comments = collect_comments_for_media(media_id)
        all_comments.extend(comments)
        time.sleep(2)

    # --- Save results ---
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! Saved {len(all_comments)} comments → {output_file}")
    return output_file

if __name__ == "__main__":
    filename = input("Enter filename containing media IDs: ").strip()
    scrape_comments(filename)

