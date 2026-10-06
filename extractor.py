import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TARGET_URL = "https://check0ver.net/en/iapps"
BASE_URL = "https://check0ver.net"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def run():
    apps = []
    seen = set()

    # لیستی سەرەکی بەرنامە فەرمییەکانی Check0ver
    defaults = [
        {"name": "WhatsApp Zero", "id": "whatsappzero", "ver": "26.34.74", "desc": "Activation code required • Freeze last seen • Hide blue ticks • Hidden chats"},
        {"name": "WA Business Zero", "id": "wabusinesszero", "ver": "26.34.74", "desc": "Activation code required • WA Business Modded with Zero features"},
        {"name": "SnapZero", "id": "snapzero", "ver": "14.11.0", "desc": "Audio saving/upload • Fake streak • Screenshot bypass • Incognito mode"},
        {"name": "YouTube Zero", "id": "youtubezero", "ver": "21.22.4", "desc": "Download Videos • Background Play • No Ads • PiP • Shorts Download"},
        {"name": "TikTok Zero", "id": "tiktokzero", "ver": "45.0.0", "desc": "Save photos and videos without watermark • Save stories"},
        {"name": "Instagram Zero", "id": "instagramzero", "ver": "422.1.0", "desc": "Download media • Remove ads • Zoom profile pictures"},
        {"name": "Jodel Zero", "id": "jodelzero", "ver": "7.189", "desc": "Complete Ban Bypass • Auto unban • Multiple accounts"}
    ]

    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=25)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.find_all(["div", "article"], class_=re.compile(r'(card|item|app)', re.I))
            
            for c in cards:
                title = c.find(["h2", "h3", "h4", "h5", "strong", "a"])
                if not title:
                    continue
                name = title.get_text(strip=True)
                if not name or len(name) < 3 or name in seen or "Login" in name:
                    continue
                
                seen.add(name)
                clean_id = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
                
                apps.append({
                    "name": name,
                    "bundleIdentifier": f"com.check0ver.{clean_id}",
                    "developerName": "Check0ver",
                    "version": "1.0",
                    "versionDate": datetime.now().strftime("%Y-%m-%d"),
                    "downloadURL": "https://check0ver.net/en/iapps",
                    "localizedDescription": f"{name} - فەرمی لە Check0ver",
                    "iconURL": "https://check0ver.net/favicon.ico",
                    "size": 0
                })
    except Exception as e:
        print(f"Error scraping: {e}")

    # ئەگەر ماڵپەڕەکە ڕێگری لێکرد، ئەپە فەرمییەکان پاشەکەوت دەکات تا فایلەکە بەتاڵ نەبێت
    if len(apps) < len(defaults):
        for item in defaults:
            if item["name"] not in seen:
                apps.append({
                    "name": item["name"],
                    "bundleIdentifier": f"com.check0ver.{item['id']}",
                    "developerName": "Check0ver Zero",
                    "version": item["ver"],
                    "versionDate": datetime.now().strftime("%Y-%m-%d"),
                    "downloadURL": "https://check0ver.net/en/iapps",
                    "localizedDescription": item["desc"],
                    "iconURL": "https://check0ver.net/favicon.ico",
                    "size": 0
                })

    # ڕێکخستنی شێوازی فەرمیی AltStore بۆ Feather
    repo_data = {
        "name": "Check0ver Apps",
        "identifier": "com.check0ver.repo",
        "apps": apps
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_data, f, ensure_ascii=False, indent=2)

    print(f"Done! Saved {len(apps)} apps successfully.")

if __name__ == "__main__":
    run()
