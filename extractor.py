import os
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://file.ipaomtk.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
}

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_ipaomtk():
    apps = []
    seen_urls = set()

    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # دۆزینەوەی هەموو لینکەکان کە کۆتاییان بە .ipa دێت یان لە ناو دوگمەکانی داگرتندان
        links = soup.find_all("a", href=True)
        count = 1

        for a in links:
            href = a['href']
            # ئەگەر لینکی ڕاستەوخۆ بوو یان پاشگری .ipa بوو
            if href.endswith(".ipa") or "/download" in href or "file.ipaomtk.com" in href:
                download_url = href if href.startswith("http") else f"{BASE_URL.rstrip('/')}/{href.lstrip('/')}"
                
                if download_url in seen_urls:
                    continue
                seen_urls.add(download_url)

                name = clean_text(a.text) or f"IPA App {count}"
                # دروستکردنی Bundle ID بەپێی ناوی ئەپەکە
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', name).lower() or f"app{count}"
                bundle_id = f"com.ipaomtk.{clean_name}"

                app_entry = {
                    "name": name,
                    "bundleIdentifier": bundle_id,
                    "developerName": "IPAOMTK",
                    "version": "1.0",
                    "versionDate": datetime.now().strftime("%Y-%m-%d"),
                    "downloadURL": download_url,
                    "localizedDescription": f"{name} downloaded from IPAOMTK",
                    "iconURL": "https://ipaomtk.com/favicon.ico",
                    "size": 0
                }
                apps.append(app_entry)
                count += 1

    except Exception as e:
        print(f"Error scraping: {e}")

    # ڕێکخستنی داتاکان بە فۆرماتی AltStore
    repo_data = {
        "name": "IPAOMTK Apps",
        "identifier": "com.ipaomtk.repo",
        "apps": apps
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_data, f, ensure_ascii=False, indent=2)

    print(f"Extraction finished. Total apps saved: {len(apps)}")

if __name__ == "__main__":
    extract_ipaomtk()
