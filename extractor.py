import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# بەستەری سەرەکی بەشی یارییەکان
BASE_GAMES_URL = "https://ipaomtk.com/games/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

def extract_games():
    games_list = []
    seen_urls = set()

    # گەڕان بەناو 5 پەڕەی یەکەمی بەشی یارییەکان (دەتوانیت ژمارەکە زیاد بکەیت)
    for page in range(1, 6):
        url = BASE_GAMES_URL if page == 1 else f"{BASE_GAMES_URL}page/{page}/"
        print(f"خەریکی هێنانی یارییەکانی پەڕەی {page}ە لە: {url}")

        try:
            res = requests.get(url, headers=HEADERS, timeout=25)
            if res.status_code != 200:
                print(f"پەڕەی {page} نەکراوە یان گەیشتە کۆتایی (Status {res.status_code})")
                break

            soup = BeautifulSoup(res.text, "html.parser")

            # دۆزینەوەی هەموو کارت و بلۆکەکانی یارییەکان لە ناو پەڕەکەدا
            articles = soup.find_all(["article", "div"], class_=re.compile(r'(post|item|app|card|game)', re.I))
            if not articles:
                articles = soup.find_all("a", href=re.compile(r'ipaomtk\.com/'))

            for item in articles:
                text_content = item.get_text(separator=" ", strip=True)
                
                # دۆزینەوەی لینکی پەڕەی تایبەتی یارییەکە
                link_tag = item if item.name == 'a' else item.find("a", href=True)
                if not link_tag or not link_tag.get("href"):
                    continue

                game_page_url = link_tag['href']
                if not game_page_url.startswith("http") or game_page_url == BASE_GAMES_URL:
                    continue

                # دۆزینەوەی ئایکۆنی وێنەی یارییەکە
                img_tag = item.find("img")
                icon_url = "https://ipaomtk.com/favicon.ico"
                if img_tag:
                    icon_url = img_tag.get("data-src") or img_tag.get("src") or icon_url

                # دەرهێنانی ناوی یارییەکە
                title_tag = item.find(["h2", "h3", "h4", "span", "div"], class_=re.compile(r'title|name', re.I))
                game_name = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
                if not game_name or len(game_name) < 2 or "Download" in game_name:
                    slug = game_page_url.strip("/").split("/")[-1]
                    game_name = slug.replace("-", " ").title()

                # بەستەری ڕاستەوخۆی سێرڤەری فایلی داگرتن
                # ماڵپەڕەکە فایلەکان بەم شێوازە لەسەر file.ipaomtk.com دادەنێت
                slug_name = game_page_url.strip("/").split("/")[-1]
                download_link = f"https://file.ipaomtk.com/ipa/{slug_name}.ipa"

                if download_link in seen_urls:
                    continue
                seen_urls.add(download_link)

                bundle_id = "com.ipaomtk.game." + re.sub(r'[^a-zA-Z0-9]', '', slug_name).lower()

                games_list.append({
                    "name": game_name,
                    "bundleIdentifier": bundle_id,
                    "developerName": "IPAOMTK Games",
                    "version": "1.0",
                    "versionDate": datetime.now().strftime("%Y-%m-%d"),
                    "downloadURL": download_link,
                    "localizedDescription": f"{game_name} - لە بەشی یارییەکانی IPAOMTK",
                    "iconURL": icon_url,
                    "size": 0
                })

        except Exception as e:
            print(f"هەڵە لە پەڕەی {page}: {e}")
            continue

    # دروستکردنی فۆرماتی تایبەتی ستانداردی AltStore / Feather
    repo_data = {
        "name": "IPAOMTK Games",
        "identifier": "com.ipaomtk.games",
        "apps": games_list
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_data, f, ensure_ascii=False, indent=2)

    print(f"تەواو بوو! بە کۆی گشتی {len(games_list)} یاری بەسەرکەوتوویی خرایە ناو apps.json.")

if __name__ == "__main__":
    extract_games()
