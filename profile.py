# netflix_posts_2025.py
# Run: python3 netflix_posts_2025.py
# ΓåÆ Saves ALL post shortcodes to <username>_postid.txt

import requests, json, time, re
from cookies_headers import COOKIES, HEADERS  # <--- load from external file

DOC_ID = "25461702053427256"  # Current Polaris query ID (Nov 2025)

def scrape_profile(username):
    """Scrape all post shortcodes for a username"""
    def get_posts(after=None):
        variables = {
            "username": username,
            "first": 50,
            "data": {
                "count": 50,
                "include_reel_media_seen_timestamp": True,
                "include_relationship_info": True,
                "latest_besties_reel_media": True,
                "latest_reel_media": True
            },
            "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True
        }
        if after:
            variables["after"] = after

        payload = {
            'variables': json.dumps(variables),
            'doc_id': DOC_ID,
            'fb_dtsg': 'NAfsdGpQ8B1C8aSW9ZBSQw7gpZMByeVd3CjWCQ8AUqxG51UlPCIlgwA:17843709688147332:1757617690',
            'lsd': 'YOvULOO686BEKESSLvSL9H',
            'jazoest': '26113',
        }

        r = requests.post(
            "https://www.instagram.com/graphql/query",
            headers=HEADERS,
            cookies=COOKIES,
            data=payload
        )
        return r.json()

    print(f"Dumping ALL @{username} posts...")
    output_file = f"{username}_postid.txt"
    with open(output_file, "w") as f:
        cursor = None
        total = 0
        while True:
            data = get_posts(cursor)
            edges = data['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges']
            
            for edge in edges:
                shortcode = edge['node']['code']
                f.write(shortcode + "\n")
                total += 1

            print(f"Saved {total} posts...", end="\r")

            page_info = data['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['page_info']
            if not page_info['has_next_page']:
                break
            cursor = page_info['end_cursor']
            time.sleep(2)

    print(f"\nDONE! {total} post IDs ΓåÆ {output_file}")
    return output_file

if __name__ == "__main__":
    USERNAME = input("Enter Instagram username: ").strip()
    scrape_profile(USERNAME)

