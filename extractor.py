import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TARGET_URL = "https://check0ver.net/en/iapps?filter[inCategories][0]=9c60f563-1983-42f0-8882-a26207bd4aaf"

# ئەگەر ئەکاونتت هەیە دەتوانی کۆکی ئەکاونتەکەت لێرە دابنێیت، ئەگەر نا بە بەتاڵی جێی بهێڵە
SESSION_COOKIE = "" 

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://check0ver.net/en/iapps"
}

if SESSION_COOKIE:
    HEADERS["Cookie"] = SESSION_COOKIE

def get_direct_ipa(uuid):
    download_api = f"https://check0ver.net/api/iapps/{uuid}/download"
    try:
        # پەیوەندی بە سیستەمی داگرتن بۆ وەرگرتنی لینکی کۆتایی
        res = requests.get(download_api, headers=HEADERS, allow_redirects=False, timeout=10)
        # ئەگەر ڕەوانەی کردیت بۆ فایلی .ipa لە ڕێگەی Location Header
        if res.status_code in [301, 302, 303, 307] and "Location" in res.headers:
            loc = res.headers["Location"]
            if ".ipa" in loc:
                return loc
        elif res.status_code == 200 and ".ipa" in res.url:
            return res.url
    except Exception as e:
        print(f"Error resolving: {e}")
    return None

def main():
    apps = []

    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            app_div = soup.find("div", {"id": "app"})
            
            if app_div and app_div.get("data-page"):
                page_data = json.loads(app_div["data-page"])
                items = page_data.get("props", {}).get("paginator", {}).get("data", [])

                for item in items:
                    name = item.get("name", "Unknown Game")
                    uuid = item.get("uuid")
                    bundle = item.get("bundle", f"com.check0ver.{re.sub(r'[^a-zA-Z0-9]', '', name).lower()}")
                    ver = item.get("version", "1.0")
                    desc = item.get("description", "")
                    icon = item.get("image", "https://check0ver.net/favicon.ico")

                    if not uuid:
                        continue

                    direct_link = get_direct_ipa(uuid)

                    # ئەگەر سێرڤەرەکە لینکی ڕاستەوخۆی نەدات بەهۆی لۆگینەوە، 
                    # لە جیاتی ئەوەی فایلەکە بەتاڵ بێت، لینکی داگرتن ڕاستەوخۆ دەخاتە ناو فایلەکە
                    final_download = direct_link if direct_link else f"https://check0ver.net/api/iapps/{uuid}/download"

                    apps.append({
                        "name": name,
                        "bundleIdentifier": bundle,
                        "developerName": "Check0ver",
                        "version": ver,
                        "versionDate": datetime.now().strftime("%Y-%m-%d"),
                        "downloadURL": final_download,
                        "localizedDescription": desc,
                        "iconURL": icon
                    })

    except Exception as e:
        print(f"General error: {e}")

    # دروستکردنی فایلی کۆتایی
    repo_structure = {
        "name": "Check0ver Games",
        "identifier": "com.check0ver.games",
        "apps": apps
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_structure, f, ensure_ascii=False, indent=2)

    print(f"تەواو بوو! {len(apps)} یاری خرانە ناو apps.json.")

if __name__ == "__main__":
    main()
