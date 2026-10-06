import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TARGET_URL = "https://check0ver.net/en/iapps?filter[inCategories][0]=9c60f563-1983-42f0-8882-a26207bd4aaf"

# کۆوکیی ئەکاونتەکەت لێرە لە ناو نێوان دوو کەوانەکە دابنێ
AUTH_COOKIE = ""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://check0ver.net/en/iapps"
}

if AUTH_COOKIE:
    HEADERS["Cookie"] = AUTH_COOKIE

def resolve_real_ipa(uuid):
    api_url = f"https://check0ver.net/api/iapps/{uuid}/download"
    try:
        # پەیوەندی بە سیستەمی داگرتن دەکرێت بۆ دەرهێنانی لینکی .ipa
        res = requests.get(api_url, headers=HEADERS, allow_redirects=False, timeout=12)
        
        # ئەگەر Redirectی کرد بۆ بەستەری ڕاستەقینە
        if res.status_code in [301, 302, 303, 307] and "Location" in res.headers:
            loc = res.headers["Location"]
            if ".ipa" in loc:
                return loc
                
        # ئەگەر ڕاستەوخۆ بەستەرەکەی گۆڕی بۆ .ipa
        res_full = requests.get(api_url, headers=HEADERS, allow_redirects=True, stream=True, timeout=12)
        final_url = res_full.url
        res_full.close()
        if ".ipa" in final_url:
            return final_url
    except Exception as e:
        print(f"Error resolving {uuid}: {e}")
    return None

def main():
    apps = []

    res = requests.get(TARGET_URL, headers=HEADERS, timeout=25)
    if res.status_code != 200:
        print("هەڵە لە وەرگرتنی لاپەڕە")
        return

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

            print(f"دەرهێنانی لینکی .ipa بۆ: {name}")
            direct_ipa = resolve_real_ipa(uuid)

            # تەنها ئەو یارییانە زیاد دەکرێن کە لینکی .ipa یان هەیە بۆ ئەوەی Feather نەوەستێت
            if direct_ipa and ".ipa" in direct_ipa:
                apps.append({
                    "name": name,
                    "bundleIdentifier": bundle,
                    "developerName": "Check0ver Games",
                    "version": ver,
                    "versionDate": datetime.now().strftime("%Y-%m-%d"),
                    "downloadURL": direct_ipa,
                    "localizedDescription": desc,
                    "iconURL": icon
                })
                print(f"سەرکەوتوو بوو: {name}")
            else:
                print(f"تێپەڕێندرا (لینکی .ipa نەدۆزرایەوە بەبێ لۆگین): {name}")

    repo_structure = {
        "name": "Check0ver Games",
        "identifier": "com.check0ver.games",
        "apps": apps
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_structure, f, ensure_ascii=False, indent=2)

    print(f"تەواو بوو! {len(apps)} بەرنامە بە بەستەری تەواوی .ipa پاشەکەوت کران.")

if __name__ == "__main__":
    main()
