import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# پەیجی ئەو بەشەی یارییەکان لە Check0ver
TARGET_URL = "https://check0ver.net/en/iapps?filter[inCategories][0]=9c60f563-1983-42f0-8882-a26207bd4aaf"
BASE_URL = "https://check0ver.net"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def resolve_direct_ipa(download_endpoint):
    """ئەم فەنکشنە بەدوای Redirect دەگەڕێت بۆ دۆزینەوەی لینکی ڕاستەقینەی .ipa"""
    try:
        # بەکارهێنانی HEAD یان GET تا لینکی کۆتایی وەربگرین
        res = requests.get(download_endpoint, headers=HEADERS, allow_redirects=True, timeout=12, stream=True)
        final_url = res.url
        # داخستنی پەیوەندی پێش ئەوەی فایلی گەورە دابەزێنێت
        res.close()
        
        if ".ipa" in final_url:
            return final_url
    except Exception as e:
        print(f"نەتوانرا بەستەری ڕاستەوخۆ دەربهێنرێت بۆ {download_endpoint}: {e}")
    return None

def extract_games():
    apps = []

    print("دەستکرا بە هێنانی داتای پەیجەکە...")
    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=25)
        if res.status_code != 200:
            print("هەڵە لە کردنەوەی پەیجەکە")
            return

        soup = BeautifulSoup(res.text, "html.parser")
        
        # دۆزینەوەی داتای JSONی ناو Inertia/Vue لەناو div#app
        app_div = soup.find("div", {"id": "app"})
        if not app_div or not app_div.get("data-page"):
            print("داتای پەیجەکە نەدۆزرایەوە!")
            return

        page_data = json.loads(app_div["data-page"])
        items = page_data.get("props", {}).get("paginator", {}).get("data", [])

        print(f"دۆزرایەوە: {len(items)} یاری لەم پەیجەدا.")

        for item in items:
            name = item.get("name", "Unknown Game")
            uuid = item.get("uuid")
            bundle = item.get("bundle") or f"com.check0ver.{re.sub(r'[^a-zA-Z0-9]', '', name).lower()}"
            version = item.get("version", "1.0")
            desc = item.get("description", "")
            icon = item.get("image", "https://check0ver.net/favicon.ico")

            if not uuid:
                continue

            download_endpoint = f"https://check0ver.net/api/iapps/{uuid}/download"
            print(f"خەریکی دەرهێنانی لینکی ڕاستەوخۆی .ipa بۆ: {name}...")

            direct_ipa_url = resolve_direct_ipa(download_endpoint)

            # ئەگەر بە سەرکەوتوویی لینکی .ipaی هێنا
            if direct_ipa_url:
                apps.append({
                    "name": name,
                    "bundleIdentifier": bundle,
                    "developerName": "Check0ver",
                    "version": version,
                    "versionDate": datetime.now().strftime("%Y-%m-%d"),
                    "downloadURL": direct_ipa_url,
                    "localizedDescription": desc,
                    "iconURL": icon,
                    "size": 0
                })
                print(f"سەرکەوتوو بوو: {name}")
            else:
                print(f"پێویستی بە لۆگین یان کۆدە: {name}")

    except Exception as e:
        print(f"کێشە لە خوێندنەوە: {e}")

    # ڕێکخستنی شێوازی فەرمیی AltStore بۆ Feather
    repo_structure = {
        "name": "Check0ver Games",
        "identifier": "com.check0ver.games",
        "apps": apps
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_structure, f, ensure_ascii=False, indent=2)

    print(f"تەواو بوو! {len(apps)} فایلی ڕاستەوخۆی .ipa پاشەکەوت کران.")

if __name__ == "__main__":
    extract_games()
