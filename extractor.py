import json
import re
import requests
from datetime import datetime

# المصادر وواجهات API البديلة لجلب بيانات تطبيقات IPAOMTK
API_URL = "https://ipaomtk.com/api/apps"
FALLBACK_URL = "https://raw.githubusercontent.com/swaggyP36000/TrollStore-IPAs/main/apps.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*"
}

def get_apps():
    apps_list = []
    
    # المحاولة الأولى: جلب التطبيقات مباشرة من واجهة برمجة IPAOMTK
    try:
        res = requests.get(API_URL, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            raw_apps = data if isinstance(data, list) else data.get("apps", [])
            for item in raw_apps:
                d_url = item.get("downloadURL") or item.get("url") or item.get("download_url") or ""
                if not d_url:
                    continue
                name = item.get("name", "Unknown App")
                b_id = item.get("bundleIdentifier") or item.get("bundleID") or f"com.ipaomtk.{re.sub(r'[^a-zA-Z0-9]', '', name).lower()}"
                
                apps_list.append({
                    "name": name,
                    "bundleIdentifier": b_id,
                    "developerName": item.get("developerName", "IPAOMTK"),
                    "version": item.get("version", "1.0"),
                    "versionDate": item.get("versionDate", datetime.now().strftime("%Y-%m-%d")),
                    "downloadURL": d_url,
                    "localizedDescription": item.get("localizedDescription") or item.get("description") or f"{name} by IPAOMTK",
                    "iconURL": item.get("iconURL") or item.get("icon") or "https://ipaomtk.com/favicon.ico",
                    "size": item.get("size", 0)
                })
    except Exception as e:
        print(f"API Fetch failed: {e}")

    # المحاولة الثانية: إذا كانت النتيجة فارغة، جلب التطبيقات المربوطة بسيرفر file.ipaomtk.com مباشرة
    if not apps_list:
        try:
            print("Fetching from mirror database...")
            res = requests.get(FALLBACK_URL, headers=HEADERS, timeout=30)
            if res.status_code == 200:
                data = res.json()
                raw_apps = data.get("apps", [])
                for item in raw_apps:
                    d_url = item.get("downloadURL", "")
                    # تصفية التطبيقات الخاصة بـ ipaomtk أو إدراج كامل التطبيقات
                    if "ipaomtk" in d_url or "ipaomtk" in item.get("developerName", "").lower():
                        apps_list.append(item)
                    elif len(apps_list) < 200: # ضمان عدم ترك المستودع فارغاً
                        apps_list.append(item)
        except Exception as e:
            print(f"Fallback fetch failed: {e}")

    repo_structure = {
        "name": "IPAOMTK Apps",
        "identifier": "com.ipaomtk.repo",
        "apps": apps_list
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_structure, f, ensure_ascii=False, indent=2)

    print(f"Done! Successfully retrieved {len(apps_list)} apps.")

if __name__ == "__main__":
    get_apps()
