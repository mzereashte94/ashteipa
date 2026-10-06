import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TARGET_URL = "https://check0ver.net/en/iapps?filter[inCategories][0]=9c60f563-1983-42f0-8882-a26207bd4aaf"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def main():
    apps = []

    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=25)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            app_div = soup.find("div", {"id": "app"})
            
            if app_div and app_div.get("data-page"):
                page_data = json.loads(app_div["data-page"])
                items = page_data.get("props", {}).get("paginator", {}).get("data", [])

                for item in items:
                    name = item.get("name", "Unknown Game")
                    uuid = item.get("uuid")
                    bundle = item.get("bundle") or f"com.check0ver.{re.sub(r'[^a-zA-Z0-9]', '', name).lower()}"
                    ver = item.get("version", "1.0")
                    desc = item.get("description", "")
                    icon = item.get("image", "https://check0ver.net/favicon.ico")

                    if not uuid:
                        continue

                    # فێڵی بەستەر بۆ ئەوەی Feather وەک فایلی ڕاستەقینەی .ipa بیناسێتەوە و ڕانەوەستێت:
                    clean_slug = re.sub(r'[^a-zA-Z0-9]', '_', name).lower()
                    download_url = f"https://check0ver.net/api/iapps/{uuid}/download?app={clean_slug}.ipa"

                    apps.append({
                        "name": name,
                        "bundleIdentifier": bundle,
                        "developerName": "Check0ver Games",
                        "version": ver,
                        "versionDate": datetime.now().strftime("%Y-%m-%d"),
                        "downloadURL": download_url,
                        "localizedDescription": desc,
                        "iconURL": icon,
                        "size": 0
                    })

    except Exception as e:
        print(f"Error: {e}")

    repo_structure = {
        "name": "Check0ver Games",
        "identifier": "com.check0ver.games",
        "apps": apps
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_structure, f, ensure_ascii=False, indent=2)

    print(f"تەواو بوو! {len(apps)} بەرنامە بە پاشگری .ipa پاشەکەوت کران.")

if __name__ == "__main__":
    main()
